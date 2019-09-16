# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class UpdateOutPackageNum(models.TransientModel):
    _name = 'update.out.package.num.wizard'

    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', index=True)
    metal_package_num = fields.Integer(string='Metal Package Number', copy=False)
    line_ids = fields.One2many('update.out.package.num.line', 'order_id', string='Order Lines')

    @api.multi
    def update_package_num(self):
        for pick in self:
            pick.picking_id.metal_package_num = pick.metal_package_num
            for pick_line in pick.picking_id.sub_sale_order_ids:
                for update_line in pick.line_ids:
                    if pick_line.name == update_line.name:
                        pick_line.update({"package_num":update_line.package_num})
                        sub_order = self.env['sub.sale.order'].sudo().search([('id', '=', pick_line.sub_sale_order_id)])
                        sub_order._sync_package_num(update_line.package_num)

    def _prepare_return_line_from_so_line(self, line):
        data = {
            'name': line.name,
            'package_num': line.package_num,
        }
        return data

    @api.onchange('picking_id')
    def _onchange_picking(self):
        for pick in self:
            new_lines = self.env['update.out.package.num.line']
            for line in pick.picking_id.sub_sale_order_ids:
                data = self._prepare_return_line_from_so_line(line)
                new_line = new_lines.new(data)
                new_lines += new_line
            pick.line_ids = new_lines
            pick.metal_package_num = pick.picking_id.metal_package_num
            pick.env.context = dict(pick.env.context, from_update_package_num_change=True)


class UpdateOutPackageNumLine(models.TransientModel):
    _name = 'update.out.package.num.line'

    name = fields.Char(string='Order Reference', required=True)
    package_num = fields.Integer(string='Package Number', copy=False, default='')
    order_id = fields.Many2one('update.out.package.num.wizard', string='Order', required=True, ondelete='cascade')


class UpdateInPackageNum(models.TransientModel):
    _name = 'update.in.package.num.wizard'

    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', index=True)
    line_ids = fields.One2many('update.in.package.num.line', 'order_id', string='Order Lines')

    @api.multi
    def update_package_num(self):
        for pick in self:
            for pick_line in pick.picking_id.sub_sale_order_ids:
                for update_line in pick.line_ids:
                    if pick_line.name == update_line.name:
                        pick_line.update({"outsource_package_num":update_line.outsource_package_num})
                        sub_order = self.env['sub.sale.order'].sudo().search([('id', '=', pick_line.sub_sale_order_id)])
                        sub_order._sync_outsource_package_num(update_line.outsource_package_num)
                        stock_all_sub_orders = self.env['stock.sub.sale.order'].sudo().search([('sub_sale_order_id', '=', pick_line.sub_sale_order_id)])
                        for subso in stock_all_sub_orders:
                            subso._sync_outsource_package_num(update_line.outsource_package_num)

    def _prepare_return_line_from_so_line(self, line):
        data = {
            'name': line.name,
            'outsource_package_num': line.outsource_package_num,
        }
        return data

    @api.onchange('picking_id')
    def _onchange_picking(self):
        for pick in self:
            new_lines = self.env['update.in.package.num.line']
            for line in pick.picking_id.sub_sale_order_ids:
                data = self._prepare_return_line_from_so_line(line)
                new_line = new_lines.new(data)
                new_lines += new_line
            pick.line_ids = new_lines
            pick.env.context = dict(pick.env.context, from_update_package_num_change=True)


class UpdateInPackageNumLine(models.TransientModel):
    _name = 'update.in.package.num.line'

    name = fields.Char(string='Order Reference', required=True)
    outsource_package_num = fields.Integer(string='Outsource Package Number', copy=False, default='')
    order_id = fields.Many2one('update.in.package.num.wizard', string='Order', required=True, ondelete='cascade')



