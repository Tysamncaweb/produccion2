# coding: utf-8
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
import base64

import odoo.addons as addons
from odoo import fields, models,api



class WhIslrConfig(models.TransientModel):
    _name = 'wh.islr.config'
    _inherit = 'res.config'
    _description = __doc__

    @api.model
    def default_get(self,fields_list):
        """ Default value config_logo field
        """
        defaults = super(WhIslrConfig, self).default_get(
        fields_list=fields_list)
        logo = open(addons.get_module_resource(
            'l10n_ve_withholding_islr', 'images', 'playa-medina.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    @api.model
    def _create_journal(self, name, jtype, code):
        """ Create journal account
        """

        self.env("account.journal").create({
            'name': name,
            'type': jtype,
            'code': code,
            'view_id': 3,
        })

    @api.model
    def _update_concepts(self,purchase,sale):
        """ Update sale and purchase concepts
        @param sale: sale concept
        @param purchase: purchase concept
        """
        context = self.context or {}
        concept_pool = self.env("islr.wh.concept")
        concept_pool.write(
             concept_pool.search([], context=context), {
                'property_retencion_islr_payable': purchase,
                'property_retencion_islr_receivable': sale}, context=context)
        return True

    @api.model
    def _set_wh_agent(self):
        """ Set if is withholding agent or not
        """
        company = self.env('res.users').browse().company_id
        self.env('res.partner').write(
             [company.partner_id.id], {'islr_withholding_agent': True})

    def execute(self):
        """ Create journals and determinate if is withholding agent or not
        """
        wiz_data = self.read()
        if wiz_data['journal_purchase']:
            self._create_journal(["journal_purchase"], 'islr_purchase',
                'ISLRP')
        if wiz_data['journal_sale']:
            self._create_journal(['journal_sale'], 'islr_sale', 'ISLRS')
        if wiz_data['account_sale'] or wiz_data['account_purchase']:
            self._update_concepts(['account_sale'][0],
                ['account_purchase'][0])
        if wiz_data['wh_agent']:
            self._set_wh_agent()


    journal_purchase= fields.Char(
            string="Journal Wh Income Purchase", size=64,
            default="Journal Income Withholding Purchase",
            help="Journal for purchase operations involving Income"
                 " Withholding")
    journal_sale= fields.Char(
            string="Journal Wh Income Sale", size=64,
            default="Journal Income Withholding Sale",
            help="Journal for sale operations involving Income Withholding"),
    account_purchase= fields.Many2one(
            "account.account",
            "Account Income Withholding Purchase",
            help="Account for purchase operations involving Income Withholding")

    account_sale= fields.Many2one(
            "account.account",
            "Account Income Withholding Sale",
            help="Account for sale operations involving Income Withholding",
        )
    wh_agent= fields.Boolean(
            "Income Withholding Agent",
            help="Check if this company is a income withholding agent")


WhIslrConfig()
