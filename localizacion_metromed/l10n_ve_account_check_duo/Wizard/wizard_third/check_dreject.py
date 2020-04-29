# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, api, models, _, exceptions


class account_check_dreject(models.TransientModel):
    _name = 'account.check.dreject'


    reject_date = fields.Date('Reject Date', required=True)
    expense_account = fields.Many2one('account.account','Expense Account')
    expense_amount = fields.Float('Expense Amount')
    invoice_expense = fields.Boolean('Invoice Expense?')
    make_expense = fields.Boolean('Make Expenses ?')


    @api.one
    def _get_address_invoice(self, partner_id):
        #partner_obj = self.env['res.partner']
        #return partner_obj.address_get([partner],['contact', 'invoice'])
        return self.env['res.partner'].browse(partner_id).address_get(['contact', 'invoice'])



    @api.one
    def action_dreject(self):

        record_ids = self._context.get('active_ids', [])
        third_check = self.env['account.third.check']
        check_objs = third_check.browse(record_ids)

        invoice_obj = self.env['account.invoice']
        move_line = self.env['account.move.line']
        invoice_line_obj = self.env['account.invoice.line']
        #wizard = self

      #  period = self.env['account.period'].find(wizard.reject_date)[0]

        for check in check_objs:
            if check.state != 'deposited':
                raise exceptions.except_orm('Check %s selected error' % (check.number),
                    'The selected checks must to be in deposited.')
                    
            if not (check.voucher_id.journal_id.default_credit_account_id.id or check.voucher_id.journal_id.default_debit_account_id.id):
                raise exceptions.except_orm('Journal %s selected error' % (check.voucher_id.journal_id.id),
                    'The journal must to be created defaults account for debit and credit.' )

            partner_address = self._get_address_invoice(check.voucher_id.partner_id.id)
            contact_address = partner_address['contact']
            invoice_address = partner_address['invoice']
            invoice_vals = ({
                            'rif': check.voucher_id.partner_id.vat, 'partner_ref': check.voucher_id.partner_id.ref,
                            'name': check.number,
                            'origin': 'Check Rejected Dep Nr. ' + (check.number or '') + ',' + (check.voucher_id.name),
                            'type': 'out_invoice',
                            'account_id': check.voucher_id.partner_id.property_account_receivable_id.id,
                            'partner_id': check.voucher_id.partner_id.id,
                            'address_invoice_id': invoice_address,
                            'address_contact_id': contact_address,
                            'date_invoice': self.reject_date,
                        })

            invoice_id = invoice_obj.create(invoice_vals)
            
            #'account_id': check.voucher_id.journal_id.default_debit_account_id.id
            invoice_line_vals = {
                'name': 'Check Rejected Dep Nr. ' + check.number,
                'origin': 'Check Rejected Dep Nr. ' + check.number,
                'invoice_id': invoice_id.id,
                'account_id': check.account_bank_id.account_id.id,
                'price_unit': check.amount,
                'quantity': 1,
            }
            invoice_id.write({'invoice_line': [(0, 0, invoice_line_vals)]})
            #invoice_line_obj.create(invoice_line_vals)
            check.write({'reject_debit_note': invoice_id.id})

            if self.make_expense:
                if self.invoice_expense:
                    if  self.expense_amount != 0.00 and self.expense_account:
                        invoice_line_obj.create({
                            'name': 'Check Rejected Dep Expenses Nr. ' + check.number,
                            'origin': 'Check Rejected Dep Nr. ' + check.number,
                            'invoice_id': invoice_id.id,
                            'account_id': self.expense_account.id,
                            'price_unit': self.expense_amount,
                            'quantity': 1,
                        })
                    else:
                        raise exceptions.except_orm(_('Error'),
                            _('You must assign expense account and amount !'))

                else:
                    if  self.expense_amount != 0.00 \
                    and self.expense_account:
                        name = self.env['ir.sequence'].get_id(check.voucher_id.journal_id.sequence_id.id)
                        move_id = self.env['account.move'].create({
                            'name': name,
                            'journal_id': check.voucher_id.journal_id.id,
                            'state': 'draft',
                         #   'period': wizard.reject_date,
                            'date': self.reject_date,
                            'ref': 'Check Rejected Dep Nr. ' + check.number,
                        })  

                        move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': self.expense_account.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                         #   'period_id': period_id,
                            'date': self.reject_date,
                            'debit': self.expense_amount,
                            'credit': 0.0,
                            'ref': 'Check Dep Reject Nr. ' + check.number,
                            'state': 'valid',
                        })

                        move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                         #   'period_id': period_id,
                            'date': self.reject_date,
                            'debit': 0.0,
                            'credit': self.expense_amount,
                            'ref': 'Check Dep Reject Nr. ' + check.number,
                            'state': 'valid',
                        })
                        move_id.write({
                            'state': 'posted',
                        })

           # wf_service.trg_validate('account.third.check', check.id,
            #        'deposited_drejected')

            # AGREGADOOOOO#############################

           # self.signal_workflow('deposited_drejected')

            check.wkf_drejected()
        return {}

