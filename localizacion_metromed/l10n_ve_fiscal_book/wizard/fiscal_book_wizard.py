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
import time

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date, timedelta


class FiscalBookWizard(models.TransientModel):

    """
    Sales book wizard implemented using the osv_memory wizard system
    """
    _name = "fiscal.book.wizard"

    TYPE = [("sale", _("Venta")),
            ("purchase", _("Compra")),
        ]
    @api.multi
    def _get_account_period(self, date=None):
        if not date:
            date = time.strftime('%Y-%m-%d')
        ids = self.env['account.period'].search([('date_start', '<=', date), ('date_stop', '>=', date)])
        if not ids:
            raise exceptions('Error !','No period defined for this date !\nPlease create a'
                  ' fiscal year.')
        return ids


    def _same_account_period(self, admin_date, account_date):
        return self._get_account_period(admin_date) == self._get_account_period(account_date)

    def _do_purchase_report(self, cr, uid, data, context=None):
        """
        This method should be overriden to generate the SENIAT purchase report
        """
        return False

    @api.multi
    def _get_needed_data(self, data):
        if data['type'] == 'sale':
            data_list_view = self._gen_wh_sales_list(
                self._cr, data['date_start'], data['date_end'])
            inv_obj = self.env['account.invoice']
            inv_ids = inv_obj.search([('date_invoice', '>=', data['date_start']),
                          ('date_invoice','<=', data['date_end']),
                          ('type', '=', 'out_invoice')])
            #inv_rd = inv_obj.read(inv_ids)
            #inv_browse = inv_obj.browse(inv_ids)
            control_numbers = range(
                data['control_start'], data['control_end'] + 1)
            #return (data_list_view, inv_rd, control_numbers, inv_browse)
            return (data_list_view, inv_ids, control_numbers)
        else:  # TODO: when it is purchase
            pass

    def _get_missing_inv_numbers(self, sequence, numbers_found):
        return set(set(sequence) ^ set(numbers_found))

    def _check_retention(self, all_data, retention_number):
        for element in all_data:
            if retention_number in element:
                return True
            return False

    def _do_new_record(self, control, inv_browse):
        invoice = [i for i in inv_browse if i.nro_ctrl == control][0]
        amount = (invoice.amount_tax * invoice.p_ret) / 100
        rp_obj = self.env['res.partner']
        rp_brw = rp_obj._find_accounting_partner(invoice.partner_id).id,
        return (invoice.date_invoice,
                invoice.date_document,
                rp_brw.vat,
                rp_brw.id,
                invoice.number,
                invoice.nro_ctrl,
                amount,
                rp_brw.name)

    @api.multi
    def _do_sale_report(self, cr, uid, data, context=None):
        """
        This method generates the SENIAT sales book report
        """
        #data_list, inv_rd, control_numbers, inv_browse = self._get_needed_data(
        #    cr, uid, data, context)
        data_list, inv_rd, control_numbers = self._get_needed_data(data)
        inv_numbers = [int(n.number) for n in inv_rd]
        missing_numbers = self._get_missing_inv_numbers(control_numbers, inv_numbers)
        for number in missing_numbers:
            inv_rd.append({'number': str(number)})
        for inv in inv_rd:
            if inv.date_document:
                if self._same_account_period(inv.date_document,inv.date_invoice):
                    if inv.nro_ctrl and not self._check_retention(data_list, inv.nro_ctrl):
                        data_list.append(self._do_new_record(inv.nro_ctrl, inv_rd))
                else:
                    if inv.nro_ctrl:
                        data_list.append(self._do_new_record(inv.nro_ctrl, inv_rd))
        data_list = self._date_sort(data_list)
        return False

    # sorting by bubblesort because quicksort exceeds recursion limit
    def _date_sort(self, data):
        _sorted = False
        while not _sorted:
            for cont in range(0, len(data) - 1):
                _sorted = True
                if data[cont][1] > data[cont + 1][1]:
                    _sorted = False
                    data[cont], data[cont + 1] = (
                        data[cont + 1], data[cont])  # swap
            if _sorted is True:
                break
        return data

    def do_report(self, ids):
        my_data = self.browse(ids)[0]
        if my_data[0].type == 'sale':
            self._do_sale_report(my_data)
        else:
            self._do_purchase_report(my_data)
        return False

    @api.model
    def default_get(self, field_list):
        # NOTE. use argument name field_list instead of fields to fix the
        # pylint error W0621 Redefining name 'fields' from outer scope.

        fiscal_book_obj = self.env['fiscal.book']
        fiscal_book = fiscal_book_obj.browse(self._context['active_id'])
        res = super(FiscalBookWizard, self).default_get(field_list)
        local_period = fiscal_book_obj.get_time_period(fiscal_book.time_period, fiscal_book)
        res.update({'type': fiscal_book.type})
        res.update({'date_start': local_period.get('dt_from', '')})
        res.update({'date_end': local_period.get('dt_to', '')})
        if fiscal_book.fortnight == 'first':
            date_obj = local_period.get('dt_to', '').split('-')
            res.update({'date_end': "%0004d-%02d-15" % (int(date_obj[0]), int(date_obj[1]))})
        elif fiscal_book.fortnight == 'second':
            date_obj = local_period.get('dt_to', '').split('-')
            res.update({'date_start': "%0004d-%02d-16" % (int(date_obj[0]), int(date_obj[1]))})
        return res

    def check_report(self, data):
        if data['type'] == 'purchase':
            if self.date_start and self.date_end:
                fecha_inicio = self.date_start
                fecha_fin = self.date_end
                book_id = data['active_id']

                purchase_book_obj = self.env['account.invoice']
                purchase_book_ids = purchase_book_obj.search(
                    [('date_invoice', '>=', fecha_inicio), ('date_invoice', '<=', fecha_fin)])
                if purchase_book_ids:
                    ids = []
                    for id in purchase_book_ids:
                        ids.append(id.id)
                    datas = self.read(self.ids)[0]
                    data = {
                        'ids': ids,
                        'model': 'report.l10n_ve_fiscal_book.report_fiscal_purchase_book',
                        'form': {
                            'datas': datas,
                            'date_from': self.date_start,
                            'date_to': self.date_end,
                            'book_id': book_id,
                        },
                        'context': self._context
                    }
                    return self.env.ref('l10n_ve_fiscal_book.report_purchase_book').report_action(self, data=data, config=False)
                else:
                    raise ValidationError('Advertencia! No existen facturas entre las fechas seleccionadas')
        else:
            if self.date_start and self.date_end:
                fecha_inicio = self.date_start
                fecha_fin = self.date_end
                book_id = data['active_id']

                purchase_book_obj = self.env['account.invoice']
                purchase_book_ids = purchase_book_obj.search(
                    [('date_invoice', '>=', fecha_inicio), ('date_invoice', '<=', fecha_fin)])
                if purchase_book_ids:
                    ids = []
                    for id in purchase_book_ids:
                        ids.append(id.id)
                    datas = self.read(self.ids)[0]
                    data = {
                        'ids': ids,
                        'model': 'report.l10n_ve_fiscal_book.report_fiscal_sale_book',
                        'form': {
                            'datas': datas,
                            'date_from': self.date_start,
                            'date_to': self.date_end,
                            'book_id': book_id,
                        },
                        'context': self._context
                    }
                    return self.env.ref('l10n_ve_fiscal_book.report_sale_book').report_action(self, data=data, config=False)
                else:
                    raise ValidationError('Advertencia! No existen facturas entre las fechas seleccionadas')


    date_start = fields.Date("Start Date", required=True, default=time.strftime('%Y-%m-%d'))
    date_end = fields.Date("End Date", required=True, default=time.strftime('%Y-%m-%d'))
    control_start = fields.Integer("Control Start")
    control_end = fields.Integer("Control End")
    type = fields.Selection(TYPE, "Type", required=True)

