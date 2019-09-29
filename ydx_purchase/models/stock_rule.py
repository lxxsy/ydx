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
                ('purchase_type', '=', 'outsource'),
            )
        else:
            domain += (
                ('purchase_type', '=', 'purchase'),
            )
        return domain

    def _prepare_purchase_order(self, product_id, product_qty, product_uom, origin, values, partner):
        purchase_order = super(StockRule, self)._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
        purchase_order['sale_order_id'] = values.get('sale_order_id', False)
        if origin.startswith('OP/'):
            purchase_order['purchase_type'] = 'purchase'
        else:
            purchase_order['purchase_type'] = 'outsource'
        return purchase_order

    def _get_custom_move_fields(self):
        custom_fields = super(StockRule, self)._get_custom_move_fields()
        custom_fields.append('sale_order_id')
        custom_fields.append('outsource')
        return custom_fields

    @api.multi
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, values, po, partner):
        line = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, partner)
        line['cabinet_no'] = values.get('cabinet_no','')
        line['material'] = values.get('material','')
        line['product_colour'] = values.get('product_colour','')
        line['product_length'] = values.get('product_length','')
        line['width'] = values.get('width','')
        line['thickness'] = values.get('thickness','')
        line['remarks'] = values.get('remarks','')
        line['product_opento'] = values.get('product_opento','')
        line['product_speci_type'] = values.get('product_speci_type','')
        return line