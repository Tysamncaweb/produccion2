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



from odoo import models, fields, api, _, netsvc, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import Warning
from odoo.tools.translate import _
import logging
import time
_logger = logging.getLogger(__name__)
from odoo.tools.translate import _
from datetime import datetime


class account_issued_check(models.Model):

    @api.multi
    @api.returns('account.checkbook') #, lambda r: r.id
    def _get_checkbook_id(self):

        checkbook_env = self.env['account.checkbook'].search([('state', '=', 'active')],)
        obj= self.browse(checkbook_env)
        ans = checkbook_env
        if ans:
            return ans
        else:
            raise exceptions.except_orm(_('Error !'), _('Debe Crear una Chequera para Poder Emitir el Cheque  '))


    _name = 'account.issued.check'
    _description = 'Manage Checks Issued'


    name =fields.Char('nombre cheque')
    numbers = fields.Char()
    number = fields.Char('Check Number', size=8, required=True, select=True, states={'draft': [('readonly', True)]})
    amount = fields.Float('Amount Check', required=True,readonly=True,states={'draft': [('readonly', False)]})
    date_check_emi = fields.Date('Fecha de emisión del Cheque',required=True ,size=28, states={'draft': [('readonly', False)]}) #default=fields.Date.context_today
    debit_date = fields.Date('Date Debit', readonly=True) # clearing date + clearing
    receiving_partner_id = fields.Many2one('res.partner','beneficiary/provider',size=8, required=True, states={'draft': [('readonly', False)]})
    check_endorsed = fields.Boolean('No Endorsed', required=True, store=True, default=True, states={'draft': [('invisible', False)]})
    clearing = fields.Selection((
            ('24', '24 hs'),
            ('48', '48 hs'),
            ('72', '72 hs'),
        ), 'Clearing',readonly=True,states={'draft': [('readonly', False)]})
    account_bank_id = fields.Many2one('res.partner.bank','Account Bank',required=True,readonly=True,states={'draft': [('readonly', False)]})
    voucher_id = fields.Many2one('account.payment', 'payment')
    bank_id = fields.Many2one('res.bank', 'Bank', readonly=True, required=True, states={'draft': [('readonly', False)]})
    issued = fields.Boolean('Issued')
    user_id = fields.Many2one('res.users','User')
    check_description = fields.Char('Description',size=100,states={'draft': [('readonly', False)]})
    change_date = fields.Date('Change Date', default= lambda *a: time.strftime('%Y-%m-%d')) #required=True)
    clearing_date = fields.Date('Fecha de Entrega de Cheque',states={'holding': [('readonly', False)]},size=28)
    state =fields.Selection([('',''),
                             ('draft','Draft'),
                             ('holding', 'En Cartera'),
                             ('handed','Handed'),
                             ('payed', 'Pagado'),
                             ('hrejected','Hand-Rejected'),
                             ('anuled', 'Anulado'),
                             ('cancel', 'Cobrado')]
    ,string='State', default='draft')
    group_multi_company= fields.Many2one('res.company')
    company_id = fields.Many2one('res.company', 'Company',readonly=True,states={'draft':[('readonly',False)]}, select=1, help="Company related to this Check=1")
    reject_debit_note = fields.Many2one('account.invoice','Reject Debit Note')
    number_draft_id = fields.Many2one('account.issued.check', 'Cheques pendientes') #.Many2one('account_checkbook','Cheques pendientes',related='checkbook_id.actual_number')#, required=True, states={'draft': [('readonly', False)]}
    checkbook_id = fields.Many2one('account.checkbook','Checkbook',required=True,states={'draft': [('readonly', False)]}) #domain="[('state', '=', 'active')]"
    checkbook_ids = fields.Char('Chequera', required=True, select=True, readonly=True, states={'draft': [('readonly', False)]})
    #checks_draft= fields.Boolean('Cheques pendientes en Borrador', required=True)
    reconcile = fields.Many2one('account.issued.check','reconcile', invisible=True)
    journal_id = fields.Many2one('account.journal',required=True, string='Journal',states={'draft': [('readonly', False)]})
    date_hrejected = fields.Date('Fecha de rechazo del cheque',size=28,states={'hrejected': [('readonly', False)]})
    cuenta_transitoria = fields.Many2one('account.account', 'Cuenta Transitoria', readonly=True, states={'draft': [('readonly', False)]})


    _sql_constraints = [('number_check_uniq','unique(number,account_bank_id)','The number must be unique!')]
    _order = "number"
    _defaults = {
        'clearing': lambda *a: '48',
        'state': 'draft',
        'change_date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda s, cr, u, c: u,
        'company_id': lambda self, cr, uid, c: self.accoun('res.users').browse(cr, uid, uid, c).company_id.id,
        'checkbook_id': 'active',  #_get_checkbook_ids
    }

    @api.multi
    def unlink(self):
        ans = {}
        for order in self:
            if order.state not in ('draft'):
                raise exceptions.except_orm(_('Error !'), _('The Check must  be in draft state only for unlink !'))
            else:
                return super(account_issued_check, order).unlink()
        return ans

    def _checkbook_fin(self, check_actual_number, check_fin_number):
        ans = {}
        if check_actual_number and check_fin_number:
            if check_actual_number == check_fin_number:
                # ans = {'warning':{'title':'Warning','message':'This is the las check in the checkbook.\nMust activate another one for the next pay'}}
                ans = {'warning': {'title': 'Advertencia',
                                   'message': 'Este es el último cheque en esta chequera.\nPara el proximo pago deberá activar una nueva'}}
        return ans


    @api.model
    def create(self, values):
            order_obj = self.env['account.payment']
            order_id = values.get('voucher_id', self._context.get('active_ids', []))
            # if not order_obj.browse(order_id):
            #     raise exceptions.except_orm(_('Error !'), _('The Check must be create on one payment !'))
            #     return ans
            checkbook_obj = self.env['account.checkbook']
            num = values['checkbook_id']
            book = checkbook_obj.browse(num)
            if book.state == 'active':
                checks = self.env['account.issued.check'].search([('checkbook_id','=',num),('number','=',values['number'])])
                checks.update({'state':values['state'],
                               'date_check_emi': values['date_check_emi'],
                               'bank_id':values['bank_id'],
                               'journal_id': values['journal_id'],
                               'account_bank_id':values['account_bank_id'],
                               'amount':values['amount'],
                               'receiving_partner_id': values['receiving_partner_id'],
                               'clearing_date': values['clearing_date'],
                               'change_date': values['change_date'],
                               'check_description': values['check_description'],
                               'company_id': book.journal_id.company_id.id,
                               })

                if values['amount'] <= 0:
                    raise Warning(_('Debe introducir en el cheque un monto mayor a 0,00'))

                # Conteo de cheque actual ----------------------------------------------
                hasta = actual = 0
                actual = int(book.actual_number)
                hasta = int(book.range_hasta)
                if actual == hasta:
                    book.write({'state': 'used', })
                else:
                    if str(book.actual_number) < str(book.range_hasta):
                        sum_actual_number = int(book.actual_number) + 1
                        book.write({'actual_number': str(sum_actual_number).zfill(8)})
                #-----------------------------------------------------------------------
                ans = checks
                checks.write(values)

            elif book.state == 'draft':
                ans = super(account_issued_check, self).create(values)
            return ans


    @api.onchange ('bank_id')
    def onchange_bank_id (self):
        self.account_bank_id= False
        self.checkbook_ids= False
        self.number = False
        self.checkbook_id = False
        self.journal_id = False

    @api.onchange ('checkbook_ids')
    def onchange_checkbook_id(self):
            result = {}
            if self.checkbook_id:
                ans = self.env['account.checkbook'].browse([(self.checkbook_id.id)])
                # Busca la chequera activa de acuerdo a la cuenta
                if not ans.id:
                    result = {'value': {'checkbook_ids': None, 'number': None}}
                    result.update({'warning': {'title': _('Error !'), 'message': _('You must be create a checkbook or change state')}})
                    return result
                if ans.state != 'active':
                    result = {'value': {'checkbook_ids': False}}
                    result.update({'warning': {'title': _('Error !'), 'message': _('The Checkbook is not active')}})
                else:
                    bus =self.env['account.issued.check'].search([('checkbook_id','=',self.checkbook_id.id),('state','!=',['draft','payed','anuled','holding','handed','hrejected'])])
                    if bus:
                        ones = bus[0]
                        one = ones.number
                        ans.update({
                            'actual_number':one,
                        })
                    else:
                        one = False
                        ans.update({
                            'state':'used',
                        })
                    result = {'value': {'number': one}}
                    result.update(self._checkbook_fin(one, ans.range_hasta))
                    pass

               # if self.checks_draft:
                    checks = self.search([('checkbook_id', '=', self.checkbook_ids), ('state', '=', 'draft')])
                    if checks:
                        result.update({'warning': {'title': _('Error !'), 'message': _('EXISTEN CHEQUES EN ESTADO BORRADOR')}})
            return result

    @api.onchange('account_bank_id')
    def onchange_(self):
        if self.account_bank_id:
            checkbook = self.env['account.checkbook'].search(
                [('account_bank_id', '=', self.account_bank_id.id),('state', '=', 'active')])
            self.checkbook_id = checkbook
            self.journal_id = checkbook.journal_id.id
            if self.checkbook_id:
                return {'value': {'checkbook_ids': self.checkbook_id.name,
                                  'journal_id': self.journal_id}}
            else:
                warning = {
                    'title': _('Advertencia'),
                    'message': _('Esta cuenta bancaria no tiene chequera asignada')
                }
                return {'value': {'checkbook_ids': False}, 'warning': warning}



    @api.onchange('checks_draft')
    def onchange_checks_draft(self):
        warning = {}
        if self.checks_draft:
            checks=self.search([('checkbook_id', '=', self.checkbook_ids),('state','=','draft')])
            if checks:
                warning = {'title': _('Advertencia'),
                    'message': _('Esta cuenta bancaria no tiene chequera asignada')
                }
        return {'checks': {'checkbook_id': False}, 'warning': warning}


    @api.multi
    def onchange_clearing_date(self, date, clearing_date):
            ans = {}
            if clearing_date < date:
                ans = {'value': {'clearing_date': None}}
                ans.update({'warning': {'title': _('Error !'), 'message': _('Clearing date must be greater than check date')}})
            else:
                ans = {'value': {'clearing_date': clearing_date}}
            return ans


    @api.model
    def name_get(self):
            res = []
            #res = super(account_issued_check, self).name_get()
            #if self._context.get('come_form', False) and self._context.get('come_form', False) == self._name:
            for number_draft_id in self:
                res.append((number_draft_id.id,'Cheque N°: %s' % (number_draft_id.number)))
            return res

    @api.one
    def validate_amount(self):
        if self.amount <= 0:
            raise Warning(_('El monto de anticipo debe ser mayor que cero'))
        return True




