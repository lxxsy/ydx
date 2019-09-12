# -*- coding: utf-8 -*-
from odoo import http

# class Receivable(http.Controller):
#     @http.route('/receivable/receivable/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/receivable/receivable/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('receivable.listing', {
#             'root': '/receivable/receivable',
#             'objects': http.request.env['receivable.receivable'].search([]),
#         })

#     @http.route('/receivable/receivable/objects/<model("receivable.receivable"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('receivable.object', {
#             'object': obj
#         })