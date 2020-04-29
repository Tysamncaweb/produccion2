# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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

import time

from odoo import api,fields,models
from odoo.fields import _
from odoo.osv import osv
#from odoo.tools.translate import _

from odoo.tools import float_compare

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def test_retenida(self, *args):
        """ Verify if this invoice is withhold
        """
        type2journal = {'out_invoice': 'iva_sale',
                        'in_invoice': 'iva_purchase', 'out_refund': 'iva_sale',
                        'in_refund': 'iva_purchase'}
        type_inv = self.browse(self.ids).type
        type_journal = type2journal.get(type_inv, 'iva_purchase')
        res = self.ret_payment_get(self.ids)
        if not res:
            return False
        ok = True

        self.cr.execute('select l.id '
                   'from account_move_line l '
                   'inner join account_journal j on (j.id=l.journal_id)'
                   ' where l.id in (' + ','.join(
            [str(item) for item in res]) + ') and j.type=' +
                   '\'' + type_journal + '\'')
        ok = ok and bool(self.cr.fetchone())
        return ok

    def _get_move_lines(self, to_wh,
                        pay_journal_id, writeoff_acc_id,
                        writeoff_journal_id, date, name
                        ):
        """ Function openerp is rewritten for adaptation in
        the ovl
        """
        return []

    def ret_and_reconcile(self, pay_amount, pay_account_id,
                          pay_journal_id, writeoff_acc_id,
                          writeoff_journal_id, date,
                          name, to_wh, writeoff_period_id=None):
        """ Make the payment of the invoice
        """

        rp_obj = self.env['res.partner']

        # TODO check if we can use different period for payment and the
        # writeoff line
        assert len(self.ids) == 1, "Can only pay one invoice at a time"
        invoice = self.browse(self.ids)
        src_account_id = invoice.account_id.id

        # Take the seq as name for move
        types = {'out_invoice': -1,
                 'in_invoice': 1,
                 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
        l1 = {
            'debit': direction * pay_amount > 0 and direction * pay_amount,
            'credit': direction * pay_amount < 0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': rp_obj._find_accounting_partner(
                invoice.partner_id).id,
            'ref': invoice.number,
            'date': date,
            'currency_id': False,
            'name': name
        }
        lines = [(0, 0, l1)]

        l2 = self._get_move_lines(to_wh, pay_journal_id, writeoff_acc_id,
                                  writeoff_journal_id, date, name)

        # TODO: check the method _get_move_lines that is forced to return []
        # and that makes that aws_customer.yml test cause a error
        if not l2:
            raise osv.except_osv(
                _('Warning !'),
                _('No accounting moves were created.\n Please, Check if there'
                  ' are Taxes/Concepts to withhold in the Invoices!'))
        # rsosa: ID 57
        deb = l2[0][2]['debit']
        cred = l2[0][2]['credit']
        if deb < 0: l2[0][2].update({'debit': deb * direction})
        if cred < 0: l2[0][2].update({'credit': cred * direction})
        #for line in l2:
        #    if deb < 0: line[2].update({'debit': deb * direction})
        #    if cred < 0: line[2].update({'credit': cred * direction})
        lines += l2

        move = {'ref': invoice.number,
                'line_ids': lines,
                'journal_id': pay_journal_id,
                'date': date,
                'state': 'draft'
                }

        move_obj = self.env['account.move']
        move_id = move_obj.create(move)
        #move_id.post()
        #PARA FORZAR LA CULMINACION DE UNA TRANSACCION DE BASE DE DATOS
        #self.env.cr.commit()

        return move_id

        #self.env['account.move'].post(move)


        line_ids = []
        total = 0.0
        line = self.env['account.move.line']
        self._cr.execute(
            'select id'
            ' from account_move_line'
            ' where move_id in (' + str(move_id.id) + ',' +
            str(invoice.move_id.id) + ')')
        lines = line.browse( [item[0] for item in self._cr.fetchall()])
        for aml_brw in lines:
            if aml_brw.account_id.id == src_account_id:
                line_ids.append(aml_brw.id)
                total += (aml_brw.debit or 0.0) - (aml_brw.credit or 0.0)
        for aml_brw in invoice.payment_ids:
            if aml_brw.account_id.id == src_account_id:
                line_ids.append(aml_brw.id)
                total += (aml_brw.debit or 0.0) - (aml_brw.credit or 0.0)
        if (not round(total, self.env['decimal.precision'].precision_get(
                 'Withhold'))) or writeoff_acc_id:
            self.env['account.move.line'].reconcile(
                 line_ids, 'manual', writeoff_acc_id,
                writeoff_period_id, writeoff_journal_id)
        #TODO REVISAR METODO RECONCILE_PARTIAL EN VERSION 8. ESTE METODO NO EXISTE EN VERSION 11
        #else:
        #    self.env['account.move.line'].reconcile_partial(
        #         line_ids, 'manual', self.context)

        # Update the stored value (fields.function), so we write to trigger
        # recompute
        self.env['account.invoice'].write({})
        self.move_id = move_id

    def ret_payment_get(self,*args):
        """ Return payments associated with this bill
        """
        # /!\ This method need revision and I (hbto) have come to believe it is
        # useless at worst, at best it needs to be refactored, to get payments
        # from invoice one just need to look at the payment_ids field

        lines = []
        #for invoice in self.browse(self.ids):
            #moves = self.move_line_id_payment_get([invoice.id])
        #    src = []
        #    for aml_brw in self.env('account.move.line').browse(moves):
        #        temp_lines = []  # Added temp list to avoid duplicate records
        #        if aml_brw.reconcile_id:
        #            temp_lines = [i.id for i in aml_brw.reconcile_id.line_id]
        #        elif aml_brw.reconcile_partial_id:
        #            temp_lines = [
        #                i.id
        #                for i in aml_brw.reconcile_partial_id.line_partial_ids]#

