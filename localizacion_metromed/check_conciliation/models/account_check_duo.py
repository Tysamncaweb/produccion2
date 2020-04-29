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
# Cambios, rsosa:
#
# - Se agrega un campo booleano para controlar la visualizacion del campo Fecha de Debito (debit_date).
# - El campo 'debit_date' se comento en la clase original y se agrega de nuevo por esta via..
# - Se comenta el campo 'state' de la clase original y se incluye de nuevo aqui con un nuevo estado agregado
#
#
##############################################################################


from odoo import fields, models, api, _, exceptions
from datetime import datetime


class account_issued_check(models.Model):
    _name = 'account.issued.check'
    _inherit = 'account.issued.check'

    date = fields.Date('date', size=28)
    state = fields.Selection([('draft', 'Draft'),
                              ('holding', 'En cartera'),
                              ('handed', 'Handed'),
                              ('hrejected', 'Rechazado'),
                              ('payed', 'Pagado'),
                              ('anuled', 'Anulado'),
                              ('cancel', 'Cobrado')],
                             string='State')

    move_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    move_payed_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    move_hrejected_id = fields.Many2one('account.move', 'Asiento contable')
    asiento_conciliado = fields.One2many('account.move.line', related='move_id.line_ids', string='Asientos contables')
    asiento_conciliado_payed = fields.One2many('account.move.line', related='move_payed_id.line_ids', string='Asientos contables')
    asiento_conciliado_hrejected = fields.One2many('account.move.line', related='move_hrejected_id.line_ids',string='Asientos contables')


    @api.multi
    def action_conciliar_validate(self):
        for check in self:
            current_date = datetime.now().strftime('%Y-%m-%d')
            check.write({
                'state': 'holding',
                'change_date': current_date,
                'user_id': self.env.uid
            })

        issued_check_obj = self
        monto = issued_check_obj.amount
        cheq_obj = self.env['account.checkbook']
        cheq_brw = cheq_obj.browse(issued_check_obj.checkbook_id.id)
        journal_obj = self.env['account.issued.check']
        cuenta_trans = journal_obj.browse(issued_check_obj.cuenta_transitoria.id)
        journal_brw = journal_obj.browse(issued_check_obj.journal_id.id)
        partner_brw = journal_obj.browse(issued_check_obj.receiving_partner_id.id)
        account_bank_brw = journal_obj.browse(issued_check_obj.account_bank_id.id)
        name = self.env['ir.sequence'].get_id(issued_check_obj.journal_id.sequence_id.id)
        vals = {
            'date': issued_check_obj.date_check_emi,
            'ref': 'Cheque entregado Nro.  ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'journal_id': journal_brw.id,
            'company_id': self.receiving_partner_id.company_id.id,
            'partner_id': partner_brw.id,
            'name': name,
            'line_ids': False,
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)

        bus = self.env['account.move'].search([('ref', 'like', [self.number and self.checkbook_ids])])
        self.move_id = bus.id
        self.move_id = move_id

        asiento = {
            'account_id': cuenta_trans.id,
            'company_id': 1,
            'currency_id': False,
            'date_maturity': False,
            'ref': issued_check_obj.checkbook_ids + ' --Cheque entregado Nro.  ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'date': issued_check_obj.date_check_emi,
            'partner_id': partner_brw.id,
            'move_id': move_id.id,
            'name': '',
            'journal_id': journal_brw.id,
            'credit': monto,
            'debit': 0.0,
            'amount_currency': 0,
        }
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)

        return True


    @api.multi
    def action_conciliar_holding(self):
        for check in self:
            check.write({
                'state': 'handed',
            })
        move_brw = self.env['account.move']
        move_handed_brw = move_brw.browse(self.move_id.id)
        move_handed_brw.write({'state': 'posted', 'move_id': move_handed_brw.id})

        issued_check_obj = self
        monto = issued_check_obj.amount
        cheq_obj = self.env['account.checkbook']
        cheq_brw = cheq_obj.browse(issued_check_obj.checkbook_id.id)
        journal_obj = self.env['account.issued.check']
        journal_brw = journal_obj.browse(issued_check_obj.journal_id.id)
        partner_brw = journal_obj.browse(issued_check_obj.receiving_partner_id.id)
        account_bank_brw = journal_obj.browse(issued_check_obj.account_bank_id.account_id.id)
        name = self.env['ir.sequence'].get_id(issued_check_obj.journal_id.sequence_id.id)
        vals = {
            'date': issued_check_obj.date_check_emi,
            'ref': 'Cheque entregado Nro.  ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'journal_id': journal_brw.id,
            'company_id': self.receiving_partner_id.company_id.id,
            'partner_id': partner_brw.id,
            'name': name,
            'line_ids': False,
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)
        bus = self.env['account.move'].search([('ref', 'like', [self.number and self.checkbook_ids] ), ('id', '!=', self.move_id.id)])
        self.move_payed_id = bus.id
        self.move_payed_id = move_id
        asiento = {
            'account_id': account_bank_brw.id,
            'company_id': 1,
            'currency_id': False,
            'date_maturity': False,
            'ref':  issued_check_obj.checkbook_ids + ' --Cheque entregado Nro.  ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'date': issued_check_obj.date_check_emi,
            'partner_id': partner_brw.id,
            'move_id': move_id.id,
            'name': '',
            'journal_id': journal_brw.id,
            'credit': 0.0,
            'debit': monto,
            'amount_currency': 0,
        }
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)
        return True

    @api.multi
    def reversal_seats(self):
        issued_check_obj = self
        for check in self:
            check.write({
                'state': 'hrejected',
            })

        if not issued_check_obj.date_hrejected:
             raise exceptions.UserError(
                  _('Para rechazar el Cheque debe llenar el campo FECHA DE RECHAZO DEL CHEQUE '))
        else:
            if self.move_id.state == 'posted' and self.move_payed_id.state == 'draft':
                bus = self.env['account.move'].search([('id', '=', self.move_id.id)])
                reverse_ids = bus.reverse_moves(self.date, bus.journal_id)
                self.env['account.move'].search([('id', '=', self.move_payed_id.id)]).unlink()
                self.move_hrejected_id = reverse_ids[0]
                return True
            return False


    @api.multi
    def action_conciliar_payed(self):
        for check in self:
            check.write({
                'state': 'payed',
            })
        move_brw = self.env['account.move']
        move_handed_brw = move_brw.browse(self.move_payed_id.id)
        move_handed_brw.write({'state': 'posted', 'move_id': move_handed_brw.id})
        return True


