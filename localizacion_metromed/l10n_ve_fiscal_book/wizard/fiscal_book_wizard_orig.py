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

class FiscalBookWizard(models.TransientModel):

    """
    Sales book wizard implemented using the osv_memory wizard system
    """
    _name = "fiscal.book.wizard"

    TYPE = [("sale", _("Sale")),
            ("purchase", _("Purchase")),
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
        fiscal_book_o = fiscal_book_obj.browse([('id', '=', self._context['active_id'])])
        res = super(FiscalBookWizard, self).default_get(field_list)
        res.update({'type': fiscal_book_o.type})
        res.update({'date_start':
                    fiscal_book_o.period_id and
                    fiscal_book_o.period_id.date_start or ''})
        res.update({'date_end':
                    fiscal_book_o.period_id and
                    fiscal_book_o.period_id.date_stop or ''})
        if fiscal_book_o.fortnight == 'first':
            date_obj = time.strptime(fiscal_book_o.period_id.date_stop, '%Y-%m-%d')
            res.update({'date_end': "%0004d-%02d-15" % (date_obj.tm_year, date_obj.tm_mon)})
        elif fiscal_book_o.fortnight == 'second':
            date_obj = time.strptime(fiscal_book_o.period_id.date_start, '%Y-%m-%d')
            res.update({'date_start': "%0004d-%02d-16" % (date_obj.tm_year, date_obj.tm_mon)})
        return res

    def check_report(self):
        data = {}
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        record = self.browse()[0]
        data['form'] = {'date_start': record.date_start, 'date_end':record.date_end,
                        'control_start':record.control_start, 'control_end':record.control_end,
                        'type':record.type}
        return self._print_report(data)

    def _print_report(self, data):
        if data['form']['type'] == 'sale':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'fiscal.book.sale', 'datas': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fiscal.book.purchase', 'datas': data}

    date_start = fields.Date("Start Date", required=True, default=time.strftime('%Y-%m-%d'))
    date_end = fields.Date("End Date", required=True, default=time.strftime('%Y-%m-%d'))
    control_start = fields.Integer("Control Start")
    control_end = fields.Integer("Control End")
    type = fields.Selection(TYPE, "Type", required=True)

FiscalBookWizard()
