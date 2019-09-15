# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_get_domain(self, values, partner):
        domain = super(StockRule, self)._make_po_get_domain(values, partner)
        if 'sale_order_id' in values:
            domain += (
                ('sale_order_id', '=', values['sale_order_id']),
            )
        return domain

    def _prepare_purchase_order(self, product_id, product_qty, product_uom, origin, values, partner):
        purchase_order = super(StockRule, self)._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
        purchase_order['sale_order_id'] = values.get('sale_order_id', False)
        return purchase_order

    def _get_custom_move_fields(self):
        custom_fields = super(StockRule, self)._get_custom_move_fields()
        custom_fields.append('sale_order_id')
        return custom_fields