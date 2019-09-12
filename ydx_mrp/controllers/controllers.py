# -*- coding: utf-8 -*-
from odoo import http

# class YdxMrp(http.Controller):
#     @http.route('/ydx_mrp/ydx_mrp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ydx_mrp/ydx_mrp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ydx_mrp.listing', {
#             'root': '/ydx_mrp/ydx_mrp',
#             'objects': http.request.env['ydx_mrp.ydx_mrp'].search([]),
#         })

#     @http.route('/ydx_mrp/ydx_mrp/objects/<model("ydx_mrp.ydx_mrp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ydx_mrp.object', {
#             'object': obj
#         })