# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import select

from odoo import models,fields,api

#account__small_box

from datetime import *
import time
from odoo.exceptions import UserError

class small_box(models.Model):
    _name = 'account.small'
    _rec_name = 'small_code'

    STATES = [('draft', 'Draft') ,
              ('aprobation', 'On Aprobation'),
             ('approved', 'Approved'),
              ('cancel', 'Cancel')]

    small_code = fields.Char('Code',readonly=True)
    small_description = fields.Char('Description',size=40)
    small_responsible = fields.Many2one('res.users',"User")
    small_coin = fields.Char('Coin',readonly=True)
    small_accounting_account = fields.Many2one('account.account',"Account")
    small_transitory_account = fields.Many2one('account.account',"Transitory")
    small_date = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    state = fields.Selection (STATES , string='State' , index=True , readonly=True , default='draft',
                              track_visibility='onchange' , copy=False , select=True)
    small_debit_account_increase = fields.Float(compute='_debt_account_increase', string='otro')
    small_debit_account = fields.Float('Debit')
    small_debit_transitory = fields.Float('Debit')
    small_type_expense = fields.One2many('account.small.type.expense','id_small_box')
    small_daily_id = fields.Many2one ('account.journal')
    #small_company_id = fields.Many2one('res.company')

    #small_period_id = fields.Many2one('account.period')

    # estructura de una funcion

    @api.onchange('small_code')
    def _consecutivo(self):

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_small_box'
        uid = self._uid
        res_company = self.env['res.company'].search([('id', '=', uid)])
        IrSequence = self.env['ir.sequence'].with_context(force_company=res_company.id)
        self.small_code = IrSequence.next_by_code(SEQUENCE_CODE)

        # if a sequence does not yet exist for this company create one
        if not self.small_code:
            IrSequence.sudo().create({
                'prefix' : 'CCH',
                'name': 'Localización Venezolana Caja Chica %s' % res_company.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': res_company.id,
            })
            self.small_code = IrSequence.next_by_code(SEQUENCE_CODE)


        #ids = self.search([(1, '=', 1)], order='small_code desc', limit=1)
        #if ids:
        #    prefijo = "CCH-"
        #    sequence = ids.small_code.split('-')
        #    sec_num = int(sequence[1]) + 1
        #    serie = sec_num
        #    self.small_code = prefijo + str(serie).rjust(5, '0')
        #else:
        #    serie = 1
        #    prefijo = "CCH-"
        #    self.small_code = prefijo + str(serie).rjust(5, '0')

    @api.onchange('small_coin')
    def _coin(self):
        self.small_coin = "Bs"

    @api.one
    def confirm(self):
        self.write({'state': "aprobation"})

    @api.one
    def confirm_small(self):
        self.write({'state': "approved"})

    @api.one
    def cancel_small(self):
        self.write({'state': "draft"})

    @api.onchange('small_accounting_account')
    def _debt_account(self):
            sum_debit_account = 0.00
            account_id = self.small_accounting_account.id
            account_move_obj = self.env['account.move.line']
            ids = account_move_obj.search([('account_id', '=',account_id)])
            for item in ids:
                sum_debit_account = sum_debit_account + item.debit
            self.small_debit_account = sum_debit_account


    @api.onchange('small_box')
    def _debt_account_increase(self):
        sum_debit_account = 0.00
        account_id = self.small_accounting_account.id
        account_move_obj = self.env['account.move.line']
        ids = account_move_obj.search([('account_id', '=', account_id)])
        for item in ids:
            sum_debit_account = sum_debit_account + item.debit
        self.small_debit_account_increase = sum_debit_account
        self.write({'small_debit_account':self.small_debit_account_increase})
        id = self.env['account.validate.small.box'].search([('name', '=', self.small_code)])
        small_debit_account = id.small_debit_account
        id_small = id.id
        if self.small_debit_account_increase != small_debit_account :
            self.env['account.validate.small.box'].search([('id', '=', id_small)]).write({'small_debit_account': self.small_debit_account_increase,
                                                                                          'state':'inactive'})


class small_type_expense(models.Model):
    _name = 'account.small.type.expense'
    _rec_name = 'id_type_expense'
    name = fields.Char('Small_type_expense')
    code = fields.Char('code')
    id_type = fields.Integer('id')
    id_type_expense = fields.Many2one('account.account')
    id_small_box = fields.Many2one('account.small')
    #id_validate_small_box = fields.Many2one('account.validate.small.box')
    #id_small_Validate_tickets = fields.Many2one('account.small.validate.tickets')

    @api.onchange('id_type_expense')
    def _expense(self):
        self.name = self.id_type_expense.name
        self.code = self.id_type_expense.code


