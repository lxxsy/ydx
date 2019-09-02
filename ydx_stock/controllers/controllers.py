# -*- coding: utf-8 -*-
from odoo import http

# class YdxStock(http.Controller):
#     @http.route('/ydx_stock/ydx_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ydx_stock/ydx_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ydx_stock.listing', {
#             'root': '/ydx_stock/ydx_stock',
#             'objects': http.request.env['ydx_stock.ydx_stock'].search([]),
#         })

#     @http.route('/ydx_stock/ydx_stock/objects/<model("ydx_stock.ydx_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ydx_stock.object', {
#             'object': obj
#         })