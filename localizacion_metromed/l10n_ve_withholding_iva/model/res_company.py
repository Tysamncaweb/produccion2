# coding: utf-8
###############################################################################

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    consolidate_vat_wh = fields.Boolean(
        string="Fortnight Consolidate Wh. VAT", default=False,
        help="If it set then the withholdings vat generate in a same"
        " fornight will be grouped in one withholding receipt.")
    allow_vat_wh_outdated = fields.Boolean(
        string="Allow outdated vat withholding",
        help="Enables confirm withholding vouchers for previous or future"
        " dates.")
    propagate_invoice_date_to_vat_withholding = fields.Boolean(
        string='Propagate Invoice Date to Vat Withholding', default=False,
        help='Propagate Invoice Date to Vat Withholding. By default is in'
        ' False.')
