# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, SUPERUSER_ID,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from ydxaddons.ydx_base.models import tools


class ProcurementContract(models.Model):
    _name = 'purchase.procurement.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Procurement Contract"
    _order = 'date_order desc, id desc'

    READONLY_STATES = {
        'to approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    def _compute_purchase_order(self):
        return len(self.purchase_order_ids)

    name = fields.Char('Contract Reference', required=True, index=True, copy=False, default='New')
    date_order = fields.Datetime('Order Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,\
        help="Depicts the date where the Quotation should be validated and converted into a purchase order.")
    date_approve = fields.Date('Approval Date', readonly=1, index=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to approve', 'To Approve'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,
        default=lambda self: self.env.user.company_id.currency_id.id)
    #order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    order_line = fields.One2many('purchase.procurement.contract.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        'purchase_order_procurement_contract_rel',
        'purchase_procurement_contract_id', 'purchase_order_id', states=READONLY_STATES,)
    purchase_order_count = fields.Integer(compute="_compute_purchase_order", string='Purchase Count', copy=False, default=0, store=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    date_planned = fields.Datetime('Dlivery Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,\
        help="Dlivery Date")
    user_id = fields.Many2one('res.users', string='Purchase Representative', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    signed_address = fields.Char(readonly=False)
    voucher_moneyformat = fields.Char(string='总计大写')

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)
    image = fields.Binary("Image", related='company_id.stamp_image', readonly=True)
    company_legal_person = fields.Char(string='Legal Person', readonly=False)
    company_address = fields.Char(compute='_compute_company_contact_address', store=True, readonly=False)
    company_contact = fields.Many2one(comodel_name='hr.employee', string='Contacts', states=READONLY_STATES,)
    company_phone = fields.Char(string='company_id.phone', readonly=False)
    company_vat = fields.Char(string='company_id.vat', readonly=False)
    company_bank_num = fields.Char(string='company_id.bank_num', readonly=False)
    company_bank = fields.Char(string='company_id.bank', readonly=False)
    company_street = fields.Char(related='company_id.street', store=True, readonly=False)
    company_street2 = fields.Char(related='company_id.street2', store=True, readonly=False)
    company_city = fields.Char(related='company_id.city', store=True, readonly=False)
    company_state = fields.Char(string='State', related='company_id.state_id.name', store=True, ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    company_country = fields.Char(string="Country", related='company_id.country_id.name', store=True, ondelete='restrict')

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, track_visibility='always', help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    partner_legal_person = fields.Char(string='Legal Person', readonly=False)
    partner_address = fields.Char(compute='_compute_partner_contact_address', store=True, readonly=False)
    partner_contact = fields.Char(string='Contacts')  # force "active_test" domain to bypass _search() override
    partner_phone = fields.Char(string='partner_phone', readonly=False)
    partner_vat = fields.Char(string='partner_id.vat', readonly=False)
    partner_bank_num = fields.Char(string='partner_bank_num', readonly=False)
    partner_bank = fields.Char(string='partner_bank', readonly=False)
    partner_street = fields.Char(related='partner_id.street', store=True, readonly=False)
    partner_street2 = fields.Char(related='partner_id.street2', store=True, readonly=False)
    partner_city = fields.Char(related='partner_id.city', store=True, readonly=False)
    partner_state = fields.Char(related='partner_id.state_id.name', store=True, string='State', readonly=False)
    partner_country = fields.Char(related='partner_id.country_id.name', store=True, string="Country", readonly=False)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.procurement.contract') or '/'
        return super(ProcurementContract, self).create(vals)

    @api.multi
    def button_confirm(self):
        purchase_contract_approval = self.env['ir.config_parameter'].sudo().get_param('purchase.purchase_contract_approval')
        for order in self:
            if order.state not in ['draft']:
                continue
            if purchase_contract_approval:
                order.state = 'to approve'
            else:
                order.state = 'done'
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    @api.multi
    def button_approve(self):
        self.write({'state': 'done'})
        return {}

    @api.multi
    def unlink(self):
        for pco in self:
            if pco.state in ['to approve', 'done']:
                raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (pco.state,))
        return super(ProcurementContract, self).unlink()

    @api.multi
    def _display_company_address(self):
        args = {
            'state_name': self.company_state or '',
            'country_name': self.company_country or '',
            'city': self.company_city or '',
            'street': self.company_street or '',
            'street2': self.company_street2 or '',
        }
        return "%(country_name)s%(state_name)s%(city)s%(street)s%(street2)s" % args

    def _compute_company_contact_address(self):
        for contract in self:
            contract.company_address = contract._display_company_address()

    @api.onchange('company_id')
    def _company_info_autoadd(self):
        for contract in self:
            contract.company_phone = self.company_id.phone
            contract.company_vat = self.company_id.vat
            contract.company_bank_num = self.company_id.bank_num
            contract.company_bank = self.company_id.bank
            contract.company_legal_person = self.company_id.legal_person
            contract.company_address = contract._display_company_address()
            contract.signed_address = contract._display_company_address()
            contract.company_contact = self.env.user.id

    @api.multi
    def _display_partner_address(self):
        args = {
            'state_name': self.partner_state or '',
            'country_name': self.partner_country or '',
            'city': self.partner_city or '',
            'street': self.partner_street or '',
            'street2': self.partner_street2 or '',
        }
        return "%(country_name)s%(state_name)s%(city)s%(street)s%(street2)s" % args

    def _compute_partner_contact_address(self):
        for contract in self:
            contract.partner_address = contract._display_partner_address()

    @api.onchange('partner_id')
    def _partner_info_autoadd(self):
        for contract in self:
            contract.partner_phone = self.partner_id.phone
            contract.partner_vat = self.partner_id.vat
            contract.partner_bank_num = self.partner_id.bank_num
            contract.partner_bank = self.partner_id.bank
            contract.partner_legal_person = self.partner_id.legal_person
            contract.partner_address = contract._display_partner_address()

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'voucher_moneyformat': tools.Num2MoneyFormat(self, amount_untaxed + amount_tax),
            })

    def _prepare_contact_line_from_po_line(self, line):
        data = {
            'purchase_line_id': line.id,
            'product_uom': line.product_uom.id,
            'product_id': line.product_id.id,
            'price_unit': line.order_id.currency_id._convert(
                line.price_unit, self.currency_id, line.company_id, self.date_order or fields.Date.today(), round=False),
            'product_qty': line.product_qty,
            'taxes_id': line.taxes_id
        }
        return data

    @api.onchange("purchase_order_ids")
    def _aoto_complete(self):
        purchase_orders = self.env['purchase.order'].search([('id','in', [po.id for po in self.purchase_order_ids])])
        new_lines = self.env['purchase.procurement.contract.line']
        if  len(purchase_orders) > 0:
            vendor = purchase_orders[-1].partner_id
            self.partner_id = vendor.id

        for porder in purchase_orders:
            for line in porder.order_line:
                flag = 0
                for nl in new_lines:
                    if nl.product_id.id == line.product_id.id:
                        nl.product_qty += line.product_qty
                        flag = 1
                        break

                if flag == 0:
                    data = self._prepare_contact_line_from_po_line(line)
                    new_line = new_lines.new(data)
                    new_lines += new_line

        self.order_line = new_lines
        self.env.context = dict(self.env.context, from_purchase_procurement_contract_change=True)


class ProcurementContractLine(models.Model):
    _name = 'purchase.procurement.contract.line'
    _description = 'Procurement Contract Line'
    _order = 'order_id, sequence, id'

    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    order_id = fields.Many2one('purchase.procurement.contract', string='Order Reference', index=True, required=True, ondelete='cascade')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    product_name = fields.Char(related='product_id.name', store=True, readonly=False)
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(string='单价', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True, readonly=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    state = fields.Selection(related='order_id.state', store=True, readonly=False)
    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', ondelete='set null', index=True)
    purchase_id = fields.Many2one('purchase.order', related='purchase_line_id.order_id', string='Purchase Order', store=False, readonly=True, related_sudo=False,
        help='Associated Purchase Order. Filled in automatically when a PO is chosen on the vendor bill.')

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    @api.multi
    @api.depends('product_uom', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id.uom_id != line.product_uom:
                line.product_uom_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
            else:
                line.product_uom_qty = line.product_qty

    @api.model
    def create(self, values):
        line = super(ProcurementContractLine, self).create(values)
        if line.order_id.state == 'to approve':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.order_id.message_post(body=msg)
        return line

    @api.multi
    def unlink(self):
        for line in self:
            if line.order_id.state in ['to approve', 'done']:
                raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.order_id.state,))
        return super(ProcurementContractLine, self).unlink()

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result

    @api.onchange('product_id')
    def onchange_product_id_warning(self):
        if not self.product_id:
            return
        warning = {}
        title = False
        message = False

        product_info = self.product_id

        if product_info.purchase_line_warn != 'no-message':
            title = _("Warning for %s") % product_info.name
            message = product_info.purchase_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product_info.purchase_line_warn == 'block':
                self.product_id = False
            return {'warning': warning}
        return {}

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if not seller:
            if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
                self.price_unit = 0.0
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit

    def _suggest_quantity(self):
        '''
        Suggest a minimal quantity based on the seller
        '''
        if not self.product_id:
            return

        seller_min_qty = self.product_id.seller_ids\
            .filtered(lambda r: r.name == self.order_id.partner_id)\
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.product_qty = seller_min_qty[0].min_qty or 1.0
            self.product_uom = seller_min_qty[0].product_uom
        else:
            self.product_qty = 1.0
