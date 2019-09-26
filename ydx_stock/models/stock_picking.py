# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"

    metal_package_num = fields.Integer(string='����������', copy=False)
    fmetals_move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", domain=['|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)],ondelete='cascade')
    cmetals_move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", domain=['|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)], ondelete='cascade')
    outsource_move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", domain=['|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)], ondelete='cascade')
    sub_sale_order_ids = fields.One2many('stock.sub.sale.order', 'picking_id', string='Sub Sale Orders', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True, ondelete='cascade')
    stock_production_part_ids = fields.One2many('stock.production.part', 'picking_id', string='Stock Production Part', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True, ondelete='cascade')
    is_payall = fields.Boolean(string='Pay All', default=False)
    incoming_type = fields.Selection([('purchase',  '�ɹ�����'), ('outsource',  'ί��')], default='purchase', required=True, string="�ջ�����")
    @api.multi
    def button_confirm_payall(self):
        for pick in self:
            pick.is_payall = True
