# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PurchaseSubSaleOrder(models.Model):
    _name = "purchase.sub.sale.order"
    _description = "Purchase Sub Sale Order"
    _order = 'date_order desc, id desc'

    _sql_constraints = [ ('check_uniq_name', 'unique(name)', '子订单编号已存在！')   ]
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    name = fields.Char(string='Order Reference', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    create_date = fields.Datetime(string='Creation Date', readonly=True, index=True, help="Date on which sales order is created.")
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    cabinet = fields.Char(string='Cabinet')
    flat_door = fields.Char(string='Flat open the door')
    sliding_door = fields.Char(string='Sliding door')
    glass_door = fields.Char(string='Glass door')
    swim_door = fields.Char(string='Swin door')
    package_num = fields.Integer(string='Package Number', copy=False, default=0, required=True)
    outsource_package_num = fields.Integer(string='Outsource Package Number', copy=False, default=0, required=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
