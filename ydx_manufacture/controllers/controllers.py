# -*- coding: utf-8 -*-
from odoo import http

# class YdxPerfectManufacturing(http.Controller):
#     @http.route('/ydx_perfect_manufacturing/ydx_perfect_manufacturing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ydx_perfect_manufacturing/ydx_perfect_manufacturing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ydx_perfect_manufacturing.listing', {
#             'root': '/ydx_perfect_manufacturing/ydx_perfect_manufacturing',
#             'objects': http.request.env['ydx_perfect_manufacturing.ydx_perfect_manufacturing'].search([]),
#         })

#     @http.route('/ydx_perfect_manufacturing/ydx_perfect_manufacturing/objects/<model("ydx_perfect_manufacturing.ydx_perfect_manufacturing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ydx_perfect_manufacturing.object', {
#             'object': obj
#         })