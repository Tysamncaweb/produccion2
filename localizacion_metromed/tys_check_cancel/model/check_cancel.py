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
#    Modulo que permite la anulacion de cheques antes de ser emitidos
#    autor: Tysamnca.
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError,Warning
import logging
_logger = logging.getLogger(__name__)
import time

class account_issued_check(models.Model):
    _inherit = 'account.issued.check'

    @api.multi
    def onchange_number(self, number):

        def anulado(num):
            if not num:
                return False
            check_cancel_obj = self.env['check.cancel']
            check_cancel_number = check_cancel_obj.search([('number','=',num)])
            if check_cancel_number:
                return True
            else:
                return False

        def usado(num):
            if not num:
                return False
            issued_check_obj = self.env['account.issued.check']
            issued_check_number = issued_check_obj.search([('number','=',num)])
            if issued_check_number:
                return True
            else:
                return False

        res = {}
        number_str = str(number)
        if len(number_str) != 8:
            res = {'value':{'number': 0}}
        else:
            while anulado(number) or usado(number):
                number = str(((number) + 1))
            res.update({'value':{'number':number}})
        return res


class check_cancel(models.Model):

    _name = 'check.cancel'
    _description = 'Permite la anulacion de numeros de cheques antes de su emision'


    number = fields.Char('Check Number', select=True, readonly=True, states={'draft': [('readonly', False)]})
    actual = fields.Char('Current Check', size=8)
    ultimo = fields.Char('Last Check', size=8)
    checkbook_ids = fields.Char('Chequera')
    checkbook_id = fields.Many2one('account.checkbook')
    check_endorsed = fields.Boolean('Endorsed', required=True, states={'draft': [('invisible', False)]})
    user_id = fields.Many2one('res.users','User')
    date = fields.Date('Date Cancel', required=True)
    notas = fields.Text('Notes',states={'draft': [('invisible', False)]})
    state = fields.Selection([('draft','Draft'),('anuled','Anulado')], string='State', default='draft')
    bank_id = fields.Many2one('res.bank', 'Bank')
    account_bank_id = fields.Many2one('res.partner.bank', 'Destiny Account', required=True)
    numbers_id = fields.Many2one('account.issued.check')
    checks_id = fields.Boolean('checks', default = False)
    numbers = fields.Char()

    account_ids = fields.Many2many('account.issued.check', string="Cheques")

    move_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    asiento_conciliado = fields.One2many('account.move.line', related='move_id.line_ids', string='Asientos contables')

    move_payed_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    asiento_conciliado_payed = fields.One2many('account.move.line', related='move_payed_id.line_ids', string='Asientos contables')


    checkbook_state = None


    @api.onchange('bank_id')
    def clean_date(self):                   # Limpia todos los campos al cambiar el banco
        self.account_bank_id = False
        self.checkbook_ids = False
        self.number = False
        self.numbers_id = False
        self.checks_id = False
        self.account_ids = False
        self.move_id = False
        self.move_payed_id = False

    @api.onchange('account_bank_id')
    def filter_account_bank_id(self):       # Filtra y trae la chequera asignada a la cuenta del banco
        if self.account_bank_id:
            self.checkbook_id= self.env['account.checkbook'].search([('account_bank_id','=',self.account_bank_id.id),('state','=','active')])
            if self.checkbook_id:
                return {'value': {'checkbook_ids': self.checkbook_id.name}}
            else:
                warning = {'title': _('Advertencia'),
                           'message': _('Esta cuenta bancaria no tiene chequera asignada')}
                return {'value': {'checkbook_ids': False}, 'warning': warning}

    @api.onchange('checks_id','numbers_id')
    def validate_type_check(self):          # Se selecciona el tipo de cheque que se desea eliminar con un checkbox (Ya usados en estado "Borrador" y "Cartera" o los no utilizados)
        if self.checks_id == False:

            if self.numbers_id:
                estado = self.env['check.cancel'].search([('number', '=', self.numbers_id.number), ('checkbook_id', '=', self.checkbook_id.id)])
                if estado.state == ('draft' or 'anuled'):
                    raise UserError(_('El cheque %s esta marcado para ser anulado') % (self.numbers_id.number))
                self.number = self.numbers_id.number

            self.account_ids = False
        elif self.checks_id == True:
            self.move_id = False
            self.move_payed_id = False
            self.numbers_id = False
            self.ultimo = self.checkbook_id.range_hasta
            if self.checkbook_id.state == 'used':
                warning = {'title': _('Advertencia'),
                           'message': _('Esta chequera fue utilizada completamente')}
                return {'warning': warning}

    @api.multi
    def name_get(self):                     # Se encarga de pintar el nombre del cheque cuando se crea o cuando se quiere visualizar
        res = []
        #res = super(check_cancel, self).name_get()
        #if self._context.get('come_form', False) and self._context.get('come_form', False) == self._name:
        for number in self:
            res.append((number.id, 'Cheque N°: %s' % (number.number)))
        return res

    @api.model
    def create(self, values):               # Crea en estado borrador, los cheques que se quieren anular
        numss = []
        nums = values.get('number', 0)
        cant_check = values.get('account_ids', 0)
        sep_checks = cant_check[0][2]
        if sep_checks:                      # Varios cheques no utilizados
            for checks in sep_checks:
                var = self.env['account.issued.check'].search([('id', '=', checks)])
                numss.append(var.number)
            res = self.value_create(numss, values)
        else:                               # Un solo cheque en estado "borrador" y "cartera"
            numss.append(nums)
            res = self.value_create(numss, values)
        #res.update({'numbers': numss})
        return res

    @api.multi
    def value_create(self, numss, values):  # Valida que los cheques seleccionados no esten en estado anulados o en borrador
        local_checkbook = values.get('checkbook_id', False)
        for checks in numss:
            values['number'] = checks
            estado = self.env['check.cancel'].search([('number', '=', checks), ('checkbook_id', '=', local_checkbook)])
            if estado.state == ('anuled' or 'draft'):
                raise UserError(_('El cheque %s ya fue anulado o esta marcado para ser anulado') % (checks))
            res = super(check_cancel, self).create(values)
        return res

    @api.onchange('account_ids')
    def validate_checks(self):
        var = []
        for account_id in self.account_ids:
            checks = self.env['check.cancel'].search([('number', '=', account_id.number), ('checkbook_id', '=', account_id.checkbook_id.id)])
            if checks:
                var.append(account_id.number)

        if len(var) == 1:
            raise UserError(_('El cheque %s esta marcado para ser anulado') % (var[0]))
        elif len(var) > 1:
            raise UserError(_('Los cheques %s estan marcados para ser anulados') % (var))
        else:
            return var

    @api.onchange('numbers_id')
    def validate_contented_seat(self):
        self.move_id = self.numbers_id.move_id.id



    @api.multi
    def write(self, values):
        #Validación previa a guardar
        if values:
            if values.get('move_id'):
                res = super(check_cancel, self).write(values)
                return res
            if values['state'] == 'draft':
                cont = 0
                cant_check = values.get('account_ids', 0)
                sep_checks = cant_check[0][2]
                if values['checks_id'] == True:
                    if sep_checks:
                        for checks in sep_checks:
                            cont += 1
                            var = self.env['account.issued.check'].search([('id', '=', checks)])
                            values['number'] = var.number
                            if cont == 1:
                                res = super(check_cancel, self).write(values)
                            else:
                                values['bank_id'] = self.bank_id.id
                                values['account_bank_id'] = self.account_bank_id.id
                                values['checkbook_id'] = self.checkbook_id.id
                                values['checkbook_ids'] = self.checkbook_ids
                                values['user_id'] = self.user_id.id
                                values['date'] = self.date
                                values['notas'] = self.notas
                                res = super(check_cancel, self).create(values)
                else:
                    if self.account_ids:
                        res = super(check_cancel, self).write(values)
                    else:
                        raise UserError(_('No se a seleccionado ningun cheque para la anulación'))
                return res
            else:
                if values['state'] == 'anuled':
                    res = super(check_cancel, self).write(values)
                    return res

    @api.multi
    def _get_checkbook_id(self):
        res={}
        checkbook_pool = self.env['account.checkbook']
        res = checkbook_pool.search([('state', '=', 'active')])
        if res:
            return res.id
        else:
            return False

    @api.multi
    def onchange_checkbook(self, checkbook_id):
        res = {}
        if not checkbook_id:
            return {}
        chequera = self.env['account.checkbook'].browse(checkbook_id)
        if chequera:
            actual = chequera.actual_number
            ultimo = chequera.range_hasta
            global checkbook_state
            checkbook_state= chequera.state
            return {'value': {'actual': actual, 'number': actual, 'ultimo': ultimo}}
        else:
            return {}

    _defaults = {
            'user_id': lambda s, cr, u, c: u,
            'date': lambda *a: time.strftime('%Y-%m-%d'),
                 }

    @api.multi
    def wkf_cancel(self):
        if self.checks_id == True:
            if self.account_ids:
                #sep_checks = self.account_ids[0][2]
                if self.account_ids:  # Varios cheques no utilizados
                    for check in self.account_ids:
                        self.cancel_check(check)
                else:
                    warning = {'title': _("Aviso"), 'message': _('No se a seleccionado ningún cheque para anular')}
                    return {'warning': warning}
                return True
        else:
            if self.numbers_id:
                if self.numbers_id.move_id.state == 'draft':
                    self.env['account.move'].search([('id', '=', self.move_id.id)]).unlink()
                elif self.numbers_id.move_id.state == 'draft' and self.numbers_id.move_payed_id.state == 'draft':
                    self.env['account.move'].search([('id', '=', self.move_id.id)]).unlink()
                    self.env['account.move'].search([('id', '=', self.move_payed_id.id)]).unlink()
                elif self.numbers_id.move_id.state == 'posted' and self.numbers_id.move_payed_id.state == 'draft':
                    self.reversal_seats()
                    self.env['account.move'].search([('id', '=', self.numbers_id.move_payed_id.id)]).unlink()
                self.cancel_check(self.numbers_id)
                return True
            #FALTA ES EL BOTON PARA MOSTRAR ASIENTO REVERTIDO
            """
            if self.numbers.find(',') != -1:
                checks_to_cancel = self.numbers.split(',')
                for check in checks_to_cancel:
                    self.cancel_check(check)
                warning = {'title': _("Aviso"),'message': _('Se han anulado los cheques %s' % (self.numbers))}
                return {'warning': warning}
            elif self.numbers.find('-') != -1:
                checks_to_cancel = self.numbers.split('-')
                checks_to_cancel = self.value_conti_create(checks_to_cancel)
                for check in checks_to_cancel:
                    self.cancel_check(check)
                warning = { 'title': _("Aviso"),'message': _('Se han Anulado la secuencia de cheques %s' % (self.numbers))}
                return {'warning': warning}
            else:
                self.cancel_check(self.number)
                warning = {'title': _("Aviso"), 'message': _('Se ha anulado el cheque numero %s' % (self.numbers))}
                return {'warning': warning}
                
                """

    @api.multi
    def reversal_seats(self):
        #Revesa solo el primer asiento contable
        bus = self.env['account.move'].search([('id','=',self.move_id.id)])
        #journal_id = self.env['account.move.line'].search([('move_id','=',self.move_id.id)])
        reverso = bus.reverse_moves(self.date,bus.journal_id)
        self.move_id = reverso[0]
        return True


    @api.multi
    def cancel_check(self, nbr):
        if self.id:

            checks_a = self.search([('number', '=', nbr.number), ('checkbook_id', '=', nbr.checkbook_id.id)])
            checks_p = self.env['account.issued.check'].search([('number', '=', nbr.number),('checkbook_id', '=', nbr.checkbook_id.id), ('state', '!=', 'cancel' or 'anuled' or 'holding' or 'handed' or 'hrejected')])
            if (checks_p.state or checks_a.state == 'draft' or 'False'):
                checks_a.write({'state': 'anuled'})
                checks_p.write({'state': 'anuled'})
            else:
                raise UserError(_('El cheque numero %s, ya fue anulado' % (nbr.number)))

            chequeras = self.env['account.checkbook']
            chequera_obj = chequeras.browse(self.checkbook_id.id)
            if chequera_obj.actual_number == nbr.number:
                if chequera_obj.actual_number == chequera_obj.range_hasta:
                    chequera_obj.write({'state': 'used'})
                else:
                    siguiente = int(nbr.number) + 1
                    siguiente = str(siguiente)
                    chequera_obj.write({
                        'actual_number': siguiente.zfill(len(nbr.number))})

        return True

    def wkf_undo(self):
        self.write({'state' : 'draft'})
        return True

class account_third_check(models.Model):

    _inherit = 'account.third.check'

    _defaults = {

        'company_id': lambda self, c: self.pool.get('res.users').browse( c).company_id.id,
    }
