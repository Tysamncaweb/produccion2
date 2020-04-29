# coding: utf-8
###########################################################################

import logging

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    logger = logging.getLogger('res.partner')

    consolidate_vat_wh = fields.Boolean(
        string='Fortnight Consolidate Wh. VAT',
        help='If set then the withholdings vat generate in a same'
        ' fornight will be grouped in one withholding receipt.')

    wh_iva_agent = fields.Boolean(
        'Wh. Agent',
        help="Indicate if the partner is a withholding vat agent")

    wh_iva_rate = fields.Float(
        string='Rate',
        help="Vat Withholding rate")

    vat_subjected = fields.Boolean('VAT Legal Statement',
    help="Check this box if the partner is subjected to the VAT. It will be used for the VAT legal statement.")

    purchase_journal_id = fields.Many2one('account.journal','Journal of purchases')
    purchase_sales_id = fields.Many2one('account.journal', 'Journal of sales')
