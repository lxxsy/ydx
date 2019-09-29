from odoo import models, fields


class YdxStockMove(models.Model):
	_inherit = "stock.move"

	order_number = fields.Char(strint="Order number")
	the_child_orders = fields.Char(int="The child orders")
	base_material = fields.Char(string="Base material")
	plane_materiel = fields.Char(string="Plane materiel")
	thickness = fields.Float(string="Thickness")
	length = fields.Float(string="Length")
	breadth = fields.Float(string="Breadth")



