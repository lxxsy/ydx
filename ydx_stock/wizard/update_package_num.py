# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class UpdatePackageNum(models.TransientModel):
    _name = 'update.package.num.wizard'

    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', index=True)
    metal_package_num = fields.Integer(string='Metal Package Number', copy=False)
    line_ids = fields.One2many('update.package.num.line', 'order_id', string='Order Lines')

    @api.multi
    def update_package_num(self):
        for pick in self:
            pick.picking_id.metal_package_num = pick.metal_package_num
            for pick_line in pick.picking_id.sub_sale_order_ids:
                for update_line in pick.line_ids:
                    if pick_line.name == update_line.name:
                        pick_line.package_num = update_line.package_num

    def _prepare_return_line_from_so_line(self, line):
        data = {
            'name': line.name,
            'package_num': line.package_num
        }
        return data

    @api.onchange('picking_id')
    def _onchange_picking(self):
        for pick in self:
            new_lines = self.env['update.package.num.line']
            for line in pick.picking_id.sub_sale_order_ids:
                data = self._prepare_return_line_from_so_line(line)
                new_line = new_lines.new(data)
                new_lines += new_line
            pick.line_ids = new_lines
            pick.metal_package_num = pick.picking_id.metal_package_num
            pick.env.context = dict(pick.env.context, from_update_package_num_change=True)


class UpdatePackageNumLine(models.TransientModel):
    _name = 'update.package.num.line'

    name = fields.Char(string='Order Reference', required=True)
    package_num = fields.Integer(string='Package Number', copy=False, default='')
    order_id = fields.Many2one('update.package.num.wizard', string='Order', required=True, ondelete='cascade')


