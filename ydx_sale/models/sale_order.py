# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # 元组左边是数据库存的值，右边是显示的字段
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Send'),
        ('sale', 'Sale'),
        ('to approve', 'To Approve'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ])

    sale_contract_ids = fields.Many2many('sale.contract', compute="_compute_contract", string='Sale Contract', copy=False, store=True)
    sale_contract_count = fields.Integer(compute="_compute_contract", string='Sale Contract Count', copy=False, default=0, store=True)
    sale_return_ids = fields.Many2many('sale.return', compute="_compute_return", string='Sale Return', copy=False, store=True)
    sale_return_count = fields.Integer(compute="_compute_return", string='Sale Return Count', copy=False, default=0, store=True)

    @api.multi
    def action_approve_order(self):
        for order in self:
            order.action_confirm()

    @api.multi
    def action_confirm_order(self):
        for order in self:
            so_order_approval = self.env['ir.config_parameter'].sudo().get_param('sale_approval_workflow.so_order_approval')
            so_double_validation_amount = self.env['ir.config_parameter'].sudo().get_param('sale_approval_workflow.so_double_validation_amount')

            if order.state not in ['draft', 'sent']:
                continue
            if so_order_approval:
                if order.amount_total < float(so_double_validation_amount):
                    order.action_confirm()
                else:
                    order.state = 'to approve'
            else:
                order.action_confirm()
        return True

    @api.multi
    def action_delivery_confirm(self):
        for order in self:
            order.order_line._action_launch_stock_rule()

    @api.multi
    def action_create_sale_contract(self):
        action = self.env.ref('ydx_sale.sale_contract_management_view')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        res = self.env.ref('ydx_sale.sale_contract_management_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        context = {}
        ids = []
        for porder in self:
            ids += porder.ids
        context.update(active_model=self.env['sale.contract'],
                       default_sale_order_ids=ids
                       )
        result['context'] = context
        if not no_create:
                result['res_id'] = self.sale_contract_ids.id or False
        return result

    @api.multi
    def action_create_sale_return(self):
        action = self.env.ref('ydx_sale.action_return_orders')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        res = self.env.ref('ydx_sale.view_return_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        context = {}
        ids = []
        for porder in self:
            ids += porder.ids
        context.update(active_model=self.env['sale.return'],
                       default_sale_order_ids=ids,
                       default_partner_id = self.partner_id.id,
                       )
        result['context'] = context
        if not no_create:
                result['res_id'] = self.sale_contract_ids.id or False
        return result

    @api.multi
    def action_view_contract(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('ydx_sale.sale_contract_management_view')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_sale_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.sale_contract_ids) > 1 and not no_create:
            result['domain'] = "[('id', 'in', " + str(self.sale_contract_ids.ids) + ")]"
        else:
            res = self.env.ref('ydx_sale.sale_contract_management_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not no_create:
                result['res_id'] = self.sale_contract_ids.id or False

        return result

    @api.multi
    def action_view_return(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('ydx_sale.action_return_orders')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_sale_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.sale_return_ids) > 1 and not no_create:
            result['domain'] = "[('id', 'in', " + str(self.sale_return_ids.ids) + ")]"
        else:
            res = self.env.ref('ydx_sale.view_return_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['context']['default_sale_order_ids'] = [self.id]
            result['context']['default_partner_id'] = self.partner_id.id
            # Do not set an invoice_id if we want to create a new bill.
            if not no_create:
                result['res_id'] = self.sale_return_ids.id or False

        return result

    @api.multi
    def action_contract_wizard(self):
        action = self.env.ref('ydx_sale.action_wizard_sale_contract')
        result = action.read()[0]
        res = self.env.ref('ydx_purchase.sale_contract_wizard_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result

    @api.depends('order_line.contract_lines.order_id')
    def _compute_contract(self):
        for order in self:
            contracts = self.env['sale.contract']
            for line in order.order_line:
                contracts |= line.contract_lines.mapped('order_id')
            order.sale_contract_ids = contracts
            order.sale_contract_count = len(contracts)

    @api.depends('order_line.return_lines.order_id')
    def _compute_return(self):
        for order in self:
            returns = self.env['sale.return']
            for line in order.order_line:
                returns |= line.return_lines.mapped('order_id')
            order.sale_return_ids = returns
            order.sale_return_count = len(returns)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_lines = fields.One2many('sale.contract.line', 'sale_line_id', string="Contract Lines", readonly=True, copy=False)
    return_lines = fields.One2many('sale.return.line', 'sale_line_id', string="Return Lines", readonly=True, copy=False)


