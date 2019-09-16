# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ResFunctionMetal(models.Model):
    _name = 'res.function.metal'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Function Metal"
    _order = 'id desc'

    name = fields.Text(string='Index', required=True, index=True, copy=False, default='New')
    sequence = fields.Integer(string='Sequence', default=10)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)

    product_id = fields.Many2one('product.product', string='Product', domain=[('fuction_type', '=', 'fmetals')], change_default=True, ondelete='restrict')
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    note = fields.Text('Description')
    product_speci_type= fields.Char(string='Specification')
    cabinet_no = fields.Char(string='Cabinet Number')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('res.connection.metal') or '/'
        return super(ResFunctionMetal, self).create(vals)

    @api.multi
    @api.onchange("product_id")
    def _onchange_product(self):
        for re in self:
            re.product_uom = re.product_id.product_tmpl_id.uom_id
            re.product_speci_type = re.product_id.product_tmpl_id.ps_speci_type


