# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import Warning

class Replacement_petty_cash(models.Model):
    _name = 'replacement.petty.cash'
    _description = 'Replacement petty cash'

    petty_cash_status = fields.Selection([
        ('process', 'En Proceso'),
        ('close', 'Cerrado'),
        ('liquidado', 'Liquidado')], default='process')


    name = fields.Char('Número',default= "/", readonly=True)
    code = fields.Many2one('account.petty.cash','petty cash', ondelete='cascade', required=True,
                                    help="tildar la opcion para asignar la factura a una caja chica específica")
    petty_cash_bank_id = fields.Many2one('account.journal', string='Banco')
    date = fields.Date('Fecha de Apertura', required=True)
    description = fields.Text('Descripción')
    responsable = fields.Char('Responsable')
    apertura = fields.Monetary('Monto de Apertura')
    consumido = fields.Monetary('Monto Consumido')
    disponible = fields.Monetary('Saldo Disponible')
    transitoria = fields.Many2one('account.account')
    facturas_ids = fields.Many2many('invoice.petty.cash', string='Facturas')
    amount_exento = fields.Monetary('Total Exento', store=True, track_visibility='always')


    amount_gravable = fields.Monetary('Total Gravable', store=True, track_visibility='always')
    amount_tax = fields.Monetary('Total IVA', store=True, track_visibility='always')
    amount_total = fields.Monetary('Total Factura', store=True, track_visibility='always')
    comment = fields.Text('Observaciones')
    residual = fields.Monetary('Saldo',  store=True, help="Remaining amount due.")


    move_id = fields.Many2one("account.move", string="Asiento Contable",
                                         help="asiento de apertura de la caja chica")
    currency_id = fields.Many2one('res.currency', string='Currency')


    @api.onchange('code')
    def petty_cash(self):
        if self.code:
            codigo = self.env['replacement.petty.cash'].search([('code', '=', self.code.id),
                                                                ('petty_cash_status', '=', 'close')])

            if codigo:
                self.disponible = codigo[-1].disponible
                self.consumido = codigo[-1].consumido
            else:
                self.disponible = codigo.disponible
                self.consumido = codigo.consumido



            return {'value': {'description': self.code.petty_cash_description,
                              'responsable': self.code.petty_cash_responsible_id.name,
                              'apertura': self.code.petty_cash_amount_open,
                              'transitoria': self.code.petty_cash_trans_account_id.id,
                              }}


    @api.onchange('facturas_ids')
    def _compute_amount(self):
        self.amount_exento = 0
        self.amount_tax = 0
        self.amount_gravable = 0
        self.amount_total = 0
        codigo = self.env['replacement.petty.cash'].search([('code', '=', self.code.id),
                                                            ('petty_cash_status', '=', 'close')])

        if codigo:
            self.disponible = codigo[-1].disponible
            self.consumido = codigo[-1].consumido
        else:
            self.disponible = 0
            self.consumido = 0
        a=0
        b=0

        for tax_line in self.facturas_ids:

            self.amount_exento = tax_line.amount_exento + self.amount_exento
            self.amount_gravable = tax_line.amount_gravable + self.amount_gravable
            self.amount_tax = tax_line.iva + self.amount_tax
            self.amount_total = tax_line.amount_total + self.amount_total
            codigo = self.env['replacement.petty.cash'].search([('code', '=', self.code.id),
                                                                ('petty_cash_status', '=', 'close')])

            if codigo:
                a = codigo[-1].disponible
                b = codigo[-1].consumido
            else:
                a = codigo.disponible
                b = codigo.consumido

            self.consumido = b + self.amount_total
            if a == 0:
                self.disponible = self.apertura - self.amount_total
            else:
                self.disponible = a - self.amount_total

        if self.consumido > self.apertura:
            raise ValidationError('El Saldo Consumido no puede ser Mayor al Saldo de Apertura de la Caja Chica')

        self.residual = self.amount_total

    def _get_company(self):
        uid = self._uid
        res_company = self.env['res.company'].search([('id', '=', uid)])
        return res_company


    def _get_sequence_code(self):
        '''metodo que crea el codigo de la caja chica si la secuencia no esta creada crea una con el
        nombre: 'l10n_petty_cash'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_replacement_petty_cash'
        company_id= self._get_company()
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        self.name = IrSequence.next_by_code(SEQUENCE_CODE)

        # if a sequence does not yet exist for this company create one
        if not self.name:
            IrSequence.sudo().create({
                'prefix' : '',
                'name': 'Localización Venezolana Caja Chica %s' % company_id.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': company_id.id,
            })
            self.name = IrSequence.next_by_code(SEQUENCE_CODE)
        return self.name

    @api.multi
    def confirm_replacement(self):
        '''metodo que cambia el estatus de la reposición de En proceso a cerrado'''
        code = self._get_sequence_code()
        self.write({'petty_cash_status': "close", 'name': code})

        if self.facturas_ids:
            for factura in self.facturas_ids:
                estado = self.env['invoice.petty.cash'].search([('id', '=', factura.id)])
                estado.write({'state': 'cancel'})
            return estado
        else:
            raise ValidationError('Por favor, Ingrese algunas Facturas')

    @api.multi
    def replacement_petty_cash(self):

        amount_disponible = self.env['account.petty.cash'].search([('id', '=', self.code.id),
                                                        ('petty_cash_status', '=', 'validate')])
        amount_disponible.write({'disponible': amount_disponible.disponible + self.amount_total})

        '''se crea el asiento contable para crear el asiento de de liquidación en la reposición de la caja chica'''

        vals = {
            'name': self.name,
            'date': self.date,
            'journal_id': self.code.petty_cash_journal_id.id,
            'state': 'posted',
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)
        company_id = self._get_company()

        self.move_petty_cash_ = {
            'account_id': self.petty_cash_bank_id.default_debit_account_id.id,
            'company_id': company_id.id,
            'date_maturity': False,
            'ref': self.code.name,
            'date': self.date,
            'partner_id': self.code.petty_cash_responsible_id.id,
            'move_id': move_id.id,
            'name': self.name,
            'journal_id': self.code.petty_cash_journal_id.id,
            'credit': self.amount_total,
            'debit': 0.0,
        }

        asiento = self.move_petty_cash_
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)


        asiento['account_id'] = self.transitoria.id
        asiento['credit'] = 0.0
        asiento['debit'] = self.amount_total

        move_line_id2 = move_line_obj.create(asiento)

        if move_line_id1 and move_line_id2:
            res = {'petty_cash_status': 'liquidado',
                   'move_id': move_id.id,
                   'amount_total': self.amount_total,
                   'name': self.name}
            super(Replacement_petty_cash, self).write(res)

        return True








