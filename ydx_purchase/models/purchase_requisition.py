from odoo import api, fields, models


class YdxPurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")
    product_opento = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right')
    ], string="Product Opento")

