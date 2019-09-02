# -*- coding: utf-8 -*-
from odoo import http

# class YdxStaff(http.Controller):
#     @http.route('/ydx_staff/ydx_staff/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ydx_staff/ydx_staff/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ydx_staff.listing', {
#             'root': '/ydx_staff/ydx_staff',
#             'objects': http.request.env['ydx_staff.ydx_staff'].search([]),
#         })

#     @http.route('/ydx_staff/ydx_staff/objects/<model("ydx_staff.ydx_staff"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ydx_staff.object', {
#             'object': obj
#         })