class validate_small_box(models.Model):
    _name = 'account.validate.small.box'

    name = fields.Char('Name', readonly=True)
    STATES = [('inactive', 'Inactive'),
              ('active', 'Active')]
    state = fields.Selection(STATES, string='State', index=True, readonly=True, default='inactive',
                             track_visibility='onchange', copy=False, select=True)
    small_box = fields.Many2one('account.small',domain="[('state','=','approved')]")
    small_coin = fields.Char ()
    small_description = fields.Char ("Description")
    small_responsible = fields.Char ("User")
    small_Validate_tickets = fields.One2many('account.small.validate.tickets','id_validate_small_box')
    total_result = fields.Float(compute='_compute_result', string='Total')
    small_debit_account = fields.Float('balance account debit')
    small_debit_transitory = fields.Float('debit')
    small_daily_name = fields.Char('account.journal')
    small_period_name = fields.Char('account.period')
    small_accounting_account = fields.Char( "Account")
    small_transitory_account = fields.Char("Transitory")

    @api.model
    def create(self, values):
        if values:
            if values.get('small_box')== False:
                raise Exception.except_orm(("Warning!"), ("Debe Selecionar la Caja Chica"))
            else:
                compare = values.get('small_box')
                ids = self.search([('small_box','=',compare)])
                if ids:
                 raise Exception.except_orm(("Warning!"), ("La Caja chica ya esta activa "))
        record = super(validate_small_box, self).create(values)
        return record



    @api.onchange('small_box')
    def _debt(self):
        account_id = self.small_box.id
        account_id_res = self.small_box.small_responsible.name
        self.small_responsible = account_id_res
        account_id_name = self.small_box.small_code
        self.name = account_id_name
        ids = self.env['account.small'].search([('id', '=', account_id)])
        for item in ids:
            self.small_coin = item.small_coin
            self.small_description = item.small_description
            self.small_debit_account = item.small_debit_account
            self.small_debit_transitory = item.small_debit_transitory
            self.small_daily_name = item.small_daily_id.name
            #self.small_period_name = item.small_period_id.name
            self.small_accounting_account = item.small_accounting_account.code
            self.small_transitory_account = item.small_transitory_account.code



    @api.multi
    @api.depends('small_Validate_tickets.Result')
    def _compute_result(self):
        for l in self:
            l.total_result = sum(line.Result for line in l.small_Validate_tickets)

    @api.multi
    @api.one
    def confirm(self):
        if(self.small_debit_account == 0) and (self.total_result == 0):
            raise Exception.except_orm(("Warning!"),("Debe Selecionar la Caja Chica"))
        if(self.total_result == 0):
            raise Exception.except_orm(("Warning!"), ("Debe Ingresar la cantidad de dinero percibido"))
        if (self.total_result != self.small_debit_account ):
            raise Exception.except_orm(("Warning!"), (" La cantidad de dinero percibido es diferente a la de la cuenta contable"))
        else:
            self.write({'state': "active"})
            self.env['account.small.validate.tickets'].search([('id_validate_small_box', '=', self.id)]).write(
                {'state': 'inactive'})
            id_small_box = self.env['account.small.replacement'].search([('id_temp', '=', self.small_box.id)])
            if id_small_box:
                self.env['account.small.replacement'].search([('id_temp', '=', self.small_box.id)]).write(
                    {'small_debit_account': self.small_debit_account})

class small_Validate_tickets(models.Model):
    _name = 'account.small.validate.tickets'


    tickets = fields.Float("Tickets")
    quantity = fields.Float("Quantity")
    Result = fields.Float(compute='_result', string='Total', store=True)
    id_validate_small_box = fields.Many2one('account.validate.small.box')
    STATES = [('inactive', 'Inactive'),
              ('active', 'Active')]
    state = fields.Selection(STATES, string='State', index=True, readonly=True, default='active',
                             track_visibility='onchange', copy=False, select=True)
    #enabled = fields.Char('enabled')

    @api.multi
    @api.depends('tickets', 'quantity')
    def _result(self):
        for l in self:
            l.Result = float(l.tickets) * float(l.quantity)

