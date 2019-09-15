# -*- coding: utf-8 -*-

from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment = fields.Binary(String="Attachment")
    purchase_order_ids = fields.One2many('purchase.order', 'sale_order_id', string='Purchase Orders', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
