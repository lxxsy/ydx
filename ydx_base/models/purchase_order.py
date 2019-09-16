# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', index=True, copy=False)
    source_attachment = fields.Binary(related="sale_order_id.attachment", string="Source Attachment")


