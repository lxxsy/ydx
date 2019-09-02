# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018 Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    last_price1 = fields.Float('The Last Price', help="Shows the last sales price of the product for selected customer from the Past two Sales order")
    # last_price2 = fields.Float('Last Sale Price 2', help="Shows the second last sales price of the product for selected customer from the Past two Sales order")



    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        result = {}
        last_price1 = 0.0
        # last_price2 = 0.0

        for record in self:
            line_ids = []
            if record.product_id:
                order_lines = self.env['sale.order.line'].sudo().search([('order_partner_id', '=', record.order_partner_id.id),('product_id', '=', record.product_id.id),('order_id.state','in',('sale','done'))])
                if order_lines:
                    for lines in order_lines:
                        line_ids.append(lines.id)
            final_list = sorted(line_ids, key=int, reverse=True)
            if len(final_list)>=1:
                last_price1 = self.env['sale.order.line'].sudo().browse(final_list[0])
                record.last_price1 = last_price1.price_unit
            # if len(final_list)>=2:
            #     last_price2 = self.env['sale.order.line'].sudo().browse(final_list[1])
            #     record.last_price2 = last_price2.price_unit


