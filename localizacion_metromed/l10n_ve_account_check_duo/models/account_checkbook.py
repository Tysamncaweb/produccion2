# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Venezuela.
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


import logging
import time
_logger = logging.getLogger(__name__)
from odoo import models, fields, api,exceptions, _
import re

class account_checkbook(models.Model):

    _name = 'account.checkbook'
    _description = 'Manage Checkbook'

    #name = fields.Char('CheckBook Name', size=30, readonly=True, select=True, required=True, states={'draft': [('readonly', False)]})
    name = fields.Char('Nombre Chequera', size=30, readonly=False, select=True, required=True, states={'used': [('readonly', True)]})
    range_desde = fields.Char('Check Number Desde', size=8, readonly=True, required=True, states={'draft': [('readonly', False)]})
    range_hasta = fields.Char('Check Number Hasta', size=8, readonly=True, required=True ,states={'draft': [('readonly', False)]})
    #actual_number = fields.Char('Next Check Number', size=8, readonly=True, required=True, states={'draft': [('readonly', False)]})
    actual_number = fields.Char('Next Check Number', size=8, required=True)
    account_bank_id = fields.Many2one('res.partner.bank','Account Bank', readonly=True, required=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users','User')
    change_date = fields.Date('Change Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'In Use'),
                              ('used', 'Used')], string='State',readonly=True, default='draft')
    bank_id = fields.Many2one('res.bank', 'Bank', readonly=True, required=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,states={'draft': [('readonly', False)]})


    #number_draft_id = fields.Many2one('account_checkbook','Cheques pendientes')  # , required=True, states={'draft': [('readonly', False)]}

    _order = "name"

    # @api.model
    # def unlink(self):
    #     ans = {}
    #     for order in self.browse(self):
    #
    #         if order.state not in ('draft'):
    #             raise exceptions.except_orm(_('Error !'), _('You can drop the checkbook(s) only in  draft state !'))
    #             return False
    #     return ans
    #Inicio Nuevo---------------------------------------------
    @api.model
    def create(self, values):
        res = super(account_checkbook, self).create(values)
        return res
    #Fin Nuevo---------------------------------------------

    @api.onchange('bank_id')
    def onchange_bank_id_1(self):
        self.account_bank_id = False
        self.journal_id = False

    @api.onchange('account_bank_id')
    def onchange_account_bank_id_1(self):
        self.journal_id = False


    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise exceptions.except_orm(_('Error !'), _('You can drop the checkbook(s) only in  draft state !'))
        else:
            return super(account_checkbook, self).unlink()

    def _validate_number(self, number):
        ans = {}
        number_obj = re.compile(r"""^\d+$""", re.X)
        if number_obj.search(number):
            ans = {'valid_number':number}
        return ans

    @api.onchange('range_desde')
    def onchange_desde(self):
        if self.range_desde:
            ans = self._validate_number(self.range_desde)
            if not ans:
                #En caso de que el valor no sea un número se vacian los campor range_desde y actual_number
                self.range_desde = ''
                self.actual_number = ''
                return {
                    #'warning': {'title':"Warning", 'message': "Check Number Desde can only be numeric"}
                    'warning': {'title': "Advertencia", 'message': "El campo 'Numero Cheque desde' debe ser númerico"}
                }
            if len(self.range_desde) != 8:
                return {
                    #'warning': {'title': "Warning", 'message': "Ckeck range desde must be 8 numbers !"},
                    'warning': {'title': "Advertencia", 'message': "El campo 'Numero Cheque desde' debe tener 8 dígitos"},
                }
            else:
                #Evaluación para saber si al modificar el nuevo numero range_desde este es mayor al numero range_hasta
                #en dicho caso el campo range_hasta se vacia para esperar un nuevo valor final.
                if self.range_hasta:
                    if int(self.range_desde) >= int(self.range_hasta):
                        self.range_hasta = ''
                value = {'range_desde':self.range_desde}
                self.actual_number = self.range_desde
                return {'value': value}
        else:
            return {'value': {'range_desde': '00000000'}}
        

    @api.onchange('range_hasta')
    def onchange_hasta(self):
        if self.range_hasta:
            ans = self._validate_number(self.range_hasta)
            if not ans:
                return {
                    #'warning': {'title': "Warning", 'message': "Check Number Hasta can only be numeric"}
                    'warning': {'title': "Advertencia", 'message': "El campo 'Numero Hasta' debe ser númerico"}
                }
            if int(self.range_hasta) < int(self.range_desde):
                self.range_hasta = ''
                return {
                    #'warning': {'title': "Warning", 'message': "Range hasta must be greater than range desde!"},
                    'warning': {'title': "Advertencia", 'message': "El campo 'Numero Hasta' debe ser mayor al campo 'Numero Cheque desde'"},
                }

    @api.multi
    def wkf_active(self):
        ans= {}
        check_obj= self.env['account.checkbook']
        for order in self:

            if not order.account_bank_id.account_id.id:
                raise exceptions.except_orm(' %s selected error' % (order.account_bank_id.bank_id.name),
                    'The account must to be created in The Company Bank / Accounting Information.' )
            ans = check_obj.search([('account_bank_id', '=', order.account_bank_id.id), ('state', '=', 'active')],)
            if ans:
                raise exceptions.except_orm(_('Error !'), _('You cant change the checkbook´s state, there is one active !'))
            else:
            #NUevo----------------------------------------------------------------------
                object_issued_check = self.env['account.issued.check']
                list_check = {}
                for i in range(int(self.range_desde), int(self.range_hasta) + 1):
                    number = str(int(i)).zfill(8)
                    list_check.update({'state': '',
                                       'bank_id': self.account_bank_id.bank_id.id,
                                       'account_bank_id': self.account_bank_id.id,
                                       'checkbook_id': self.id,
                                       'checkbook_ids': self.display_name,
                                       'number': number,
                                       'amount': 0,
                                       'receiving_partner_id': 3,
                                       'clearing_date': self.create_date,
                                       'date_check_emi': self.create_date,
                                       'journal_id': 1,
                                       })
                    object_issued_check.create(list_check)
            #Fin Nuevo ------------------------------------------------------------------
                self.write({'state': 'active'})
                return True

    @api.multi
    def wkf_used(self):
        self.write({ 'state' : 'used' })
        return True




