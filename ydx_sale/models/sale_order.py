# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv import expression
from functools import partial
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _sql_constraints = [ ('check_uniq_sale_order', 'unique(name)', '订单编号已存在！')   ]
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
    sub_sale_order_ids = fields.One2many('sub.sale.order', 'order_id', string='Sub Sale Orders', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)
    connection_metal_line = fields.One2many('res.connection.metal', 'order_id', string='Connection Metal Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)
    function_metal_line = fields.One2many('res.function.metal', 'order_id', string='Function Metal Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)
    outsource_line = fields.One2many('res.outsource', 'order_id', string='Outsource Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)
    production_part_line = fields.One2many('res.production.part', 'order_id', string='Production Part Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)

    factory_order_no = fields.One2many('sale.factory.no', 'order_id', string='Sale Factory No', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False)
    is_replenishment = fields.Boolean(default=False,string=_("补单"))
    upload_sale_date = fields.Datetime(string='Upload Sale Date')
    quotations_date = fields.Datetime(string='Quotations Date')
    pay_date = fields.Datetime(string='Pay Date', compute="_get_invoiced")
    confirm_date = fields.Datetime(string='Confirm Date')
    install_address = fields.Char(string='Install Address', required=True)
    phone = fields.Char(string='Phone', required=True)
    is_install = fields.Boolean(default=False)
    # designer = fields.Char(string='Designer', required=True)
    designer = fields.Many2one('sale.designer', string='Designer', required=True)
    spliter = fields.Many2one('res.users', string='Spliter', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)

    sub_sale_amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_sub_sale_amount_all', track_visibility='onchange', track_sequence=5)
    sub_sale_amount_by_group = fields.Binary(string="Tax amount by group", compute='_sub_sale_amount_by_group', help="type: [(name, amount, base, formated amount, formated base)]")
    sub_sale_amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_sub_sale_amount_all')
    sub_sale_amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_sub_sale_amount_all', track_visibility='always', track_sequence=6)
    material_use = fields.Float(compute='_sub_sale_amount_all', string='Material Use', default=0.0, copy=False, store=True)
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='附件上传')
    express_info = fields.Char(string='物流快递', compute='_compute_picking_express')

    @api.onchange('partner_id')
    def onchange_partner_id_phone_address(self):
        """
        Update the following fields when the partner is changed:
        - phone
		- install_address
        """
        if not self.partner_id:
            self.update({
                'phone': False,
                'install_address': False
            })
            return

        phone = self.partner_id.phone
        #判断国家、城市、街道等字段是否为空，为空则不拼接
        install_address = ""

        if self.partner_id.country_id.name:
            install_address += self.partner_id.country_id.name
        if self.partner_id.state_id.name:
            install_address += self.partner_id.state_id.name
        if self.partner_id.city:
            install_address += self.partner_id.city
        # if self.partner_id.zip:
        #     install_address += self.partner_id.zip
        if self.partner_id.street:
            install_address += self.partner_id.street
        if self.partner_id.street2:
            install_address += self.partner_id.street2
        values = {
            'phone': phone,
            'install_address': install_address,
        }
        self.update(values)


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
                if order.sub_sale_amount_total < float(so_double_validation_amount):
                    order.action_confirm()
                else:
                    order.state = 'to approve'
            else:
                order.action_confirm()
            # if order.is_replenishment == False:
            #     if not order.factory_order_no:
            #         self.env['sale.factory.no'].create({
            #             "order_id": order.id
            #         })
        return True

    def _get_sub_sale_order_values(self, sub_sale_order):
        move_values = {
            'name': sub_sale_order.name,
            'product_id': sub_sale_order.product_id.id,
            'cabinet': sub_sale_order.cabinet,
            'flat_door': sub_sale_order.flat_door,
            'sliding_door': sub_sale_order.sliding_door,
            'glass_door': sub_sale_order.glass_door,
            'swim_door': sub_sale_order.swim_door,
            'picking_id': self.picking_ids.id,
            'sale_order_id':sub_sale_order.order_id.id,
            'sub_sale_order_id':sub_sale_order.id
        }
        return move_values

    def _create_stock_sub_sale_order(self, sub_order_ids):
        for sub_order_id in sub_order_ids:
            if sub_order_id.is_downpayment:
                continue
            data = self._get_sub_sale_order_values(sub_order_id)
            self.env['stock.sub.sale.order'].sudo().create(data)

    def _get_stock_production_part(self, production_part_line):
        move_values = {
            'product_name': production_part_line.product_name,
            'product_uom_qty': production_part_line.product_uom_qty,
            'product_uom': production_part_line.product_uom.id,
            'product_speci_type': production_part_line.product_speci_type,
            'cabinet_no': production_part_line.cabinet_no,
            'product_color': production_part_line.product_color,
            'product_material': production_part_line.product_material,
            'product_length': production_part_line.product_length,
            'product_width': production_part_line.product_width,
            'product_thick': production_part_line.product_thick,
            'material_use': production_part_line.material_use,
            'material_open_length': production_part_line.material_open_length,
            'material_open_width': production_part_line.material_open_width,
            'band_side': production_part_line.band_side,
            'barcode': production_part_line.barcode,
            'note': production_part_line.note,
            'picking_id': self.picking_ids.id,
        }
        return move_values

    def _create_stock_production_part(self, production_part_line):
        for line in production_part_line:
            data = self._get_stock_production_part(line)
            self.env['stock.production.part'].sudo().create(data)

    @api.multi
    def action_delivery_confirm(self):
        for order in self:
            order.connection_metal_line._action_launch_stock_rule()
            order.function_metal_line._action_launch_stock_rule()
            order.outsource_line._action_launch_stock_rule()
            self._create_stock_sub_sale_order(order.sub_sale_order_ids)
            self._create_stock_production_part(order.production_part_line)


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

    @api.depends('state', 'sub_sale_order_ids.invoice_status', 'sub_sale_order_ids.invoice_lines')
    def _get_invoiced(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.

        The invoice_ids are obtained thanks to the invoice lines of the SO lines, and we also search
        for possible refunds created directly from existing invoices. This is necessary since such a
        refund is not directly linked to the SO.
        """
        # Ignore the status of the deposit product
        deposit_product_id = self.env['sale.advance.payment.inv']._default_product_id()
        line_invoice_status_all = [(d['order_id'][0], d['invoice_status']) for d in
                                   self.env['sub.sale.order'].read_group(
                                       [('order_id', 'in', self.ids), ('product_id', '!=', deposit_product_id.id)],
                                       ['order_id', 'invoice_status'], ['order_id', 'invoice_status'], lazy=False)]
        for order in self:
            invoice_ids = order.sub_sale_order_ids.mapped('invoice_lines').mapped('invoice_id').filtered(
                lambda r: r.type in ['out_invoice', 'out_refund'])
            # Search for invoices which have been 'cancelled' (filter_refund = 'modify' in
            # 'account.invoice.refund')
            # use like as origin may contains multiple references (e.g. 'SO01, SO02')
            refunds = invoice_ids.search([('origin', 'like', order.name), ('company_id', '=', order.company_id.id),
                                          ('type', 'in', ('out_invoice', 'out_refund'))])
            invoice_ids |= refunds.filtered(lambda r: order.name in [origin.strip() for origin in r.origin.split(',')])
            # Search for refunds as well
            domain_inv = expression.OR([
                ['&', ('origin', '=', inv.number), ('journal_id', '=', inv.journal_id.id)]
                for inv in invoice_ids if inv.number
            ])
            if domain_inv:
                refund_ids = self.env['account.invoice'].search(expression.AND([
                    ['&', ('type', '=', 'out_refund'), ('origin', '!=', False)],
                    domain_inv
                ]))
            else:
                refund_ids = self.env['account.invoice'].browse()

            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]

            if order.state not in ('sale', 'done'):
                invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
            elif all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
            elif all(invoice_status in ['invoiced', 'upselling'] for invoice_status in line_invoice_status):
                invoice_status = 'upselling'
            else:
                invoice_status = 'no'

            order.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
                'invoice_status': invoice_status
            })
            if len(set(invoice_ids.ids + refund_ids.ids)) == 1:
                order.update({
                    'pay_date': fields.Datetime.now(),
                })



    def _force_lines_to_invoice_policy_order(self):
        for line in self.sub_sale_order_ids:
            if self.state in ['sale', 'done']:
                line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('sub_sale_order_ids','sub_sale_order_ids.price_total', 'sub_sale_order_ids.material_use')
    def _sub_sale_amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            sub_sale_amount_untaxed = sub_sale_amount_tax = 0.0
            material_use_tmp = 0.0
            for line in order.sub_sale_order_ids:
                sub_sale_amount_untaxed += line.price_subtotal
                sub_sale_amount_tax += line.price_tax
                material_use_tmp += line.material_use
            order.update({
                'sub_sale_amount_untaxed': sub_sale_amount_untaxed,
                'sub_sale_amount_tax': sub_sale_amount_tax,
                'sub_sale_amount_total': sub_sale_amount_untaxed + sub_sale_amount_tax,
                'material_use':material_use_tmp,
            })

    def _sub_sale_amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.sub_sale_order_ids:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        # Keep track of the sequences of the lines
        # To keep lines under their section
        inv_line_sequence = 0
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            # sequence is the natural order of order_lines
            for line in order.sub_sale_order_ids:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        section_invoice = pending_section.invoice_line_create_vals(
                            invoices[group_key].id,
                            pending_section.qty_to_invoice
                        )
                        inv_line_sequence += 1
                        section_invoice[0]['sequence'] = inv_line_sequence
                        line_vals_list.extend(section_invoice)
                        pending_section = None

                    inv_line_sequence += 1
                    inv_line = line.invoice_line_create_vals(
                        invoices[group_key].id, line.qty_to_invoice
                    )
                    inv_line[0]['sequence'] = inv_line_sequence
                    line_vals_list.extend(inv_line)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env['account.invoice.line'].create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            # Idem for partner
            so_payment_term_id = invoice.payment_term_id.id
            fp_invoice = invoice.fiscal_position_id
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = fp_invoice
            # To keep the payment terms set on the SO
            invoice.payment_term_id = so_payment_term_id
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

    @api.multi
    def _compute_attachment_number(self):
        """附件上传"""
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_field', '=', self.name)], ['res_field'], ['res_field'])
        attachment = dict((data['res_field'], data['res_field_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.name, 0)

    @api.multi
    def action_get_attachment_view(self):
        """附件上传动作视图"""
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_field', '=', self.name)]
        res['context'] = {'default_res_field': self.name}
        return res

    @api.depends('picking_ids.express_info')
    def _compute_picking_express(self):
        for order in self:
            express = ''
            for pick in order.picking_ids:
                if pick.express_info:
                    express += pick.express_info
            order.express_info = express

# class AccountPayment(models.Model):
#     _inherit = "account.payment"
#
#     def action_validate_invoice_payment(self):
#         super(AccountPayment, self).action_validate_invoice_payment()
#         name = self.invoice_ids.origin
#         order = self.env['sale.order'].search([('name', '=', name)])
#         if order.is_replenishment == False:
#             if not order.factory_order_no:
#                 order.env['sale.factory.no'].create({
#                     "order_id": order.id
#                 })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_lines = fields.One2many('sale.contract.line', 'sale_line_id', string="Contract Lines", readonly=True, copy=False)
    return_lines = fields.One2many('sale.return.line', 'sale_line_id', string="Return Lines", readonly=True, copy=False)


