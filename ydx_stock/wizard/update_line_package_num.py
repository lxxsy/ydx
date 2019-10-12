# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class UpdateLinePackageNum(models.TransientModel):
    _name = 'update.line.package.num.wizard'
    picking_id = fields.Many2one('stock.sub.sale.order', _('子销售订单号'), index=True)
    package_num = fields.Integer(string='包裹数量', copy=False)

    @api.multi
    def update_package_num(self):
        for pick in self:
            pick.picking_id.package_num = pick.package_num
            sub_order = self.env['sub.sale.order'].sudo().search([('id', '=', pick.picking_id.sub_sale_order_id)])
            sub_order._sync_package_num(pick.package_num)

    @api.onchange('picking_id')
    def _onchange_picking(self):
        for pick in self:
            pick.package_num = pick.picking_id.package_num
            pick.env.context = dict(pick.env.context, from_update_package_num_change=True)


class UpdateLineoutsOurcePackageNum(models.TransientModel):
    _name = 'update.line.outsource.package.num.wizard'
    picking_id = fields.Many2one('stock.sub.sale.order', _('子销售订单号'), index=True)
    outsource_package_num = fields.Integer(string=_('外购包裹数量'), copy=False)

    @api.multi
    def update_package_num(self):
        for pick in self:
            pick.picking_id.outsource_package_num = pick.outsource_package_num

            sub_order = self.env['sub.sale.order'].sudo().search([('id', '=', pick.picking_id.sub_sale_order_id)])
            sub_order._sync_outsource_package_num(pick.outsource_package_num)
            stock_all_sub_orders = self.env['stock.sub.sale.order'].sudo().search(
                [('sub_sale_order_id', '=', pick.picking_id.sub_sale_order_id)])
            stock_all_sub_orders._sync_outsource_package_num(pick.outsource_package_num)

    @api.onchange('picking_id')
    def _onchange_picking(self):
        for pick in self:
            pick.outsource_package_num = pick.picking_id.outsource_package_num
            pick.env.context = dict(pick.env.context, from_update_package_num_change=True)