class account_move(models.Model):
    _inherit = 'account.move'

    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        mlo = self.env['account.move.line'].search([('move_id', '=',self.ids[0])])
        if not mlo.reconcile:
            super(account_move, self).assert_balanced(fields)
        return True






class account_third_check(models.Model):
    _name = 'account.third.check'
    _inherit = 'account.third.check'

    date = fields.Date('Fecha de rechazo del cheque')
    state = fields.Selection((
        ('draft', 'Draft'),
        ('holding', 'Holding'),
        ('deposited', 'Deposited'),
        ('drejected', 'Dep-Rejected'),
        ('sold', 'Cobrado'),
    ), 'State', required=True, default='draft')

    move_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    move_payed_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    move_drejected_id = fields.Many2one('account.move', 'Asiento contable')
    asiento_conciliado = fields.One2many('account.move.line', related='move_id.line_ids', string='Asientos contables')
    asiento_conciliado_payed = fields.One2many('account.move.line', related='move_payed_id.line_ids',string='Asientos contables')
    asiento_conciliado_drejected = fields.One2many('account.move.line', related='move_drejected_id.line_ids',string='Asientos contables')


    @api.multi
    def action_conciliar_third_validate(self):
        issued_check_obj = self
        monto = issued_check_obj.amount
        journal_obj = self.env['account.third.check']
        journal_brw = journal_obj.browse(issued_check_obj.journal_id.id)
        partner_brw = journal_obj.browse(issued_check_obj.source_partner_id.id)
        cuenta_trans = journal_obj.browse(issued_check_obj.cuenta_transitoria.id)
        #name = self.env['ir.sequence'].get_id(issued_check_obj.sequence_id.id)
        vals = {
            'date': issued_check_obj.date_in,
            'ref': 'Cheque entregado Nro. ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'journal_id': 1 ,
            'company_id': self.source_partner_id.company_id.id,
            'partner_id': partner_brw.id,
            'name': 'Cheque de terceros Nro./' + issued_check_obj.number,
            'line_ids': False,
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)
        for check in self:
            current_date = datetime.now().strftime('%Y-%m-%d')
            check.write({
                'state': 'holding',
                'change_date': current_date,
                'user_id': self.env.uid,
            })
        self.move_id = move_id
        asiento = {
            'account_id': cuenta_trans.id,
            'company_id': 1,
            'currency_id': False,
            'date_maturity': False,
            'ref':  ' Cheque entregado Nro.  ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'date': issued_check_obj.date_in,
            'partner_id': issued_check_obj.source_partner_id.id,
            'move_id': move_id.id,
            'name': '',
            'journal_id': 1,
            'credit': 0.0,
            'debit': monto,
            'amount_currency': 0,
        }
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)

        return True



    @api.multi
    def action_conciliar_third_holding(self):
        for check in self:
            check.write({
                'state': 'deposited',
            })
        move_brw = self.env['account.move']
        move_handed_brw = move_brw.browse(self.move_id.id)
        move_handed_brw.write({'state': 'posted', 'move_id': move_handed_brw.id})

        # PARA CREAR UN NUEVO ASIENTO (solo con los datos principales) DESPUES DE VALIDAR EL ANTERIOR

        issued_check_obj = self
        monto = issued_check_obj.amount
        journal_obj = self.env['account.third.check']
        journal_brw = journal_obj.browse(issued_check_obj.journal_id.id)
        partner_brw = journal_obj.browse(issued_check_obj.source_partner_id.id)
        #name = self.env['ir.sequence'].get_id(issued_check_obj.journal_id.sequence_id.id)
        cuenta_trans = journal_obj.browse(issued_check_obj.cuenta_transitoria.id)
        vals = {
            'date': issued_check_obj.date_in,
            'ref': 'Cheque Cobrado Nro. ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'journal_id': 1,
            'company_id': self.source_partner_id.company_id.id,
            'partner_id': partner_brw.id,
            'name': 'Cheque de terceros Nro./' + issued_check_obj.number,
            'line_ids': False,
        }
        move_obj = self.env['account.move']
        move_id_holding = move_obj.create(vals)
        self.move_payed_id = move_id_holding
        asiento = {
            'account_id': cuenta_trans.id,
            'company_id': 1,
            'currency_id': False,
            'date_maturity': False,
            'ref':  ' Cheque entregado Nro.  ' + issued_check_obj.number + ' -- Monto: ' + str(monto),
            'date': issued_check_obj.date_in,
            'partner_id': issued_check_obj.source_partner_id.id,
            'move_id': move_id_holding.id,
            'name': '',
            'journal_id': 1,
            'credit': monto,
            'debit': 0.0,
            'amount_currency': 0,
        }
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)
        return True

    @api.multi
    def reversal_seats_third(self):
        third_check_obj = self
        for check in self:
            check.write({
                'state': 'drejected',
            })

        if not third_check_obj.date_drejected:
            raise exceptions.UserError(
                _('Para rechazar el Cheque debe llenar el campo FECHA DE RECHAZO DEL CHEQUE '))
        else:
            if self.move_id.state == 'posted' and self.move_payed_id.state == 'draft':
                bus = self.env['account.move'].search([('id', '=', self.move_id.id)])
                reverse_ids = bus.reverse_moves(self.date, bus.journal_id)
                self.env['account.move'].search([('id', '=', self.move_payed_id.id)]).unlink()
                self.move_drejected_id = reverse_ids[0]
                return True
        return False


    @api.multi
    def action_conciliar_third_payed(self):
        for check in self:
            check.write({
                'state': 'sold',
            })
        move_brw = self.env['account.move']
        move_handed_brw = move_brw.browse(self.move_payed_id.id)
        move_handed_brw.write({'state': 'posted', 'move_id': move_handed_brw.id})
        return True