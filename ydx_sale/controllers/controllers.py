# -*- coding: utf-8 -*-
from odoo import http

# class YdxSale(http.Controller):
#     @http.route('/ydx_sale/ydx_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ydx_sale/ydx_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ydx_sale.listing', {
#             'root': '/ydx_sale/ydx_sale',
#             'objects': http.request.env['ydx_sale.ydx_sale'].search([]),
#         })

#     @http.route('/ydx_sale/ydx_sale/objects/<model("ydx_sale.ydx_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ydx_sale.object', {
#             'object': obj
#         })