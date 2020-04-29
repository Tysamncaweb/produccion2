# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import Warning

class Account_petty_cash(models.Model):
    _name = 'account.petty.cash'
    _description = 'Register small box'

    STATES = [('draft', 'Draft'),
              ('approved', 'Approved'),
              ('validate', 'Validate'),
              ('change', 'Change')]

    name = fields.Char('Código',default= "/")
    petty_cash_description = fields.Char('Descripción')
    petty_cash_responsible_id = fields.Many2one('res.users', string="Responsable", help="Usuario responsable de la caja chica")
    petty_cash_currency_id = fields.Many2one('res.currency', string='Moneda')
    petty_cash_account_id = fields.Many2one('account.account', "Cuenta Contable",
                                       help="Cuenta contable de la caja chica")
    petty_cash_trans_account_id = fields.Many2one('account.account', "Cuenta Transitoria",
                                                  help = "Cuenta contable transitoria de la caja chica ")
    petty_cash_status = fields.Selection(STATES, string='Estado',readonly=True, copy=False, default='draft')
    petty_cash_date = fields.Date(string='Fecha',help="Fecha de creación de la caja chica")
    petty_cash_move_id= fields.Many2one("account.move",string="Asiento Contable",help="asiento de apertura de la caja chica")
    petty_cash_move_reconcile = fields.One2many('account.move.line', related='petty_cash_move_id.line_ids', string='Asientos contables', readonly=True)
    petty_cash_journal_id = fields.Many2one("account.journal", string="Diario de Caja Chica", help="Diario de la caja chica")
    currency_id = fields.Many2one('res.currency', string='Currency')
    petty_cash_amount_open = fields.Monetary("Monto de Apertura", default=None, help="Saldo de apertura de la caja chica")
    petty_cash_bank_id = fields.Many2one('account.journal', string='Banco')
    #sure = fields.Boolean(default=False)
    petty_cash_amount_new = fields.Monetary('New Amount petty cash')
    #currency_id = fields.Many2one('res.currency', string='Currency')

    disponible = fields.Monetary('Saldo Disponible')


    @api.multi
    def validate_petty_cash_amount_open(self):
        if self.petty_cash_amount_open <= 0:
            raise Warning(_('El monto de apertura debe ser mayor que cero'))
        else:
            self.disponible = self.petty_cash_amount_open
        return True


    def _get_company(self):
        uid = self._uid
        res_company = self.env['res.company'].search([('id', '=', uid)])
        return res_company

    def _get_sequence_code(self):
        '''metodo que crea el codigo de la caja chica si la secuencia no esta creada crea una con el
        nombre: 'l10n_petty_cash'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_petty_cash'
        company_id= self._get_company()
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        self.name = IrSequence.next_by_code(SEQUENCE_CODE)

        # if a sequence does not yet exist for this company create one
        if not self.name:
            IrSequence.sudo().create({
                'prefix' : 'CCH',
                'name': 'Localización Venezolana Caja Chica %s' % company_id.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': company_id.id,
            })
            self.name = IrSequence.next_by_code(SEQUENCE_CODE)
        return self.name

    @api.one
    def confirm_petty_cash(self):

        petty_cash = self.env['account.petty.cash'].search([('petty_cash_account_id', '=', self.petty_cash_account_id.id),
                                                                ('petty_cash_status','=', ['approved','validate'])])
        if petty_cash:
            raise Warning(_('Ya existe una Caja Chica con esta Cuenta Transitoria'))
        else:

            '''metodo que cambia el estatus de la caja chica de borrador a aprobado'''
            code = self._get_sequence_code()
            self.write({'petty_cash_status': "approved",'name':code})



    @api.multi
    def validate_petty_cash(self):
        '''se crea el asiento contable para crear el asiento de apertura de la caja chica'''
        self.validate_petty_cash_amount_open()

        vals = {
            'name': self.name,
            'date': self.petty_cash_date,
            'journal_id': self.petty_cash_journal_id.id,
            'state': 'posted',
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)
        company_id= self._get_company()

        self.move_petty_cash_ = {
            'account_id': self.petty_cash_bank_id.default_debit_account_id.id,
            'company_id': company_id.id,
            'currency_id': self.petty_cash_currency_id.id,
            'date_maturity': False,
            'ref': self.petty_cash_description,
            'date': self.petty_cash_date,
            #'partner_id': self.partner_id.id,
            'move_id': move_id.id,
            'name': self.name,
            'journal_id': self.petty_cash_journal_id.id,
            'credit':  self.petty_cash_amount_open,
            'debit':0.0,
        }

        asiento = self.move_petty_cash_
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)

        asiento['account_id'] = self.petty_cash_account_id.id
        asiento['credit'] = 0.0
        asiento['debit'] = self.petty_cash_amount_open

        move_line_id2 = move_line_obj.create(asiento)

        if move_line_id1 and move_line_id2:
                res = {'petty_cash_status': 'validate',
                       'petty_cash_move_id': move_id.id,
                       'petty_cash_amount_open': self.petty_cash_amount_open,
                       'name':self.name}
                super(Account_petty_cash, self).write(res)
        return True

    def change_amount_petty_cash(self):
        #if self.sure == False:
        #    res = {'sure':'True'}
        #    super(Account_petty_cash,self).write(res)

        #if self.petty_cash_amount_new == 0:
        #    raise exceptions.Warning(_('El monto no puede ser cero'))
        pass

