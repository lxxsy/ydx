# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_contract_ids = fields.Many2many('purchase.procurement.contract', compute="_compute_contract", string='Purchase Contract', copy=False, store=True)
    purchase_contract_count = fields.Integer(compute="_compute_contract", string='Purchase Contract Count', copy=False, default=0, store=True)
    purchase_return_ids = fields.Many2many('purchase.return', compute="_compute_return", string='Purchase Return Order', copy=False, store=True)
    purchase_return_count = fields.Integer(compute="_compute_return", string='Purchase Return Count', copy=False, default=0, store=True)
    attachment = fields.Binary(String="Attachment")
    purchase_sub_sale_line = fields.One2many('purchase.sub.sale.order', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    purchase_type = fields.Selection([('purchase',  'Purchase Order'),
                                   ('outsource',  'Outsource')], default='purchase')

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

        """
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        """
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
        """
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        """
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

    def _prepare_purchase_sub_sale_line_from_line(self, line):
        data = {
            'name': line.name,
            'product_id': line.product_id.id,
            'cabinet': line.cabinet,
            'flat_door': line.flat_door,
            'sliding_door': line.sliding_door,
            'glass_door': line.glass_door,
            'swim_door': line.swim_door,
            'package_num': line.package_num,
            'outsource_package_num': line.outsource_package_num,
            'order_id': line.order_id.id,
            'sub_sale_order_id': line.id
        }

        return data

    @api.depends('sale_order_id')
    def _compute_sub_sale_order_line(self):
        for order in self:
            new_lines = self.env['purchase.sub.sale.order']
            sub_order_lines = self.env['sub.sale.order'].sudo().search([('order_id','=', order.sale_order_id.id)])
            for line in sub_order_lines:
                data = self._prepare_purchase_sub_sale_line_from_line(line)
                new_line = new_lines.new(data)
                new_lines += new_line
            order.purchase_sub_sale_line = new_lines
            order.env.context = dict(self.env.context, from_purchase_sub_sale_order_line_change=True)

    @api.model
    def create(self, vals):
        pu = super(PurchaseOrder, self).create(vals)
        pu._compute_sub_sale_order_line()
        return pu

    def _get_stock_sub_sale_order_values(self, pick, purchase_sub_sale_line):
        move_values = []
        for sub_sale_order in purchase_sub_sale_line:
            move_value = {
                'name': sub_sale_order.name,
                'product_id': sub_sale_order.product_id.id,
                'cabinet': sub_sale_order.cabinet,
                'flat_door': sub_sale_order.flat_door,
                'sliding_door': sub_sale_order.sliding_door,
                'glass_door': sub_sale_order.glass_door,
                'swim_door': sub_sale_order.swim_door,
                'picking_id': pick.id,
                'sub_sale_order_id':sub_sale_order.sub_sale_order_id
            }
            move_values.append(move_value)
        return move_values

    @api.multi
    def _create_picking(self):
        for purchase in self:
            super(PurchaseOrder, purchase)._create_picking()
            for pick in purchase.picking_ids:
                datas = purchase._get_stock_sub_sale_order_values(pick, purchase.purchase_sub_sale_line)
                purchase.env['stock.sub.sale.order'].sudo().create(datas)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    contract_lines = fields.One2many('purchase.procurement.contract.line', 'purchase_line_id', string="Contract Lines",readonly=True, copy=False)
    return_lines = fields.One2many('purchase.return.lines', 'purchase_line_id', string="Return Lines", readonly=True,copy=False)
    cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    product_length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")
    purchase_type = fields.Selection(related='order_id.purchase_type')

    def _merge_in_existing_line(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if product_id.fuction_type == 'outsource':
            # if this is defined, this is a dropshipping line, so no
            # this is to correctly map delivered quantities to the so lines
            return False
        return super(PurchaseOrderLine, self)._merge_in_existing_line(
            product_id=product_id, product_qty=product_qty, product_uom=product_uom,
            location_id=location_id, name=name, origin=origin, values=values)
