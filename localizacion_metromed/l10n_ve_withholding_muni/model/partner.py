# -*- coding: utf-8 -*-
##############################################################################
#
#    autor: Tysamnca.
#
##############################################################################

from odoo import fields, models

class ResParther(models.Model):
    _inherit = 'res.partner'

    property_county_wh_payable = fields.Many2one('account.account',
                                                 company_dependent=True,
                                                 string="Purchase local withholding account",
                                                 oldname="property_county_wh_payable",
                                                 help="This account will be used debit local withholding amount",
                                                 required=False)

    property_county_wh_receivable = fields.Many2one('account.account',
                                                    company_dependent=True,
                                                    string="Sale local withholding account",
                                                    oldname="property_county_wh_receivable",
                                                    help="This account will be used credit local withholding amount",
                                                    required = False)

