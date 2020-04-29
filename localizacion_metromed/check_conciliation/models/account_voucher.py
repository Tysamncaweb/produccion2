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
#    Cambios, rsosa:
#
#    - Se sobreescribe el metodo 'first_move_line_get' para incluir el ID de la
#      cuenta transitoria de Banco a la hora de realizar un pago con cheque
#
##############################################################################

from odoo import fields, models, api, exceptions

class account_payment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):

        voucher = self
        debit = credit = 0.0
        transitoria_id = None
        
        if voucher.type in ('purchase', 'payment'):
            credit = voucher.paid_amount_in_company_currency

            chequera_id = 0

            if voucher.issued_check_ids:
                for check in voucher.issued_check_ids:
                    chequera_id = check.checkbook_id.id
                chequera_obj = self.env['account.checkbook'].browse(chequera_id)
                if chequera_obj: transitoria_id = chequera_obj.cuenta_transitoria.id
        elif voucher.type in ('sale', 'receipt'):
            debit = voucher.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': voucher.name or '/',
                'debit': debit,
                'credit': credit,
                #'account_id': voucher.account_id.id,
                'move_id': move_id,
                'journal_id': voucher.journal_id,
               # 'period_id': voucher.period_id.id,
                'partner_id': voucher.partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': company_currency != current_currency and sign * voucher.amount or 0.0,
                'date': voucher.date,
                'date_maturity': voucher.date_due
            }
        # si se obtiene la cuenta transitoria, se agrega ese ID al diccionario, de lo contrario se agrega el ID de la cuenta por defecto.
        if transitoria_id:
            move_line.update({'account_id': transitoria_id})
        else:
            move_line.update({'account_id': voucher.account_id.id})
        return move_line

    def action_validate_invoice_payment(self):
        move = super(account_payment, self).action_validate_invoice_payment()
        if move:
            for ch in self.issued_check_ids:
                ch.write({'state':'handed'})
            for ch in self.third_check_ids:
                ch.write({'state': 'holding',
                          'voucher_id':self._ids})
            #self.env['account.issued.check']
        return move


   # def action_validate_invoice_payment(self):
   #     move = super(account_payment, self).action_validate_invoice_payment()
   #     if move:
   #         for ch in self.third_check_ids:
   #             ch.write({'state':'handed'})
   #         #self.env['account.issued.check']
   #     return move