#                lines = list(set(temp_lines))
#                src.append(aml_brw.id)

            #lines += [item for item in lines if item not in src]
        return lines

    @api.multi
    def check_tax_lines(self, compute_taxes):
        """ Check if no tax lines are created. If
        existing tax lines, there are checks on the invoice
        and match the tax base.
        """
        assert len(self) == 1, "Can only check one invoice at a time."
        account_invoice_tax = self.env['account.invoice.tax']
        company_currency = self.company_id.currency_id
        if not self.tax_line:
            for tax in compute_taxes.values():
                account_invoice_tax.create(tax)
        else:
            tax_key = []
            precision = self.env['decimal.precision'].precision_get('Account')
            for tax in self.tax_line:
                if tax.manual:
                    continue
                # Comment the following line from original method
                # key = (tax.tax_code_id.id, tax.base_code_id.id,
                # tax.account_id.id)

                # Group by tax id (now use this key)
                key = (tax.tax_id.id)
                tax_key.append(key)
                if key not in compute_taxes:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('Global taxes defined, but they are not in invoice'
                          ' lines !'))
                base = compute_taxes[key]['base']
                if float_compare(abs(base - tax.base),
                                 company_currency.rounding,
                                 precision_digits=precision) == 1:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('Tax base different!\nClick on compute to update'
                          ' the tax base.'))
                # for key in compute_taxes:
                if key not in tax_key:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('Taxes are missing!\nClick on compute button.'))


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    tax_id = fields.Many2one(
            'account.tax', 'Tax', required=False, ondelete='set null',
            help="Tax relation to original tax, to be able to take off all"
                 " data from invoices.")


    @api.model
    def compute(self, invoice):
        """ Calculate the amount, base, tax amount,
        base amount of the invoice
        """

        tax_grouped = {}
        if isinstance(invoice, (int)):
            inv = self.env['account.invoice'].browse(invoice)
        else:
            inv = invoice
        currency = inv.currency_id.with_context(
            date=inv.date_invoice or time.strftime('%Y-%m-%d'))
        company_currency = inv.company_id.currency_id
        for line in inv.invoice_line:
            for tax in line.invoice_line_tax_id.compute_all(
                    (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                    line.quantity, line.product_id, inv.partner_id)['taxes']:
                val = {}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['quantity']
                # add tax id #
                val['tax_id'] = tax['id']

                if inv.type in ('out_invoice', 'in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(
                        val['base'] * tax['base_sign'], company_currency,
                        round=False)
                    val['tax_amount'] = currency.compute(
                        val['amount'] * tax['tax_sign'], company_currency,
                        round=False)
                    val['account_id'] = tax['account_collected_id'] or \
                                        line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(
                        val['base'] * tax['ref_base_sign'], company_currency,
                        round=False)
                    val['tax_amount'] = currency.compute(
                        val['amount'] * tax['ref_tax_sign'], company_currency,
                        round=False)
                    val['account_id'] = tax['account_paid_id'] or \
                                        line.account_id.id

                # key = (val['tax_code_id'], val['base_code_id'],
                #                       val['account_id'])
                # group by tax id #
                key = (val['tax_id'])
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for tax in tax_grouped.values():
            tax['base'] = currency.round(tax['base'])
            tax['amount'] = currency.round(tax['amount'])
            tax['base_amount'] = currency.round(tax['base_amount'])
            tax['tax_amount'] = currency.round(tax['tax_amount'])
        return tax_grouped