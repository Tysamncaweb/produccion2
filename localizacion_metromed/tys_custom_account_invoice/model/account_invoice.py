# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Modulo que permite la anulacion de cheques antes de ser emitidos
#    autor: Tysamnca.
#
##############################################################################

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime

class PurchaseBook(models.AbstractModel):

    _name = 'report.tys_custom_account_invoice.custom_invoice_template'

    @api.multi
    def get_report_values(self, docids, data=None):
        invoices =[]
        invoice_lines = []
        for inv_id in docids:
            invoices.append(self.env['account.invoice'].browse(inv_id))
            invoice_lines = self.env['account.invoice.line'].search([('invoice_id','=',inv_id)])

        telefono = '0' + invoices[0].partner_id.phone[4:]
        formated_rif = invoices[0].partner_id.vat[2:]
        return {
            'telefono': telefono,
            'formated_rif':formated_rif,
            'invoices': invoices,
            'invoice_lines': invoice_lines
        }
