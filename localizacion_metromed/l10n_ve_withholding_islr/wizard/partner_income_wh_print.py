# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from odoo import fields, models
from odoo.tools.translate import _
from odoo import exceptions


class PartnerIncomeWhPrintwizard(models.TransientModel):

    """
    This wizard will print the islr reports for a given partner.
    """
    def _get_company(self):
        user = self.env['res.users'].browse()
        return user.company_id.id

    _name = 'partner.income.wh.print'
    _description = 'Partner Income Withholding Print'

    #period_id= fields.Many2one(
    #        'account.period',
    #        string='Period',
    #        required=True,
    #        help='Fiscal period to be use in the report.')
    partner_id = fields.Many2one(
            'res.partner',
            string='Partner',
            required=True,
            help='Partner to be use in the report.')
    company_id = fields.Many2one(
            'res.company',
            string='Company',
            required=True,
            default=lambda s: s._get_company(),
            help='Company')
    #iwdl_ids = fields.Many2many(
    #        'islr.wh.doc.line',
    #        'rel_wizard_iwdl',
    #        'iwdl_list',
    #        'iwdl_ids',
    #        string='ISLR WH Doc Line',
    #        help='ISLR WH Doc Line')


    def get_partner_address(self,idp):
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        rp_obj = self.env['res.partner']
        addr = rp_obj.browse(idp)
        addr_inv = (addr.street and ('%s, ' % addr.street.title()) or '') + \
            (addr.zip and ('Codigo Postal: %s, ' % addr.zip) or '') +\
            (addr.city and ('%s, ' % addr.city.title()) or '') + \
            (addr.state_id and ('%s, ' % addr.state_id.name.title()) or '') + \
            (addr.country_id and
             ('%s ' % addr.country_id.name.title()) or
             '') or _('NO INVOICE ADDRESS DEFINED')
        return addr_inv

    def print_report(self):
        """
        @return an action that will print a report.
        """
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        iwdl_obj = self.env['islr.wh.doc.line']
       # brw = self.browse(ids[0])
        iwdl_ids = iwdl_obj.search([
            ('invoice_id.partner_id', '=', self.partner_id.id),
            #('islr_wh_doc_id.period_id', '=', brw.period_id.id),
            ('islr_wh_doc_id.type', '=', 'in_invoice'),
            ('islr_wh_doc_id.state', '=', 'done')])
        if iwdl_ids:
            self.write({
                'iwdl_ids': [(6, 0, iwdl_ids)]}, )
        else:
            raise exceptions.except_orm(_(u'No Withholdings'),
                                 _(u'No Income Withholding for %s'
                                   % self.partner_id.name.upper()))
        data = dict()
        data['ids'] = ids
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'l10n.ve.partner.income.wh.report', 'datas': data}
