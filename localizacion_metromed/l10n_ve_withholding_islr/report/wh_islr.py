# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

#from openerp.report import report_sxw
#from openerp.tools.translate import _

from odoo import models, api, _
from odoo.exceptions import UserError, Warning


class RepComprobanteIslr(models.AbstractModel):
    _name = 'report.l10n_ve_withholding_islr.template_wh_islr'

    # _inherit = 'report.abstract_report'
    # _template = 'l10n_ve_withholding_iva.template_wh_vat'

    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['islr.wh.doc'].browse(docids)}
        res = dict()
        return {
            'data': data['form'],
            'model': self.env['report.l10n_ve_withholding_islr.template_wh_islr'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
        }
    def _get_date_invoice(self, id):

        date_invoice = id[0].invoice_id.date_document
        return date_invoice

    def _get_supplier_invoice_number(self, id):

        supplier_number = id[0].invoice_id.supplier_invoice_number
        return supplier_number

    def _get_nro_ctrl(self, id):

        nro_ctrl = id[0].invoice_id.nro_ctrl
        return nro_ctrl

    def _get_islr_wh_concept(self,id):

        concept = id[0].concept_id.name

        return concept

    def _get_islr_wh_retencion_islr(self,id):

        retencion_islr_local = id[0].retencion_islr
        return retencion_islr_local

    def _get_islr_wh_doc_invoices_base(self,id):

        base_ret_local = id[0].base_amount
        return base_ret_local

    def _get_islr_wh_doc_invoice_subtract(self,id):

        subtract_local = id[0].subtract
        return subtract_local

    def _get_islr_invoice_amount_ret(self,id):

        amount_ret_local = id[0].amount
        return amount_ret_local


    def get_period(self, date):
        if not date:
            raise Warning(_("You need date."))
        split_date = date.split('-')
        return str(split_date[1]) + '/' + str(split_date[0])

    def get_date(self, date):
        if not date:
            raise Warning(_("You need date."))
        split_date = date.split('-')
        return str(split_date[2]) + '/' + (split_date[1]) + '/' + str(split_date[0])


    def get_direction(self, partner):
        direction = ''
        direction = ((partner.street and partner.street + ', ') or '') + \
                    ((partner.street2 and partner.street2 + ', ') or '') + \
                    ((partner.city and partner.city + ', ') or '') + \
                    ((partner.state_id.name and partner.state_id.name + ',')or '')+ \
                    ((partner.country_id.name and partner.country_id.name + '') or '')
        if direction == '':
            direction = 'Sin direccion'
        return direction

    def get_tipo_doc(self, tipo=None):
        if not tipo:
            return []
        types = {'out_invoice': '1', 'in_invoice': '1', 'out_refund': '2',
                 'in_refund': '2'}
        return types[tipo]
