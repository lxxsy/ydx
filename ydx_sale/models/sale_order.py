# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv import expression
from functools import partial
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _sql_constraints = [ ('check_uniq_sale_order', 'unique(sale_order_no)', '订单编号已存在！')   ]
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
    sub_sale_order_ids = fields.One2many('sub.sale.order', 'order_id', string='Sub Sale Orders', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    connection_metal_line = fields.One2many('res.connection.metal', 'order_id', string='Connection Metal Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    function_metal_line = fields.One2many('res.function.metal', 'order_id', string='Function Metal Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    outsource_line = fields.One2many('res.outsource', 'order_id', string='Outsource Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    production_part_line = fields.One2many('res.production.part', 'order_id', string='Production Part Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

    sale_order_no = fields.Char(string='Sale Order No.', required=True)
    factory_order_no = fields.Char(string='Factory Order No.', required=True)
    upload_sale_date = fields.Datetime(string='Upload Sale Date')
    quotations_date = fields.Datetime(string='Quotations Date')
    pay_date = fields.Datetime(string='Pay Date')
    confirm_date = fields.Datetime(string='Confirm Date')
    install_address = fields.Char(string='Install Address', required=True)
    phone = fields.Char(string='Phone', required=True)
    is_install = fields.Boolean(default=False)
    designer = fields.Char(string='Designer', required=True)
    spliter = fields.Many2one('res.users', string='Spliter', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)

    sub_sale_amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_sub_sale_amount_all', track_visibility='onchange', track_sequence=5)
    sub_sale_amount_by_group = fields.Binary(string="Tax amount by group", compute='_sub_sale_amount_by_group', help="type: [(name, amount, base, formated amount, formated base)]")
    sub_sale_amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_sub_sale_amount_all')
    sub_sale_amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_sub_sale_amount_all', track_visibility='always', track_sequence=6)
    material_use = fields.Float(compute='_sub_sale_amount_all', string='Material Use', default=0.0, copy=False, store=True)

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
            data = self._get_sub_sale_order_values(sub_order_id)
            self.env['stock.sub.sale.order'].sudo().create(data)

    def _get_stock_production_part(self, production_part_line):
        move_values = {
            'product_id': production_part_line.product_id.id,
            'product_uom_qty': production_part_line.product_uom_qty,
            'product_uom': production_part_line.product_uom,
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
                'material_use':material_use_tmp
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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_lines = fields.One2many('sale.contract.line', 'sale_line_id', string="Contract Lines", readonly=True, copy=False)
    return_lines = fields.One2many('sale.return.line', 'sale_line_id', string="Return Lines", readonly=True, copy=False)