class PurchaseBook(models.AbstractModel):

    _name = 'report.l10n_ve_fiscal_book.report_fiscal_purchase_book'

    @api.model
    def get_report_values(self, docids, data=None):



        date_start = datetime.strptime(data['form']['date_from'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_to'], DATE_FORMAT)
        datos_compras = []
        purchasebook_ids = self.env['fiscal.book.line'].search(
            [('fb_id','=',data['form']['book_id']), ('emission_date', '>=', date_start.strftime(DATETIME_FORMAT)), ('emission_date', '<=', date_end.strftime(DATETIME_FORMAT))])

        sum_compras_credit = 0
        sum_total_with_iva = 0
        sum_vat_general_base = 0
        sum_vat_general_tax = 0
        sum_vat_reduced_base = 0
        sum_vat_reduced_tax = 0
        sum_vat_additional_base = 0
        sum_vat_additional_tax = 0
        sum_get_wh_vat = 0

        compras_credit = 0
        origin = 0
        number = 0

        for h in purchasebook_ids:

            if h.type == 'ntp':
                compras_credit = h.invoice_id.amount_untaxed

            if h.doc_type == 'N/DB':
                origin = h.invoice_id.origin
                number = h.invoice_id.number

            sum_compras_credit += compras_credit
            sum_total_with_iva += h.total_with_iva
            sum_vat_general_base += h.vat_general_base
            sum_vat_general_tax += h.vat_general_tax
            sum_vat_reduced_base += h.vat_reduced_base
            sum_vat_reduced_tax += h.vat_reduced_tax
            sum_vat_additional_base += h.vat_additional_base
            sum_vat_additional_tax += h.vat_additional_tax
            sum_get_wh_vat += h.get_wh_vat

            datos_compras.append({

                'emission_date': h.emission_date,
                'partner_vat': h.partner_vat,
                'partner_name': h.partner_name,
                'wh_number': h.wh_number,
                'invoice_number': h.invoice_number,
                'ctrl_number': h.ctrl_number,
                'debit_affected': h.debit_affected,
                'credit_affected': h.credit_affected,
                'type': h.void_form,
                'doc_type': h.doc_type,
                'origin': origin,
                'number': number,
                'total_with_iva': h.total_with_iva,
                'compras_credit': compras_credit,
                'vat_general_base': h.vat_general_base,
                'vat_general_rate':int(h.vat_general_base and h.vat_general_tax * 100 / h.vat_general_base),
                'vat_general_tax': h.vat_general_tax,
                'vat_reduced_base': h.vat_reduced_base,
                'vat_reduced_rate': int(h.vat_reduced_base and h.vat_reduced_tax * 100 / h.vat_reduced_base),
                'vat_reduced_tax': h.vat_reduced_tax,
                'vat_additional_base': h.vat_additional_base,
                'vat_additional_rate': int(h.vat_additional_base and h.vat_additional_tax * 100 / h.vat_additional_base),
                'vat_additional_tax': h.vat_additional_tax,
                'get_wh_vat': h.get_wh_vat,
            })

        sum_ali_gene_addi = sum_vat_general_base + sum_vat_additional_base
        sum_ali_gene_addi_credit = sum_vat_general_tax + sum_vat_additional_tax
        total_compras_base_imponible = sum_vat_general_base + sum_ali_gene_addi + sum_vat_reduced_base
        total_compras_credit_fiscal = sum_vat_general_tax + sum_ali_gene_addi_credit + sum_vat_reduced_tax


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': date_end.strftime(DATE_FORMAT),
            'a': 0.00,
            'datos_compras': datos_compras,
            'sum_compras_credit': sum_compras_credit,
            'sum_total_with_iva': sum_total_with_iva,
            'sum_vat_general_base' : sum_vat_general_base,
            'sum_vat_general_tax': sum_vat_general_tax,
            'sum_vat_reduced_base': sum_vat_reduced_base,
            'sum_vat_reduced_tax': sum_vat_reduced_tax,
            'sum_vat_additional_base': sum_vat_additional_base,
            'sum_vat_additional_tax': sum_vat_additional_tax,
            'sum_get_wh_vat': sum_get_wh_vat,
            'sum_ali_gene_addi': sum_ali_gene_addi,
            'sum_ali_gene_addi_credit': sum_ali_gene_addi_credit,
            'total_compras_base_imponible': total_compras_base_imponible,
            'total_compras_credit_fiscal': total_compras_credit_fiscal,

        }

class FiscalBookSaleReport(models.AbstractModel):
    _name = 'report.l10n_ve_fiscal_book.report_fiscal_sale_book'

    @api.model
    def get_report_values(self, docids, data=None):


        date_start = datetime.strptime(data['form']['date_from'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_to'], DATE_FORMAT)
        fbl_obj = self.env['fiscal.book.line'].search(
            [('fb_id','=',data['form']['book_id']),
             ('emission_date', '>=', date_start.strftime(DATETIME_FORMAT)),
             ('emission_date', '<=', date_end.strftime(DATETIME_FORMAT))])

        docs = []
        suma_total_w_iva = 0
        suma_no_taxe_sale = 0
        suma_vat_general_base = 0
        suma_vat_general_tax = 0
        suma_vat_reduced_base = 0
        suma_vat_reduced_tax = 0
        suma_vat_additional_base = 0
        suma_vat_additional_tax = 0
        suma_get_wh_vat = 0
        suma_ali_gene_addi = 0
        suma_ali_gene_addi_debit = 0
        total_ventas_base_imponible = 0
        total_ventas_debit_fiscal = 0

        suma_amount_tax = 0

        for line in fbl_obj:
            if line.type == 'ntp':
                no_taxe_sale = line.vat_general_base
            else:
                no_taxe_sale = 0.0

            docs.append({
                'rannk': line.rank,
                'emission_date': line.emission_date,
                'partner_vat': line.partner_vat,
                'partner_name': line.partner_name,
                'export_form': '',
                'wh_number': line.wh_number,
                'invoice_number': line.invoice_number if line.doc_type == 'FACT' else '',
                'ctrl_number': line.ctrl_number,
                'debit_note': '',
                'credit_note': line.wh_number if line.doc_type == 'N/CR' else '',
                'type': line.void_form,
                'affected_invoice': line.affected_invoice,
                'total_w_iva': line.total_with_iva,
                'no_taxe_sale': no_taxe_sale,
                'export_sale': '',
                'vat_general_base': line.vat_general_base,
                'vat_general_rate': int(line.vat_general_base and line.vat_general_tax * 100 / line.vat_general_base),
                'vat_general_tax': line.vat_general_tax,
                'vat_reduced_base': line.vat_reduced_base,
                'vat_reduced_rate': int(line.vat_reduced_base and line.vat_reduced_tax * 100 / line.vat_reduced_base),
                'vat_reduced_tax': line.vat_reduced_tax,
                'vat_additional_base': line.vat_additional_base,
                'vat_additional_rate': int(line.vat_additional_base and line.vat_additional_tax * 100 / line.vat_additional_base),
                'vat_additional_tax': line.vat_additional_tax,
                'get_wh_vat': line.get_wh_vat,
            })

            suma_total_w_iva += line.total_with_iva
            suma_no_taxe_sale += no_taxe_sale
            suma_vat_general_base += line.vat_general_base
            suma_vat_general_tax += line.vat_general_tax
            suma_vat_reduced_base += line.vat_reduced_base
            suma_vat_reduced_tax += line.vat_reduced_tax
            suma_vat_additional_base += line.vat_additional_base
            suma_vat_additional_tax += line.vat_additional_tax
            suma_get_wh_vat += line.get_wh_vat

            #RESUMEN LIBRO DE VENTAS
            suma_ali_gene_addi = suma_vat_general_base + suma_vat_additional_base
            suma_ali_gene_addi_debit = suma_vat_general_tax + suma_vat_additional_tax
            total_ventas_base_imponible = suma_vat_general_base + suma_ali_gene_addi + suma_vat_reduced_base
            total_ventas_debit_fiscal = suma_vat_general_tax + suma_ali_gene_addi_debit + suma_vat_reduced_tax


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start':date_start.strftime(DATE_FORMAT),
            'date_end': date_end.strftime(DATE_FORMAT),
            'docs': docs,
            'a': 0.00,
            'suma_total_w_iva': suma_total_w_iva,
            'suma_no_taxe_sale': suma_no_taxe_sale,
            'suma_vat_general_base': suma_vat_general_base,
            'suma_vat_general_tax': suma_vat_general_tax,
            'suma_vat_reduced_base': suma_vat_reduced_base,
            'suma_vat_reduced_tax': suma_vat_reduced_tax,
            'suma_vat_additional_base': suma_vat_additional_base,
            'suma_vat_additional_tax': suma_vat_additional_tax,
            'suma_get_wh_vat': suma_get_wh_vat,
            'suma_ali_gene_addi': suma_ali_gene_addi,
            'suma_ali_gene_addi_debit': suma_ali_gene_addi_debit,
            'total_ventas_base_imponible': total_ventas_base_imponible,
            'total_ventas_debit_fiscal': total_ventas_debit_fiscal,
        }


FiscalBookWizard()
