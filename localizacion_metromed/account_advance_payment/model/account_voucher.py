# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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

from odoo import fields, models, api, exceptions, _

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    advance_account_id = fields.Many2one('account.account', 'Advance Account')

    @api.multi
    def writeoff_move_line_get(self, voucher_id, line_total, move_id,
                               name, company_currency, current_currency):
        move_line = super(AccountVoucher, self).writeoff_move_line_get( voucher_id, line_total, move_id, name, company_currency,
            current_currency)
        voucher = self.env['account.voucher'].browse(voucher_id)
        if (move_line and not voucher.payment_option == 'with_writeoff'
                and voucher.partner_id):
            if voucher.type in ('sale', 'receipt'):
                account_id = (
                    voucher.advance_account_id and
                    voucher.advance_account_id.id or
                    voucher.partner_id.property_account_customer_advance.id)
            else:
                account_id = (
                    voucher.advance_account_id and
                    voucher.advance_account_id.id or
                    voucher.partner_id.property_account_supplier_advance.id)
            if not account_id:
                title = _('Missing Configuration on Partner !')
                message = _('Please Fill Advance Accounts on Partner !')
                raise exceptions.except_orm(title, message)
            move_line['account_id'] = account_id
        return move_line

    @api.onchange('partner_id', 'pay_now')
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount,
                            currency_id, ttype, date, context=None):
        res = super(AccountVoucher, self).onchange_partner_id(
            cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype,
            date, context=context)
        context = context or {}
        if not partner_id:
            return res
        partner_pool = self.pool.get('res.partner')
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        advance_account_id = False
        if ttype in ('sale', 'receipt'):
            advance_account_id = (
                partner.property_account_customer_advance and
                partner.property_account_customer_advance.id or False)
        else:
            advance_account_id = (
                partner.property_account_supplier_advance and
                partner.property_account_supplier_advance.id or False)
        if len(res) == 0:
            return res
        res['value']['advance_account_id'] = advance_account_id
        return res
