from odoo import models, fields


class YdxStockMove(models.Model):
	_inherit = "stock.move"

	order_number = fields.Char(strint="order number")
	the_child_orders = fields.Char(int="the child orders")
	Base_material = fields.Char(string="Base material")
	plane_materiel = fields.Char(string="plane materiel")



