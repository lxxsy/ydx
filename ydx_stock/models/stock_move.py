# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class YdxStockMove(models.Model):
    _inherit = "stock.move"

    product_function_type = fields.Selection(related='product_id.fuction_type', readonly=True)
	cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")