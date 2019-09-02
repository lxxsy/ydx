# -*- coding: utf-8 -*-
from odoo import http

# class YdxBase(http.Controller):
#     @http.route('/ydx_base/ydx_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ydx_base/ydx_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ydx_base.listing', {
#             'root': '/ydx_base/ydx_base',
#             'objects': http.request.env['ydx_base.ydx_base'].search([]),
#         })

#     @http.route('/ydx_base/ydx_base/objects/<model("ydx_base.ydx_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ydx_base.object', {
#             'object': obj
#         })