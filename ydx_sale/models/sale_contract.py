# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, SUPERUSER_ID,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from ydxaddons.ydx_base.models import tools


class SaleContract(models.Model):
    _name = 'sale.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Sale Contract"
    _order = 'date_order desc, id desc'

    READONLY_STATES = {
        'to approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()


    name = fields.Char('Contract Reference', required=True, index=True, copy=False, default='New')
    date_order = fields.Datetime('Order Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,\
        help="Depicts the date where the Quotation should be validated and converted into a sale order.")
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
    #order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    order_line = fields.One2many('sale.contract.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    sale_order_ids = fields.Many2many(
        'sale.order',
        'sale_order_contract_rel',
        'sale_contract_id', 'sale_order_id', states=READONLY_STATES,)
    sale_order_count = fields.Integer(compute="_compute_sale_order", string='Sale Order Count', copy=False, default=0, store=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    date_planned = fields.Datetime('Dlivery Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,\
        help="Dlivery Date.")
    user_id = fields.Many2one('res.users', string='Sale Representative', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    signed_address = fields.Char(readonly=False)
    voucher_moneyformat = fields.Char(string='Amount of capital')

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)
    image = fields.Binary("Image", related='company_id.stamp_image', readonly=True)
    company_legal_person = fields.Char(string='Legal Person', readonly=False)
    company_address = fields.Char(compute='_compute_company_contact_address', store=True, readonly=False)
    company_contact = fields.Many2one(comodel_name='hr.employee', string=u'委托人', states=READONLY_STATES,)
    company_phone = fields.Char(string='company_id.phone', readonly=False)
    company_vat = fields.Char(string='company_id.vat', readonly=False)
    company_bank_num = fields.Char(string='company_id.bank_num', readonly=False)
    company_bank = fields.Char(string='company_id.bank', readonly=False)
    company_street = fields.Char(related='company_id.street', store=True, readonly=False)
    company_street2 = fields.Char(related='company_id.street2', store=True, readonly=False)
    company_city = fields.Char(related='company_id.city', store=True, readonly=False)
    company_state = fields.Char(string='State', related='company_id.state_id.name', store=True, ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    company_country = fields.Char(string="Country", related='company_id.country_id.name', store=True, ondelete='restrict')
    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=_get_default_team, oldname='section_id')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, states=READONLY_STATES, change_default=True, track_visibility='always', help="You can find a customers by its Name, TIN, Email or Internal Reference.")
    partner_legal_person = fields.Char(string='Legal Person')
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
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.contract') or '/'
        return super(SaleContract, self).create(vals)

    @api.multi
    def button_confirm(self):
        sale_contract_approval = self.env['ir.config_parameter'].sudo().get_param('sale.sale_contract_approval')
        for order in self:
            if order.state not in ['draft']:
                continue
            if sale_contract_approval:
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
                raise UserError(_('Cannot delete a sale order line which is in state \'%s\'.') % (pco.state,))
        return super(SaleContract, self).unlink()

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
            'sale_line_id': line.id,
            'product_uom': line.product_uom.id,
            'product_id': line.product_id.id,
            'price_unit': line.order_id.currency_id._convert(
                line.price_unit, self.currency_id, line.company_id, self.date_order or fields.Date.today(), round=False),
            'product_uom_qty': line.product_uom_qty,
            'tax_id': line.tax_id
        }
        return data

    @api.onchange("sale_order_ids")
    def _aoto_complete(self):
        sale_orders = self.env['sale.order'].search([('id','in', [po.id for po in self.sale_order_ids])])
        new_lines = self.env['sale.contract.line']
        if  len(sale_orders) > 0:
            customer = sale_orders[-1].partner_id
            self.partner_id = customer.id
            self.user_id = sale_orders[-1].user_id
            self.team_id = sale_orders[-1].team_id
            # if len(customer.child_ids) > 0:
            #     self.partner_contact = customer.child_ids

        for porder in sale_orders:
            for line in porder.order_line:
                if line.is_downpayment:
                    continue
                flag = 0
                for nl in new_lines:
                    if nl.product_id.id == line.product_id.id:
                        nl.product_uom_qty += line.product_uom_qty
                        flag = 1
                        break

                if flag == 0:
                    data = self._prepare_contact_line_from_po_line(line)
                    new_line = new_lines.new(data)
                    new_lines += new_line

        self.order_line = new_lines
        self.env.context = dict(self.env.context, from_sale_contract_change=True)


class SaleContractLine(models.Model):
    _name = 'sale.contract.line'
    _description = 'Sale Contract Line'
    _order = 'order_id, sequence, id'

    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    order_id = fields.Many2one('sale.contract', string='Order Reference', index=True, required=True, ondelete='cascade')
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, required=True)
    product_name = fields.Char(related='product_id.name', store=True, readonly=False)
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(string='Price Unit', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True, readonly=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    state = fields.Selection(related='order_id.state', store=True, readonly=False)
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete='set null', index=True)
    sale_id = fields.Many2one('sale.order', related='sale_line_id.order_id', string='Sale Order', store=False, readonly=True, related_sudo=False,
        help='Associated Sale Order. Filled in automatically when a SO is chosen on the contract.')
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string='Product attribute values that do not create variants')
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id', string='User entered custom product attribute values')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.model
    def create(self, values):
        line = super(SaleContractLine, self).create(values)
        if line.order_id.state == 'to approve':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.order_id.message_post(body=msg)
        return line

    @api.multi
    def unlink(self):
        for line in self:
            if line.order_id.state in ['to approve', 'done']:
                raise UserError(_('Cannot delete a sale order line which is in state \'%s\'.') % (line.order_id.state,))
        return super(SaleContractLine, self).unlink()

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id) if fpos else taxes

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = self.get_sale_order_line_multiline_description_sale(product)

        vals.update(name=name)

        self._compute_tax_id()

        vals['price_unit'] = self.product_id.list_price
        self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position'))
        self.price_unit = self.product_id.list_price


    def get_sale_order_line_multiline_description_sale(self, product):
        """ Compute a default multiline description for this sales order line.
        This method exists so it can be overridden in other modules to change how the default name is computed.
        In general only the product is used to compute the name, and this method would not be necessary (we could directly override the method in product).
        BUT in event_sale we need to know specifically the sales order line as well as the product to generate the name:
            the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return product.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        See note about `product_no_variant_attribute_value_ids` above the field
        definition: this method is not reliable to recompute the description at
        a later time, it should only be used initially.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        product_attribute_with_is_custom = self.product_custom_attribute_value_ids.mapped('attribute_value_id.attribute_id')

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate)
        for no_variant_attribute_value in self.product_no_variant_attribute_value_ids.filtered(
            lambda ptav: ptav.attribute_id not in product_attribute_with_is_custom
        ):
            name += "\n" + no_variant_attribute_value.attribute_id.name + ': ' + no_variant_attribute_value.name

        # display the is_custom values
        for pacv in self.product_custom_attribute_value_ids:
            name += "\n" + pacv.attribute_value_id.attribute_id.name + \
                ': ' + pacv.attribute_value_id.name + \
                ': ' + (pacv.custom_value or '').strip()

        return name


