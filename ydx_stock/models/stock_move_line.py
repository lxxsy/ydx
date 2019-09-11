from odoo import models,fields


class YdxStockMove(models.Model):
    _inherit = "stock.move.line"

    cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")
