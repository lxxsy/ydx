from odoo import fields, models,_


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fuction_type = fields.Selection([('cmetals',  'Connection Metals'),
                                   ('fmetals',  'Function Metals'),
                                   ('outsource', 'Outsource'),
                                   ('parts', 'Production Parts'),
                                     ('finished','成品')])
