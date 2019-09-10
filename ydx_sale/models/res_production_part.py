# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResProductionPart(models.Model):
    _inherit = 'res.production.part'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    order_id = fields.Many2one('sale.order', related='sub_order_id.order_id', string='Sale Order', required=True, index=True, copy=False)
    sub_order_id = fields.Many2one('sub.sale.order', string='Sub Sale Order', required=True, ondelete='cascade', index=True, copy=False)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")