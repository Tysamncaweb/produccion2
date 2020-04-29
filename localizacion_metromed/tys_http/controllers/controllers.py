# -*- coding: utf-8 -*-
from odoo import http

# class Submodules/tysHttp(http.Controller):
#     @http.route('/submodules/tys_http/submodules/tys_http/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/submodules/tys_http/submodules/tys_http/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('submodules/tys_http.listing', {
#             'root': '/submodules/tys_http/submodules/tys_http',
#             'objects': http.request.env['submodules/tys_http.submodules/tys_http'].search([]),
#         })

#     @http.route('/submodules/tys_http/submodules/tys_http/objects/<model("submodules/tys_http.submodules/tys_http"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('submodules/tys_http.object', {
#             'object': obj
#         })