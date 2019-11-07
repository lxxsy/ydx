# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.addons import decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _order = 'name desc, id desc'
	
    purchase_contract_ids = fields.Many2many('purchase.procurement.contract', compute="_compute_contract", string='Purchase Contract', copy=False, store=True)
    purchase_contract_count = fields.Integer(compute="_compute_contract", string='Purchase Contract Count', copy=False, default=0, store=True)
    purchase_return_ids = fields.Many2many('purchase.return', compute="_compute_return", string='Purchase Return Order', copy=False, store=True)
    purchase_return_count = fields.Integer(compute="_compute_return", string='Purchase Return Count', copy=False, default=0, store=True)
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='附件上传')
    purchase_sub_sale_line = fields.One2many('purchase.sub.sale.order', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    purchase_type = fields.Selection([('purchase',  'Purchase Order'),
                                   ('outsource',  'Outsource')], default='purchase',required=True)
    receipt_state = fields.Selection([('not done',  _('未收货')),
                                   ('done',  _('已收货'))], string=_("收货状态"), default='not done',compute='_get_receipt_bill')
    bill_state = fields.Char(default=_('未付款'), string=_("付款状态"), compute='_get_receipt_bill')

    @api.depends('state', 'picking_ids.state','invoice_ids.state')
    def _get_receipt_bill(self):
        """
        若采购订单状态、收货单状态、付款单状态发生改变时触发方法
        收货状态默认为not done（未收货），若收货单状态为完成则变为done（已收货）
        付款状态默认为未付款，若付款单状态为paid（已支付），则统计付款单总计金额凭借为已付款**元。
        :return: 收货状态的key，付款单付款总计
        """
        for order in self:
            invoice_ids_amount_total = 0
            receipt_state = 'done'
            for invoice in order.invoice_ids:
                if invoice.state != 'draft' and invoice.state != 'cancel':
                    invoice_ids_amount_total = invoice.amount_total - invoice.residual
            if not order.picking_ids:
                receipt_state = 'not done'
            for pick in order.picking_ids:
                if pick.state != 'done':
                    receipt_state = 'not done'
                    break

            order.update({
                'receipt_state': receipt_state,
                'bill_state': '已付款'+str(invoice_ids_amount_total)+'元'
            })

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

    def _compute_sub_sale_order_line(self):
        for order in self:
            new_lines = self.env['purchase.sub.sale.order']
            sub_order_lines = self.env['sub.sale.order'].sudo().search([('order_id','=', order.sale_order_id.id)])
            for line in sub_order_lines:
                if line.is_downpayment:
                    continue
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
                pick.incoming_type = purchase.purchase_type
                datas = purchase._get_stock_sub_sale_order_values(pick, purchase.purchase_sub_sale_line)
                purchase.env['stock.sub.sale.order'].sudo().create(datas)

    @api.multi
    @api.depends("origin")
    def _compute_attachment_number(self):
        """附件上传"""
        sources = self.origin if self.origin else self.name
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_field', '=', sources)], ['res_field'], ['res_field'])
        attachment = dict((data['res_field'], data['res_field_count']) for data in attachment_data)
        for expense in self:
            sources_tmp = expense.origin if expense.origin else expense.name
            expense.attachment_number = attachment.get(sources_tmp, 0)

    @api.multi
    def action_get_attachment_view(self):
        """附件上传动作视图"""
        self.ensure_one()
        sources = self.origin if self.origin else self.name
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_field', '=', sources)]
        res['context'] = {'default_res_field': sources}
        return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_name = fields.Char(string=_("名称"))
    contract_lines = fields.One2many('purchase.procurement.contract.line', 'purchase_line_id', string="Contract Lines",readonly=True, copy=False)
    return_lines = fields.One2many('purchase.return.lines', 'purchase_line_id', string="Return Lines", readonly=True,copy=False)
    sub_sale_order_no = fields.Char(string="子销售订单")
    cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    product_length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")
    product_opento = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('twoopen', _('对开')),
        ('upward', _('上翻')),
        ('down', _('下翻')),
        ('noopen', _('不开')),
        ('twoopen_and_right', _('对开+右开')),
        ('twoopen_and_left', _('对开+左开')),
    ], string="Product Opento")
    purchase_type = fields.Selection(related='order_id.purchase_type')
    product_speci_type = fields.Char(string=_('规格型号'))
    discount = fields.Float(string='折扣(%)', digits=dp.get_precision('Discount'), default=0.0)

    def _merge_in_existing_line(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if product_id.fuction_type == 'outsource':
            # if this is defined, this is a dropshipping line, so no
            # this is to correctly map delivered quantities to the so lines
            return False
        return super(PurchaseOrderLine, self)._merge_in_existing_line(
            product_id=product_id, product_qty=product_qty, product_uom=product_uom,
            location_id=location_id, name=name, origin=origin, values=values)

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'cabinet_no': self.cabinet_no,
            'material': self.material,
            'product_colour': self.product_colour,
            'length': self.product_length,
            'width': self.width,
            'thickness': self.thickness,
            'band_number': self.band_number,
            'remarks': self.remarks,
            'product_opento': self.product_opento,
            'product_name': self.product_name,
            'product_speci_type': self.product_speci_type,
            'sub_sale_order_no': self.sub_sale_order_no,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            # Always call '_compute_quantity' to round the diff_quantity. Indeed, the PO quantity
            # is not rounded automatically following the UoM.
            if get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = self.product_uom._compute_quantity(diff_quantity, self.product_uom, rounding_method='HALF-UP')
            res.append(template)
        return res
    
    @api.model
    def create(self, values):
        if not values.get("name"):
            values["name"] = values.get("product_id")
        return super(PurchaseOrderLine, self).create(values)
    
    @api.multi
    def write(self, values):
        if "name" in values:
            for value in values:
                 if not values.get("name"):
                    value["name"] = value.get("product_id")
        return super(PurchaseOrderLine, self).write(values)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()

        if self.product_id:
            self.product_speci_type = self.product_id.product_tmpl_id.ps_speci_type

        return res

    @api.depends('product_qty', 'discount', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                price,
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
