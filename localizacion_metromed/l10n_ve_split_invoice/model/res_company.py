# coding: utf-8

from odoo import fields,models


class ResCompany(models.Model):
    _inherit = 'res.company'

    lines_invoice = fields.Integer ('Invoices line',requiere=False, default=50, help="Number of lines per invoice" )


ResCompany()
