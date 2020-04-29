# -*- coding: utf-8 -*-
from odoo import http

# class Submodules/intelAccountInvoiceReport(http.Controller):
#     @http.route('/submodules/intel_account_invoice_report/submodules/intel_account_invoice_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/submodules/intel_account_invoice_report/submodules/intel_account_invoice_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('submodules/intel_account_invoice_report.listing', {
#             'root': '/submodules/intel_account_invoice_report/submodules/intel_account_invoice_report',
#             'objects': http.request.env['submodules/intel_account_invoice_report.submodules/intel_account_invoice_report'].search([]),
#         })

#     @http.route('/submodules/intel_account_invoice_report/submodules/intel_account_invoice_report/objects/<model("submodules/intel_account_invoice_report.submodules/intel_account_invoice_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('submodules/intel_account_invoice_report.object', {
#             'object': obj
#         })