class small_replacement(models.Model):
    _name = 'account.small.replacement'

    replacement_code = fields.Char('Code', readonly=True)
    replacement_date = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    replacement_transactions = fields.One2many ('account.small.transactions','id_replacement')
    small_box = fields.Many2one('account.validate.small.box', domain="[('state','=','active')]")
    small_description = fields.Char("Description")
    small_responsible = fields.Char("User")
    small_debit_account = fields.Float('Account debit')
    small_debit_account_increase = fields.Float(compute='_debt_account', string='otro')
    id_temp = fields.Integer()
    small_daily_name = fields.Char('account.journal')
    small_period_name = fields.Char('account.period')
    small_accounting_account = fields.Char("Account")
    small_transitory_account = fields.Char("Transitory")
    replacement_diary = fields.One2many('account.move.line', 'id_account_small')
    date_invoice = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    total_amount = fields.Float(compute='_compute_sum', string='Amount consumed')
    small_amount_consumed = fields.Float(compute='_compute_res', string='Balance available')
    STATES = [('inactive', 'Inactive'),
              ('active', 'Active')]
    state = fields.Selection(STATES, string='State', index=True, readonly=True, default='inactive',
                             track_visibility='onchange', copy=False, select=True)

    @api.model
    def create(self, values):
        if self:
            raise Exception.except_orm(("Warning!"), ("Debe Selecionar la Caja Chica"))
        if values:
            if values.get('small_box') == False:
                raise Exception.except_osv(("Warning!"), ("Debe Selecionar la Caja Chica"))
            else:
                compare = values.get('small_box')
                ids = self.search([('small_box', '=', compare)])
                if ids:
                    raise Exception.except_osv(("Warning!"), ("La Caja chica ya esta activa "))
                else:
                    values['state'] = 'active'
                    record = super(small_replacement,self).create(values)
                    return record


    @api.onchange('replacement_code')
    def consecutive(self):
        ids = self.search([(1, '=', 1)], order='replacement_code desc', limit=1)
        if ids:
            prefix = "NCCH-"
            sequence = ids.replacement_code.split('-')
            sec_num = int(sequence[1]) + 1
            series = sec_num
            self.replacement_code = prefix + str(series).rjust(3, '0')
        else:
            series = 1
            prefix = "NCCH-"
            self.replacement_code = prefix + str(series).rjust(3, '0')

    @api.onchange('small_box')
    def _debt(self):
        account_id = self.small_box.id
        ids = self.env['account.validate.small.box'].search([('id', '=', account_id)])
        for item in ids:
            self.small_responsible = item.small_responsible
            self.small_description = item.small_description
            self.small_debit_account = item.small_debit_account
            #self.small_balance_available = item.total_result
            self.small_daily_name = item.small_daily_name
            self.small_period_name = item.small_period_name
            self.small_accounting_account = item.small_accounting_account
            self.small_transitory_account = item.small_transitory_account
            self.id_temp = item.small_box
            id_temp = item.small_box
            self.env['account.small.tmp'].create({'id_temp': id_temp})


    @api.one
    def save(self):
        if self.total_amount > self.small_debit_account:
            raise Exception.except_osv(("Warning!"),
                                 (" La cantidad de dinero ingresada es mayor a la de la cuenta contable"))
        else:
            selec = self.env['account.small.transactions'].search([('selection', '=', True)])
            if selec:
                for selec in selec:
                    journal_id = self.small_daily_name
                    journal_id = self.env['account.journal'].search([('name', '=', journal_id)])
                    journal_id = journal_id.id
                    period_id = self.small_period_name
                    period_id = self.env['account.period'].search([('name', '=', period_id)])
                    period_id = period_id.id
                    consecutive = self.replacement_code
                    date = self.replacement_date
                    small_transitory_account = self.small_transitory_account
                    id_account = self.env['account.account'].search([('code', '=', small_transitory_account)])
                    account_id_trans = id_account.id
                    selection = selec.selection
                    state = selec.state
                    if state != "posted" :
                        id = selec.id
                        account_id = selec.account_small_type_expense.id_type_expense.id
                        partner_id = selec.provider.id
                        total = selec.total_amount
                        self.env['account.small.transactions'].search([('id', '=', id)]).write({'state': "posted"})
                        status = self.env['account.small.transactions'].search([('state', '=', "posted")])
                        if status:
                            search = self.env['account.move'].search([('name', '=', consecutive)])
                            if search:
                                for item2 in search:
                                    move_id = item2.id
                                    create_uid = item2.create_uid.id
                                    company_id = item2.company_id.id
                                    write_uid = item2.write_uid.id
                                    date = item2.date
                                    name = item2.name

                                    insert_account_move_line_debit = {
                                        'company_id': company_id,
                                        'partner_id' : partner_id,
                                        'blocked': "FALSE",
                                        'create_uid': create_uid,
                                        'credit': 0.00,
                                        'centralisation': "normal",
                                        'journal_id': journal_id,
                                        'state': "draft",
                                        'debit': total,
                                        'account_id': account_id,
                                        'period_id': period_id,
                                        'date_create': date,
                                        'date': date,
                                        'write_uid': write_uid,
                                        'move_id': move_id,
                                        'name': name,
                                        'tax_amount': 0.00,
                                        'amount_currency': 0.00,
                                        'id_account_small': id
                                    }


                                    self.env['account.move.line'].create(insert_account_move_line_debit)

                                    insert_account_move_line_credit = {
                                        'company_id': company_id,
                                        'partner_id': partner_id,
                                        'blocked': "FALSE",
                                        'create_uid': create_uid,
                                        'credit': total,
                                        'centralisation': "normal",
                                        'journal_id': journal_id,
                                        'state': "draft",
                                        'debit': 0.00,
                                        'account_id': account_id_trans,
                                        'period_id': period_id,
                                        'date_create': date,
                                        'date': date,
                                        'write_uid': write_uid,
                                        'move_id': move_id,
                                        'name': name,
                                        'tax_amount': 0.00,
                                        'amount_currency': 0.00,
                                        'id_account_small': id
                                    }

                                    self.env['account.move.line'].create(insert_account_move_line_credit)

                            else:
                                insert_account_move = {
                                    'name': consecutive,
                                    'partner_id': partner_id,
                                    'company_id': 1,
                                    'journal_id': journal_id,
                                    'state': "posted",
                                    'period_id': period_id,
                                    'date': date
                                }

                                self.env['account.move'].create(insert_account_move)

                                search = self.env['account.move'].search([('name', '=', consecutive)])
                                if search:
                                    for item2 in search:
                                        move_id = item2.id
                                        create_uid = item2.create_uid.id
                                        company_id = item2.company_id.id
                                        write_uid = item2.write_uid.id
                                        date = item2.date
                                        name = item2.name

                                        insert_account_move_line_debit = {
                                            'company_id': company_id,
                                            'partner_id': partner_id,
                                            'blocked': "FALSE",
                                            'create_uid': create_uid,
                                            'credit': 0.00,
                                            'centralisation': "normal",
                                            'journal_id': journal_id,
                                            'state': "draft",
                                            'debit': total,
                                            'account_id': account_id,
                                            'period_id': period_id,
                                            'date_create': date,
                                            'date': date,
                                            'write_uid': write_uid,
                                            'move_id': move_id,
                                            'name': name,
                                            'tax_amount': 0.00,
                                            'amount_currency': 0.00,
                                            'id_account_small': id
                                        }

                                        self.env['account.move.line'].create(insert_account_move_line_debit)

                                        insert_account_move_line_credit = {
                                            'company_id': company_id,
                                            'partner_id': partner_id,
                                            'blocked': "FALSE",
                                            'create_uid': create_uid,
                                            'credit': total,
                                            'centralisation': "normal",
                                            'journal_id': journal_id,
                                            'state': "draft",
                                            'debit': 0.00,
                                            'account_id': account_id_trans,
                                            'period_id': period_id,
                                            'date_create': date,
                                            'date': date,
                                            'write_uid': write_uid,
                                            'move_id': move_id,
                                            'name': name,
                                            'tax_amount': 0.00,
                                            'amount_currency': 0.00,
                                            'id_account_small': id
                                        }

                                        self.env['account.move.line'].create(insert_account_move_line_credit)
                        else:
                            raise Exception.except_osv(("Warning!"), ("No se realizo el ingreso del registro de la factura"))
                    else:
                        selec = self.env['account.small.transactions'].search([('selection', '!=', True)])
                        if selec:
                            raise Exception.except_osv(("Warning!"), ("Debe tildar el campo de seleccion no tildado"))
            else:
                raise Exception.except_osv(("Warning!"), ("Debe tildar el campo de seleccion no tildado"))


    @api.multi
    def delete(self):
        busq = self.env['account.small.transactions'].search([('delete', '=', True)])
        if busq:
            for busq in busq:
                id = busq.id
                id_one2many = []
                id_one2many.append(id)
                self.env.cr.execute("delete from account_small_transactions where id=%s",id_one2many)
                id_account = self.env['account.move.line'].search([('id_account_small', '=', id)])
                for id_account in id_account:
                    id_account = id_account.id
                    if id_account:
                        ids = []
                        ids.append(id_account)
                        self.env.cr.execute("delete from account_move_line where id=%s", ids)
        else:
            raise Exception.except_osv(("Warning!"),
                                 ("Debe tildar el campo de Delete no tildado"))



    @api.multi
    @api.depends('replacement_transactions.total_amount')
    def _compute_sum(self):
        for l in self:
            l.total_amount = sum(line.total_amount for line in l.replacement_transactions)

    @api.multi
    @api.depends('total_amount', 'small_debit_account')
    def _compute_res(self):
        self.small_amount_consumed =  self.small_debit_account - self.total_amount

    @api.onchange('small_box')
    def _debt_account(self):
        if self:
            sum_debit_account = 0.00
            small_accounting_account = self.small_accounting_account
            small_accounting_account = self.env['account.account'].search([('code', '=',small_accounting_account)])
            if small_accounting_account:
                small_accounting_account = small_accounting_account.id
                account_move_obj = self.env['account.move.line']
                ids = account_move_obj.search([('account_id', '=', small_accounting_account)])
                for item in ids:
                    sum_debit_account = sum_debit_account + item.debit
                    self.small_debit_account_increase = sum_debit_account
                if self.small_debit_account_increase != self.small_debit_account:
                    raise Exception.except_osv(("Warning!"),
                                (" La caja chica posee un aumento se debe validar el efctivo"))


