# -*- coding: utf-8 -*-
from odoo import http

# class Submodules/accountPeriod(http.Controller):
#     @http.route('/submodules/account_period/submodules/account_period/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/submodules/account_period/submodules/account_period/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('submodules/account_period.listing', {
#             'root': '/submodules/account_period/submodules/account_period',
#             'objects': http.request.env['submodules/account_period.submodules/account_period'].search([]),
#         })

#     @http.route('/submodules/account_period/submodules/account_period/objects/<model("submodules/account_period.submodules/account_period"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('submodules/account_period.object', {
#             'object': obj
#         })