from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('metals',  'Metals'),
                                           ('outsource', 'Outsource'),
                                           ('parts', 'Production Parts')])
