# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ResOutsource(models.Model):
    _name = 'res.outsource'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Outsource"
    _order = 'id desc'

    name = fields.Text(string='Index', required=True, index=True, copy=False, default='New')
    sequence = fields.Integer(string='Sequence', default=10)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_speci_type= fields.Char(string='Specification')
    cabinet_no = fields.Char(string='Cabinet Number')
    color = fields.Char(string='Color')
    product_height = fields.Float(string='Product Height', default=0.0)
    product_width = fields.Float(string='Product Width', default=0.0)
    product_thick = fields.Float(string='Product Thick', default=0.0)
    product_opento = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right')
    ], string="Product Opento")
    note = fields.Text('Description')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('res.connection.metal') or '/'
        return super(ResOutsource, self).create(vals)


