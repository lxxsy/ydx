# -*- coding: utf-8 -*-
#
# from odoo import models, fields, api
# from mrp.models import product
# from mrp_account import mrp_production
#
#
# # class ydx_perfect_manufacturing(models.Model):
# #     _name = 'ydx_perfect_manufacturing.ydx_perfect_manufacturing'
#
# #     name = fields.Char()
# #     value = fields.Integer()
# #     value2 = fields.Float(compute="_value_pc", store=True)
# #     description = fields.Text()
# #
# #     @api.depends('value')
# #     def _value_pc(self):
# #         self.value2 = float(self.value) / 100
# class ydx_cost_curve(models.Model):
#
#     # ---继承
#     _inherit = ['product.template','product.product','mrp.workcenter.productivity']
#
#     # 成本
#     product_cost_ydx = fields.Many2one('总成本', default= '_costs_generate')
#
#     #   时间
