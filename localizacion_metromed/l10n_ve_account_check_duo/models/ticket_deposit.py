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
from odoo import fields, models, _


class ticket_deposit(models.Model):
       
    _name = "ticket.deposit" 
    _description = 'Ticket Deposit'

    name = fields.Char(string='Ticket Deposit number',size=128, required=True, select=True, readonly=True, ondelete='set null')
    date = fields.Date('Ticket Deposit Date',readonly=True)
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account',required=True)
    total_ammount = fields.Float('Total Ammount',readonly=True)
    checks_ids = fields.One2many('account.third.check','ticket_deposit_id',string='Check Lines')

    _sql_constraints = [('name_uniq','unique(name)','The name must be unique!')]
    _order = "date"

class ticket_deposit_line (models.Model):
    
    _name = "ticket.deposit.line" 
    _description = 'Ticket Deposit Line'
    _order = "ticket_deposit_id"

    ticket_deposit_id = fields.Many2one('ticket.deposit', string='Ticket Deposit', ondelete='set null')
    name = fields.Char(string='Description', size=256)
    account_third_check_id = fields.Many2one('account.third.check', string='Thirds Checks')



