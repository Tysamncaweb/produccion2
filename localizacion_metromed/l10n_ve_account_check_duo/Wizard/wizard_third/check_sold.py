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

from odoo import models, fields, exceptions, netsvc, api


class account_check_sold( models.TransientModel):
    _name = 'account.check.sold'


    sold_date = fields.Date('Sold Date', required=True)
    expense_account = fields.Many2one('account.account','Expense Account',required=True)
    expense_amount = fields.Float('Expense Amount')
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account',required=True)

    @api.one
    def action_sold(self):
        record_ids = self._context.get('active_ids', [])
        
        third_check = self.env['account.third.check']
        check_objs = third_check.browse(record_ids)

     #   wf_service = netsvc.LocalService('workflow')
        move_line = self.env['account.move.line']
       # wizard = self

     #   period_id = self.env['account.period'].find(wizard.sold_date)[0]

        for check in check_objs:
            if not (check.voucher_id.journal_id.default_credit_account_id.id or check.voucher_id.journal_id.default_debit_account_id.id):
                raise exceptions.except_orm('Journal %s selected error' % (check.voucher_id.journal_id.id),
                    'The journal must to be created defaults account for debit and credit.' )
                    
            if not self.bank_account_id.account_id.id:
                raise exceptions.except_orm(' %s selected error' % (self.bank_account_id.bank.name),
                    'The account must to be created in The Company Bank / Accounting Information.' )
                    
            if not check.amount > self.expense_amount:
                 raise exceptions.except_orm('Check %s selected error' % (check.number),
                    'The expense amount must to be minor than check amount.'
                     )
                
            if check.state != 'holding':
                raise exceptions.except_orm('Check %s selected error' % (check.number),
                    'The selected checks must to be in holding.'
                     )

            if  self.expense_amount != 0.00  \
            and self.expense_account:
                name = self.env['ir.sequence'].get_id(check.voucher_id.journal_id.sequence_id.id)
                move_id = self.env['account.move'].create({
                                                        'name': name,
                                                        'journal_id': check.voucher_id.journal_id.id,
                                                        'state': 'draft',
                                                     #   'period_id': period_id,
                                                        'date': self.sold_date,
                                                        'ref': 'Check Sold Nr. ' + check.number,
                        })
                #debit 
                move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': self.expense_account.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                        #    'period_id': period_id,
                            'date': self.sold_date,
                            'debit': self.expense_amount,
                            'credit': 0.0,
                            'ref': 'Check Sold Nr. ' + check.number,
                            'state': 'valid',
                        })
                #debit         
                move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': self.bank_account_id.account_id.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                         #   'period_id': period_id,
                            'date': self.sold_date,
                            'debit': check.amount - self.expense_amount,
                            'credit': 0.0,
                            'ref': 'Check Sold Nr. ' + check.number,
                            'state': 'valid',
                        })
                #credit 
                move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                            'move_id': move_id.id,
                            'journal_id': check.voucher_id.journal_id.id,
                            #'period_id': period_id,
                            'date': self.sold_date,
                            'debit': 0.0,
                            'credit':check.amount,
                            'ref': 'Check Sold Nr. ' + check.number,
                            'state': 'valid',
                        })
                move_id.write({
                            'state': 'posted',
                        })

            #    wf_service.trg_validate('account.third.check', check.id,
             #       'holding_sold')

            check.wkf_sold()
        return {}
