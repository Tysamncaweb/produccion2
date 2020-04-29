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

from odoo import fields, models, exceptions, netsvc, _, api
import logging
_logger = logging.getLogger(__name__)


class wizard_ticket_deposit(models.Model):
    _name = 'wizard.ticket.deposit'


    name = fields.Char('Ticket deposited number', size=30)
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account',required=True)
    date = fields.Date('Deposit Date',required=True)
    total_amount = fields.Float("Total Amount",readonly=True)
    ticket_deposit = fields.Many2one('ticket.deposit',string='Ticket Deposit')


    @api.multi
    def default_get(self):

        amount_total = 0.00
        one_time = True
        partnerid = {}
        values = super(wizard_ticket_deposit, self).default_get(self)
        third_check = self.env['account.third.check']

        if self._context is None:
            context = {}
        record_ids = self._context.get('active_ids', [])

        check_objs = third_check.browse(record_ids)

        for check in check_objs:
            if check.state == 'holding':
                amount_total += check.amount
            else:
                raise exceptions.except_orm('Check %s selected error' % (check.number),
                                     'The selected checks must to be in the holding.')

        values.update({'total_amount': amount_total})
        return values


    @api.multi
    def action_ticket_deposit(self):
        third_check_obj = self.env['account.third.check']

     #   wf_service = netsvc.LocalService('workflow')
        ticket_obj = self.env['ticket.deposit']
        ticket_line_obj = self.env['ticket.deposit.line']

        move_line = self.env['account.move.line']

        wizard = self.browse(self._cr,self._uid,self._ids[0])
        wizard_ids = [wizard.id]

      #  period_id = self.env['account.period'].find(self._cr,self._uid, wizard.date)[0]

        if self._context is None:
            context = {}
        record_ids = self._context.get('active_ids', [])

        check_ids = third_check_obj.browse(self._cr, self._uid, record_ids)

        for wizid in wizard_ids:
            pay = self.browse(self._cr,self._uid, wizid)

            # creo el ticket
            ticket_obj.create(self._cr, self._uid, {
                'name': pay.name,
                'bank_account_id': wizard.bank_account_id.id,
                'date': pay.date,
                'total_ammount': pay.total_amount,

            })

            # busco el id del receipt
            id_ticket_dep = ticket_obj.search(self._cr, self._uid, [('name', '=', pay.name)])

            for third_check in third_check_obj.browse(self._cr, self._uid, record_ids):
                third_check_obj.write(self._cr, self._uid, third_check.id, {
                    'ticket_deposit_id': id_ticket_dep[0],
                })

                ticket_line_obj.create(self._cr, self._uid, {
                    'ticket_deposit_id': id_ticket_dep[0],
                    'account_third_check_id': third_check.id,
                    'name': 'Activo',

                })

            id_receipt = ticket_obj.search(self._cr, self._uid, [('name', '=', pay.name)])

            self.write(self._cr, self._uid, wizid, {
                'ticket_deposit': id_receipt[0],
            })

        for check in check_ids:
            if not (
                check.voucher_id.journal_id.default_credit_account_id.id or check.voucher_id.journal_id.default_debit_account_id.id):
                raise exceptions.except_orm('Journal %s selected error' % (check.voucher_id.journal_id.id),
                                     'The journal must to be created defaults account for debit and credit.')

            if not wizard.bank_account_id.account_id.id:
                raise exceptions.except_orm(' %s selected error' % (wizard.bank_account_id.bank.name),
                                     'The account must to be created in The Company Bank / Accounting Information.')

            if check.state != 'holding':
                raise exceptions.except_orm('Check %s selected error' % (check.number),
                                     'The selected checks must to be in the holding.')

            else:
                name = self.env['ir.sequence'].get_id(self._cr, self._uid, check.voucher_id.journal_id.id)

                move_id = self.env['account.move'].create(self._cr, self._uid, {
                    'name': name,
                    'journal_id': check.voucher_id.journal_id.id,
                    'state': 'draft',
                    #'period_id': period_id,
                    'date': wizard.date,
                    'ref': 'Check Deposit Nr. ' + check.number,
                })

                move_line.create(self._cr, self._uid, {
                    'name': name,
                    'centralisation': 'normal',
                    'account_id': wizard.bank_account_id.account_id.id,
                    'move_id': move_id,
                    'journal_id': check.voucher_id.journal_id.id,
                   # 'period_id': period_id,
                    'date': check.date,
                    'debit': check.amount,
                    'credit': 0.0,
                    'ref': 'Check Deposit Nr. ' + check.number,
                    'state': 'valid',
                })
                move_line.create(self._cr, self._uid, {
                    'name': name,
                    'centralisation': 'normal',
                    'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                    'move_id': move_id,
                    'journal_id': check.voucher_id.journal_id.id,
                   # 'period_id': period_id,
                    'date': check.date,
                    'debit': 0.0,
                    'credit': check.amount,
                    'ref': 'Check Deposit Nr. ' + check.number,
                    'state': 'valid',
                })

                check.write({'account_bank_id': wizard.bank_account_id.id})
            #    wf_service.trg_validate(self._uid, 'account.third.check', check.id, 'holding_deposited', cr)
            self.env['account.move'].write(self._cr, self._uid, [move_id], {'state': 'posted',})

        return {}
wizard_ticket_deposit()