class account_third_check(models.Model):

        _name = 'account.third.check'
        _description = 'Manage Checks Third'

        number = fields.Char('Check Number', size=8, required=True, readonly=True,states={'draft': [('readonly', False)]})
        sequence_number = fields.Char('Id Number', size=40, readonly=True, states={'draft': [('readonly', False)]})
        amount = fields.Float('Check Amount', required=True, readonly=True, states={'draft': [('readonly', False)]})
        date_in = fields.Date('Fecha de Registro', size=17, required=True, states={'draft': [('readonly', False)]})
        date_check = fields.Date('Fecha del cheque', size=15, required=True, readonly=True, states={'draft': [('readonly', False)]})
        source_partner_id = fields.Many2one('res.partner', 'Cliente', size=8, required=True)
        destiny_partner_id = fields.Many2one('res.partner', 'Destiny Partner', readonly=True,states={'handed': [('required', True)]})
        check_endorsed = fields.Boolean('Endorsed', required=True, states={'draft': [('invisible', False)]})
        state = fields.Selection((
            ('draft', 'Draft'),
            ('holding', 'Holding'),
            ('deposited', 'Deposited'),
            ('drejected', 'Dep-Rejected'),
            ('sold', 'Cobrado' ),
        ), 'State', required=True, default='draft')
        account_bank_id = fields.Char('Bank', size=24, readonly=True, required=True,states={'draft': [('readonly', False)]})
        vat = fields.Char('RIF', size=11, states={'draft': [('readonly', False)]})
        user_id = fields.Many2one('res.users', 'User')
        change_date = fields.Date('Change Date')#, required=True)
        clearing_date = fields.Date(string='Fecha de entrega del cheque')
        clearing = fields.Selection((
            ('24', '24 hs'),
            ('48', '48 hs'),
            ('72', '72 hs'),
        ), 'Tiempo de Cobro', size=15, readonly=True, states={'draft': [('readonly', False)]})
        bank_id = fields.Selection((
            ('100%_Banco', '100% Banco'), ('Bancamiga', 'Bancamiga'),('BanCaribe', 'BanCaribe'),('Banco_Activo', 'Banco Activo'),('Banco_Agrícola_de_Venezuela', 'Banco_Agrícola_de_Venezuela'),
            ('Banco_Bicentenario_del_Pueblo', 'Banco Bicentenario del Pueblo'),('Banco_Caroní', 'Banco Caroní'),('Banco_de_Comercio_Exterior_(Bancoex)', 'Banco de Comercio Exterior (Bancoex)'),
            ('Banco_de_Exportación_y_Comercio', 'Banco de Exportación y Comercio'),('Banco_de_Venezuela', 'Banco de Venezuela'),('Banco_del_Tesoro', 'Banco del Tesoro'),('Banco_Exterior', 'Banco Exterior'),
            ('Banco_Internacional_de_Desarrollo', 'Banco Internacional de Desarrollo'),('Banco_Mercantil', 'Banco Mercantil'),('Banco_Nacional_de_Crédito_BNC', 'Banco Nacional de Crédito BNC'),('Banco_Plaza', 'Banco Plaza'),
            ('Banco_Sofitasa', 'Banco Sofitasa'), ('Banco_Venezolano_de_Crédito', 'Banco Venezolano de Crédito'), ('Bancrecer', 'Bancrecer'), ('Banesco', 'Banesco'), ('BanFANB', 'BanFANB'),
            ('Bangente', 'Bangente'), ('Banplus', 'Banplus'), ('BBVA_Provincial', 'BBVA Provincial'), ('BFC_Banco_Fondo_Común', 'BFC Banco Fondo Común'), ('BOD', 'BOD'),
            ('Citibank_Sucursal_Venezuela', 'Citibank Sucursal Venezuela'), ('DELSUR', 'DELSUR'), ('Instituto_Municipal_de_Crédito_Popular_(IMCP)', 'Instituto Municipal de Crédito Popular (IMCP)'), ('Mi_Banco', 'Mi Banco'),
        ), 'Tiempo de Cobro', size=15, readonly=True, states={'draft': [('readonly', False)]})

        voucher_id = fields.Many2one('account.payment', 'payment')
        company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True,states={'draft': [('readonly', False)]}, select=1,help="Company related to this Check")
        reject_debit_note = fields.Many2one('account.invoice', 'Reject Debit Note')
        reject_debit_note_prov = fields.Many2one('account.invoice', 'Reject Debit Note Prov')
        clearing_date_hasta = fields.Date('Clearing Date Hasta', required=False)
        ticket_deposit_id = fields.Many2one('ticket.deposit', string='Ticket Deposit', required=False, readonly=True,states={'draft': [('readonly', False)]})
        description = fields.Char('Observacion/Ref', Size=100)
        journal_id = fields.Many2one('account.journal', string='Journal',states={'draft': [('readonly', False)]})
        date_drejected = fields.Date('Fecha de rechazo del cheque', size=28,states={'deposited': [('readonly', False)]})
        cuenta_transitoria = fields.Many2one('account.account', 'Cuenta Transitoria', readonly=True,states={'draft': [('readonly', False)]})


        _order = "clearing_date"
        _defaults = {
            'state': 'draft',
            'clearing': lambda *a: '48',
            'date_in': lambda *a: time.strftime('%Y-%m-%d'),
            'change_date': lambda *a: time.strftime('%Y-%m-%d'),
            'user_id': lambda s, cr, u, c: u,
            'company_id': lambda self, c: self.env['res.users'].browse(self, c).company_id.id,
        }


        @api.multi
        def search(self, args, offset=0, limit=None, order=None, count=False):
            pos = 0
            desde = False
            hasta = False
            while pos < len(args):
                if args[pos][0] == 'clearing_date':
                    desde = args[pos][2]
                if args[pos][0] == 'clearing_date_hasta':
                    hasta = args[pos][2]
                pos +=1

                if desde and hasta:
                    return super(account_third_check,self).search([('clearing_date', '>', desde),
                                                                    ('clearing_date', '<', hasta),
                                                                    ])

            return super(account_third_check,self).search(args, offset=offset, limit=limit, order=order, count=count)


        @api.multi
        def onchange_number(self, number):
            ans = {}
            if number:
                if len(number) != 8:
                    ans = {'value': {'number': '0'}}
                    ans.update({'warning': {'title': _('Error !'), 'message': _('Ckeck Number must be 8 numbers !')}})
                else:

                    ans = {'value': {'number': number}}
            return ans

        @api.multi
        def onchange_clearing_date(self, date, clearing_date):
            ans = {}
            if clearing_date < date:
                ans = {'value': {'clearing_date': None}}
                ans.update(
                    {'warning': {'title': _('Error !'), 'message': _('Clearing date must be greater than check date')}})
            else:
                ans = {'value': {'clearing_date': clearing_date}}
            return ans

        @api.multi
        def onchange_vat(self, vat):
            obj = self.browse(self)
            ans = {}
            if obj.number:
                if not vat:
                    ans.update({'warning': {'title': _('Error !'), 'message': _('Vat number must be not null !')}})
                else:
                    if len(vat) != 11:
                        ans = {'value': {'vat': None}}
                        ans.update(
                            {'warning': {'title': _('Error !'), 'message': _('Vat number must be 11 numbers !')}})
                    else:
                        ans = {'value': {'vat': vat}}
                return ans

        @api.multi
        def unlink(self):
            ans = {}
            for order in self:
                if order.state not in ('draft'):
                    raise exceptions.except_orm(_('Error !'), _('The Check must  be in draft state only for unlink !'))
                else:
                    return super(account_third_check, order).unlink()
            return ans

        @api.model
        def create(self, values):
            order_obj = self.env['account.payment']
            seq_obj_name = 'check.third'
            name = self.env['ir.sequence'].get(seq_obj_name)
            values['sequence_number'] = name
            ans = super(account_third_check, self).create(values)
            if values['amount'] <= 0:
                raise Warning(_('Debe introducir en el cheque un monto mayor a 0,00'))
            return ans

