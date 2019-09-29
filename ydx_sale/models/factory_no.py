# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime

class SaleFactoryNo(models.Model):
    _name = "sale.factory.no"

    name = fields.Char('Factory No')
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, index=True, copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code("sale.factory.no")
        return super(SaleFactoryNo, self).create(vals)


class sequence(models.Model):
    _inherit = 'ir.sequence'
    last_month = fields.Integer("last",default=0)
    auto_reset = fields.Boolean("Auto reset", default=False)

    def _next(self):
        if self.auto_reset:
            thismonth=int(datetime.datetime.now().month)
            if thismonth!=self.last_month:
                self.last_month=thismonth
                self.number_next_actual=1
        result = super(sequence,self)._next()
        return result