# coding: utf-8
######################################

from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    ret = fields.Boolean(
        string='Withholdable',
        help="Indicate if the tax must be withheld")

    wh_vat_collected_account_id = fields.Many2one(
        'account.account',
        string="Invoice VAT Withholding Account",
        help="This account will be used when applying a withhold to an"
        " Invoice")

    wh_vat_paid_account_id = fields.Many2one(
        'account.account',
        string="Refund VAT Withholding Account",
        help="This account will be used when applying a withhold to a"
        " Refund")

    type_tax = fields.Selection([('iva', 'IVA'),
        						('islr', 'ISLR'),
        						('responsability','Social responsability'),
        						('municipal', 'Municipal'),
        						('fiscal', 'Stamp duty')],required=True,help="Tax type",string="Tipo de Impuesto")