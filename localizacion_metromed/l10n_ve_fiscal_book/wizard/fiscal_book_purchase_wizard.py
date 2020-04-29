from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date, timedelta

from odoo.exceptions import ValidationError
import urllib
from odoo import http


class report_fiscal_book_purchase(models.Model):
    _name = "fiscal.purchase.book"
    _description = "Libro de Compras"

    date_from = fields.Date(string='Fecha Inicio')
    date_to = fields.Date(string='Fecha Fin')

    vat_general_rate = fields.Float(compute='_compute_vat_rates', method=True,
                                    string='General rate', multi='all', help="Vat general tax rate ")
    vat_additional_rate = fields.Float(compute='_compute_vat_rates', method=True,
                                       string='Additional rate', multi='all',
                                       help="Vat plus additional tax rate ")





    @api.model
    def default_get(self, field_list):
        # NOTE. use argument name field_list instead of fields to fix the
        # pylint error W0621 Redefining name 'fields' from outer scope.

        fiscal_book_obj = self.env['fiscal.book']
        fiscal_book = fiscal_book_obj.browse(self._context['active_id'])
        res = super(report_fiscal_book_purchase, self).default_get(field_list)
        local_period = fiscal_book_obj.get_time_period(fiscal_book.time_period, fiscal_book)
        res.update({'type': local_period.type})
        res.update({'date_from': local_period.get('dt_from', '')})
        res.update({'date_to': local_period.get('dt_to', '')})
        if fiscal_book.fortnight == 'first':
            date_obj = local_period.get('dt_to', '').split('-')
            res.update({'date_to': "%0004d-%02d-15" % (int(date_obj[0]), int(date_obj[1]))})
        elif fiscal_book.fortnight == 'second':
            date_obj = local_period.get('dt_to', '').split('-')
            res.update({'date_from': "%0004d-%02d-16" % (int(date_obj[0]), int(date_obj[1]))})
        return res

    @api.multi
    def purchase_book(self,data):
        if self.date_from and self.date_to:
            fecha_inicio = self.date_from
            fecha_fin = self.date_to

            purchase_book_obj = self.env['fiscal.book.line']
            purchase_book_ids = purchase_book_obj.search(
                [('emission_date', '>=', fecha_inicio), ('emission_date', '<=', fecha_fin)])
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
                                 'date_from': self.date_from,
                                 'date_to': self.date_to,
                             },
                             'context': self._context
                        }
                return self.env.ref('l10n_ve_fiscal_book.report_purchase_book').report_action(self, data=data, config=False)
            else:
                raise ValidationError('Advertencia! No existen facturas entre las fechas seleccionadas')

class PurchaseBook(models.AbstractModel):

    _name = 'report.l10n_ve_fiscal_book.report_fiscal_purchase_book'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = datetime.strptime(data['form']['date_from'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_to'], DATE_FORMAT)
        datos_compras = []
        purchasebook_ids = self.env['fiscal.book.line'].search(
            [('emission_date', '>=', date_start.strftime(DATETIME_FORMAT)), ('emission_date', '<=', date_end.strftime(DATETIME_FORMAT))])

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
                'vat_general_rate': int(h.vat_general_base and h.vat_general_tax * 100 / h.vat_general_base),
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