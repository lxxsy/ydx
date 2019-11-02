# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"

    metal_package_num = fields.Integer(string='五金包裹数量', copy=False)
    fmetals_move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", domain=[('product_function_type', '=', 'fmetals'),'|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)],ondelete='cascade')
    cmetals_move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", domain=[('product_function_type', '=', 'cmetals'),'|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)], ondelete='cascade')
    outsource_move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", domain=[('product_function_type', '=', 'outsource'),'|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)], ondelete='cascade')
    sub_sale_order_ids = fields.One2many('stock.sub.sale.order', 'picking_id', string='Sub Sale Orders', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True, ondelete='cascade')
    stock_production_part_ids = fields.One2many('stock.production.part', 'picking_id', string='Stock Production Part', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True, ondelete='cascade')
    is_payall = fields.Boolean(string='Pay All', default=False)
    incoming_type = fields.Selection([('purchase',  '采购订单'), ('outsource',  '委外')], default='purchase', required=True, string="收货类型")
    express_info = fields.Char(string='物流快递')
    cargo_state = fields.Selection([('no',  '未完成'), ('done',  '完成')], default='no', required=True, string="备货状态")
    outsource_sale_id = fields.Char(_('委外销售订单'), related='purchase_id.origin')
    @api.multi
    def button_confirm_payall(self):
        for pick in self:
            pick.is_payall = True


    @api.multi
    def button_cargo_state(self):
        for order in self:
            order.write({'cargo_state': 'done'})
        return True
