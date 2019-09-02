# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class YdxPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_contract_ids = fields.Many2many('purchase.procurement.contract', compute="_compute_contract", string='Purchase Contract', copy=False, store=True)
    purchase_contract_count = fields.Integer(compute="_compute_contract", string='Purchase Contract Count', copy=False, default=0, store=True)
    purchase_return_ids = fields.Many2many('purchase.return', compute="_compute_return", string='Purchase Return Order', copy=False, store=True)
    purchase_return_count = fields.Integer(compute="_compute_return", string='Purchase Return Count', copy=False, default=0, store=True)

    @api.multi
    def action_create_procurement_contract(self):
        action = self.env.ref('ydx_purchase.procurement_contract_management_view')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        res = self.env.ref('ydx_purchase.procurement_contract_management_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        context = {}
        ids = []
        for porder in self:
            ids += porder.ids
        context.update(active_model=self.env['purchase.procurement.contract'],
                       default_purchase_order_ids=ids
                       )
        result['context'] = context
        if not no_create:
                result['res_id'] = self.purchase_contract_ids.id or False
        return result

    @api.multi
    def action_view_contract(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('ydx_purchase.procurement_contract_management_view')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.purchase_contract_ids) > 1 and not no_create:
            result['domain'] = "[('id', 'in', " + str(self.purchase_contract_ids.ids) + ")]"
        else:
            res = self.env.ref('ydx_purchase.procurement_contract_management_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not no_create:
                result['res_id'] = self.purchase_contract_ids.id or False

        return result

    @api.multi
    def action_create_return(self):
        action = self.env.ref('ydx_purchase.purchase_return_form_action')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        res = self.env.ref('ydx_purchase.purchase_return_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        context = {}
        ids = []
        for porder in self:
            ids += porder.ids
        context.update(active_model=self.env['purchase.return'],
                       default_purchase_order_ids=ids,
                       default_partner_id=self.partner_id.id,
                       )
        result['context'] = context
        if not no_create:
                result['res_id'] = self.purchase_return_ids.id or False
        return result

    @api.multi
    def action_view_return(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('ydx_purchase.purchase_return_form_action')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.purchase_return_ids) > 1 and not no_create:
            result['domain'] = "[('id', 'in', " + str(self.purchase_return_ids.ids) + ")]"
        else:
            res = self.env.ref('ydx_purchase.purchase_return_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not no_create:
                result['res_id'] = self.purchase_return_ids.id or False

        return result

    @api.multi
    def action_contract_wizard(self):
        action = self.env.ref('ydx_purchase.action_wizard_procurement_contract')
        result = action.read()[0]
        res = self.env.ref('ydx_purchase.procurement_contract_wizard_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result

    @api.depends('order_line.contract_lines.order_id')
    def _compute_contract(self):
        for order in self:
            contracts = self.env['purchase.procurement.contract']
            for line in order.order_line:
                contracts |= line.contract_lines.mapped('order_id')
            order.purchase_contract_ids = contracts
            order.purchase_contract_count = len(contracts)

    @api.depends('order_line.return_lines.purchase_return_id')
    def _compute_return(self):
        for order in self:
            return_order = self.env['purchase.return']
            for line in order.order_line:
                return_order |= line.return_lines.mapped('purchase_return_id')
            order.purchase_return_ids = return_order
            order.purchase_return_count = len(return_order)


class YdxPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    contract_lines = fields.One2many('purchase.procurement.contract.line', 'purchase_line_id', string="Contract Lines", readonly=True, copy=False)
    return_lines = fields.One2many('purchase.return.lines', 'purchase_line_id', string="Return Lines", readonly=True, copy=False)
