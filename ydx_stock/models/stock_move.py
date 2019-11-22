# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class StockMove(models.Model):
    _inherit = "stock.move"

    product_name = fields.Char(string=_("名称"))
    product_function_type = fields.Selection(related='product_id.fuction_type', readonly=True)
    sub_sale_order_no = fields.Char(string="子销售订单")
    cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")
    product_speci_type = fields.Char(string=_("规格型号"))
    order_number = fields.Char(strint="Order number")
    the_child_orders = fields.Char(int="The child orders")
    base_material = fields.Char(string="Base material")
    plane_materiel = fields.Char(string="Plane materiel")

    product_opento = fields.Selection([
        ('left', _("左开")),
        ('right', _("右开")),
        ('twoopen', _('对开')),
        ('upward', _('上翻')),
        ('down', _('下翻')),
        ('noopen', _('不开')),
        ('twoopen_and_right', _('对开+右开')),
        ('twoopen_and_left', _('对开+左开')),
    ], string=_("开向"))
    picking_type_code = fields.Selection(related='picking_id.picking_type_code',readonly=True)
    outsource_quantity = fields.Float(string='数量', digits=dp.get_precision('Product Unit of Measure'))
