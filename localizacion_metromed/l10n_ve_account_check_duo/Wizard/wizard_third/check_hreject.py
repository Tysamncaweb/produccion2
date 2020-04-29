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

from odoo import models, fields, _, netsvc, exceptions, api

import logging

_logger = logging.getLogger(__name__)


class account_check_hreject(models.TransientModel):
    _name = 'account.check.hreject'


    reject_date = fields.Date('Reject Date', required=True)
    expense_account = fields.Many2one('account.account','Expense Account')
    expense_amount = fields.Float('Expense Amount')
    invoice_expense = fields.Boolean('Invoice Expense?')
    make_expense = fields.Boolean('Make Expenses ?', default=False)


    @api.multi
    def _get_address_invoice(self, partner):
         #partner_obj = self.env['res.partner']
         #return partner_obj.address_get([partner],['contact', 'invoice'])
         return self.env['res.partner'].browse(partner).address_get(['contact', 'invoice'])


    @api.one
    def action_hreject(self):
        record_ids = self._context.get('active_ids', [])

        third_check = self.env['account.third.check']
        check_objs = third_check.browse(record_ids)


      #  wf_service = netsvc.LocalService('workflow')
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        invoice_obj_prov = self.env['account.invoice']
        invoice_line_obj_prov = self.env['account.invoice.line']
        move_line = self.env['account.move.line']

        #wizard = self

      #  period_id = self.env['account.period'].find(wizard.reject_date)[0]

        for check in check_objs:
            if check.state != 'holding':
                raise exceptions.except_orm('Check %s selected error' % (check.number),
                    'The selected checks must to be in holding.'
                     )
                     
            if not (check.voucher_id.journal_id.default_credit_account_id.id or check.voucher_id.journal_id.default_debit_account_id.id):
                raise exceptions.except_orm('Journal %s selected error' % (check.voucher_id.journal_id.id),
                    'The journal must to be created defaults account for debit and credit.' )
                    
                             
            #client      
            partner_address = self._get_address_invoice(check.voucher_id.partner_id.id)
            contact_address = partner_address['contact']
            invoice_address = partner_address['invoice']
            invoice_vals = {
                            'name': check.number,
                            'origin': 'Check Rejected Hand Nr. ' + (check.number or '') + ',' + (check.voucher_id.name),
                            'type': 'out_invoice',
                            'account_id': check.voucher_id.partner_id.property_account_receivable_id.id,
                            'partner_id': check.voucher_id.partner_id.id,
                             'address_invoice_id': invoice_address,
                             'address_contact_id': contact_address,
                            'date_invoice': self.reject_date,
                        }

            invoice_id = invoice_obj.create(invoice_vals)
            
            invoice_line_vals = {
                'name': 'Check Rejected Hand Nr. ' + check.number,
                'origin': 'Check Rejected Hand Nr. ' + check.number,
                'invoice_id': invoice_id.id,
                'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                'price_unit': check.amount,
                'quantity': 1,
            }
            invoice_line_obj.create(invoice_line_vals)
            check.write({'reject_debit_note': invoice_id.id})
            
            #proveedor         
            #partner_address = self._get_address_invoice(check.voucher_id.partner_id.id)

            partner_address = self._get_address_invoice(check.destiny_partner_id)
            contact_address = partner_address['contact']
            invoice_address = partner_address['invoice']
            invoice_vals_prov = {
                            'name': check.number,
                            'origin': 'Check Rejected Hand Nr. ' + (check.number or '') + ',' + (check.voucher_id.name),
                            'type': 'in_invoice',
                            'account_id': check.voucher_id.partner_id.property_account_receivable_id.id,
                            'partner_id': check.destiny_partner_id,
                            'address_invoice_id': invoice_address,
                            'address_contact_id': contact_address,
                            'date_invoice': self.reject_date,
                        }

            invoice_id_prov = invoice_obj_prov.create(invoice_vals_prov)
            
            invoice_line_vals_prov = {
                'name': 'Check Rejected Hand Nr. ' + check.number,
                'origin': 'Check Rejected Hand Nr. ' + check.number,
                #'invoice_id': invoice_id_prov.id,
                'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                'price_unit': check.amount,
                'quantity': 1,
            }
            invoice_line_obj_prov.create(invoice_line_vals_prov)
            check.write({'reject_debit_note_prov': invoice_id_prov.id})
            

            if self.make_expense:
                if self.invoice_expense:
                    if  self.expense_amount != 0.00 and self.expense_account:
                        #cliente
                        invoice_line_obj.create({
                            'name': 'Check Rejected Hand Expenses Nr. ' + check.number,
                            'origin':'Check Rejected Hand Nr. ' + check.number,
                            'invoice_id': invoice_id.id,
                            'account_id': self.expense_account.id,
                            'price_unit': self.expense_amount,
                            'quantity': 1,
                        })
                        #proveedor
                        invoice_line_obj.create({
                            'name': 'Check Rejected Hand Expenses Nr. ' + check.number,
                            'origin':'Check Rejected Hand Nr. ' + check.number,
                           # 'invoice_id': invoice_id_prov.id,
                            'account_id': self.expense_account.id,
                            'price_unit': self.expense_amount,
                            'quantity': 1,
                        })
                        
                    else:
                        raise exceptions.except_orm(_('Error'),_('You must assign expense account and amount !'))

                else:
                    if  self.expense_amount != 0.00 \
                    and self.expense_account:
                        name = self.env['ir.sequence'].next_by_id(check.voucher_id.journal_id.sequence_id.id)
                        move_id = self.env['account.move'].create({
                            'name': name,
                            'journal_id': check.voucher_id.journal_id.id,
                            'state': 'draft',
                          #  'period_id': period_id,
                            'date': self.reject_date,
                            'ref': 'Check Rejected Hand Nr. ' + check.number,
                        })

                        move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': self.expense_account.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                          #  'period_id': period_id,
                            'date': self.reject_date,
                            'debit': self.expense_amount,
                            'credit': 0.0,
                            'ref': 'Check Rejected Hand Nr. ' + check.number,
                            'state': 'valid',
                        })

                        move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                           # 'period_id': period_id,
                            'date': self.reject_date,
                            'debit': 0.0,
                            'credit': self.expense_amount,
                            'ref': 'Check Rejected Hand Nr. ' + check.number,
                            'state': 'valid',
                        })
                        move_id.write({
                            'state': 'posted',
                        })

           # wf_service.trg_validate(self.env.uid, 'account.third.check', check.id, 'handed_hrejected', self.env.cr)

            check.wkf_hrejected()
        return {}