class small_transactions(models.Model):
    _name = 'account.small.transactions'

    STATES = [('draft', 'Draft'),
              ('posted', 'Posted')]
    small_box = fields.Many2one('account.validate.small.box', domain="[('state','=','active')]")

    # Datos para insertar en account move line

    selection = fields.Boolean('selection')
    name = fields.Many2one('account.small.document.type', "Document type")
    partner_id = fields.Integer('Res.user')
    account_small_type_expense = fields.Many2one('account.small.type.expense')
    date = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    document_number = fields.Char('N°document')
    control_number = fields.Char('N° control')
    provider = fields.Many2one('res.partner', "Provider")
    taxable = fields.Float('Taxable amount')
    iva = fields.Float('Iva')
    total_amount = fields.Float(compute='_result', string='Total', store=True)
    state = fields.Selection(STATES, string='State', index=True, readonly=True, default='draft',
                             track_visibility='onchange', copy=False, select=True)
    delete = fields.Boolean('delete')
    id_replacement = fields.Many2one('account.small.replacement')



    @api.onchange('name')
    def _debt(self):
        id_tem = self.env['account.small.tmp'].search([])
        for item in id_tem:
            id_tem = item.id_temp
        id_small = self.env['account.small'].search([('id','=',id_tem)])
        for iten in id_small:
            id_small_box = iten.id
            domain = [('id_small_box', '=', id_small_box)]
            return {'domain': {'account_small_type_expense': domain}}

    @api.multi
    @api.depends('taxable', 'iva')
    def _result(self):
        for l in self:
            l.total_amount = float(l.taxable) + float(l.iva)

class account_small_tmp(models.Model):
    _name = 'account.small.tmp'
    id_temp = fields.Integer()

class small_Provider(models.Model):
    _name = 'account.small.provider'

    name = fields.Char('Name')
    provider_code = fields.Char('Description')
    provider_date = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    provider_rif = fields.Char('RIF')

class small_document_type(models.Model):
    _name = 'account.small.document.type'
    name = fields.Char('Document type')

    @api.model
    def create(self, values):
        if values:
            if values.get('name') == False:
                raise Exception.except_osv(("Warning!"), ("Debe crear un tipo de Documento"))
            else:
                compare = values.get('name')
                ids = self.search([('name', '=', compare)])
                if ids:
                    raise Exception.except_osv(("Warning!"), ("El Documento ya esta creado "))
        record = super(small_document_type, self).create(values)
        return record


class account_move_line(models.Model):
    _inherit = 'account.move.line'
    id_account_small = fields.Integer("DNI")

class account_move(models.Model):
    _inherit = 'account.move'
    id_account_small_move = fields.Integer("DNI")









