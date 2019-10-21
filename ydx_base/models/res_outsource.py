# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ResOutsource(models.Model):
    _name = 'res.outsource'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Outsource"
    _order = 'id asc'

    name = fields.Text(string='Index', required=True, index=True, copy=False, default='New')
    sequence = fields.Integer(string='Sequence', default=10)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', string='Product', domain=[('fuction_type', '=', 'outsource')], required=True, change_default=True, ondelete='restrict')
    product_name = fields.Char(string=_("名称"))
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_speci_type= fields.Char(string='Specification')
    door_type = fields.Char(string='门型')
    material = fields.Char(string="物料材质")
    cabinet_no = fields.Char(string='Cabinet Number')
    color = fields.Char(string='Color')
    product_height = fields.Float(string='Product Height', default=0.0)
    product_width = fields.Float(string='Product Width', default=0.0)
    product_thick = fields.Float(string='Product Thick', default=0.0)
    product_opento = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('twoopen', _('对开')),
        ('upward', _('上翻')),
        ('down', _('下翻')),
        ('noopen', _('不开')),
    ], string="Product Opento")
    note = fields.Text('Description')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('res.connection.metal') or '/'
        return super(ResOutsource, self).create(vals)

    @api.multi
    @api.onchange("product_id")
    def _onchange_product(self):
        for re in self:
            re.product_uom = re.product_id.product_tmpl_id.uom_id
            re.product_speci_type = re.product_id.product_tmpl_id.ps_speci_type



