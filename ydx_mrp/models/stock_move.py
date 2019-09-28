from odoo import models, fields


class YdxStockMove(models.Model):
	_inherit = "stock.move"

	Order_number = fields.Char(strint="Order_number")
	The_child_orders = fields.Char(int="The_child_orders")
	Base_material = fields.Char(string="Base material")
	Plane_materiel = fields.Char(string="Plane materiel")
	Thickness = fields.Float(string="Thickness")
	Length = fields.Float(string="Length")
	Breadth = fields.Float(string="Breadth")



