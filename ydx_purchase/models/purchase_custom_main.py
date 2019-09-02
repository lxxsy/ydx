# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime


class purchase_custom(models.Model):
    _name = 'purchase.custom.product'

    name = fields.Char("Template", required=True)
    check_active = fields.Boolean("Active", default="True")
    purchase_custom_line_ids = fields.One2many("purchase.custom.lines", "purchase_custom_id")


class purchase_custom_lines(models.Model):
    _name = 'purchase.custom.lines'

    purchase_custom_id = fields.Many2one("purchase.custom.product")
    product_id = fields.Many2one("product.product", string="产品", required=True)
    desc_name = fields.Char("Description", required=True)
    order_qty = fields.Float("Order Quantity", default=1.0)
    unit_price = fields.Float("Unit Price")
    uom = fields.Many2one("uom.uom", string="UOM")

    @api.onchange("product_id")
    def onchnange_product(self):
        for i in self:
            if i.product_id:
                i.desc_name = i.product_id.display_name
                i.uom = i.product_id.uom_id
                i.unit_price = i.product_id.standard_price


class inherit_purchase(models.Model):
    _inherit = "purchase.order"

    product_template_id = fields.Many2one("purchase.custom.product", string="Product Template",
                                          domain=[('check_active', '=', True)])

    @api.onchange('product_template_id')
    def onchange_product_template(self):
        if self.product_template_id:
            product_list = []
            for i in self.product_template_id:
                for j in i.purchase_custom_line_ids:
                    product_list.append((0, 0, {
                        "date_planned": datetime.now(),
                        "product_id": j.product_id.id,
                        "name": j.desc_name,
                        "product_qty": j.order_qty,
                        "price_unit": j.unit_price,
                        "product_uom": j.uom.id,
                    }))

                self.update({"order_line": product_list})
