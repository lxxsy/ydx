# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class YdxSaleAccountInvoice(models.Model):
    _inherit = 'account.invoice'



class YdxSaleAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _order = 'invoice_id, sequence, id'

    sale_return_line_ids = fields.Many2many(
        'sale.return.line',
        'sale_return_line_invoice_rel',
        'invoice_line_id', 'return_line_id',
        string='Sales Return Lines', readonly=True, copy=False)

    sub_sale_line_ids = fields.Many2many(
        'sub.sale.line',
        'sub_sale_line_invoice_rel',
        'invoice_line_id', 'sub_sale_line_id',
        string='Sub Sales Lines', readonly=True, copy=False)