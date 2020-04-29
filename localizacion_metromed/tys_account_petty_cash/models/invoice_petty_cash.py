# coding: utf-8
###########################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import fields, models, api, exceptions

'''class ResPartner(models.Model):
    _inherit = 'gastos.petty.cash'

    @api.multi
    def name_get(self):
        if self._context is None:
            self._context = {}
        res = []
        if self._context.get('otro_nombre', True):
            for partner in self:
                res.append((partner.id, ("%(parnter_order_count)s  %(parnter_name)s") % {
                    'parnter_order_count': partner.cta_contable,
                    'parnter_name': partner.name
                }))
        else:
            for record in self:
                res.append((record.id, ("%(parnter_name)s") % {
                    'parnter_name': record.name
                }))
        return res'''
class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    factura_id = fields.Many2one('invoice.petty.cash')

class Invoice_petty_cash(models.Model):
    _name = 'invoice.petty.cash'
    _description = 'Invoice petty cash'


    TYPE_PETTY_CASH = [('invoice', 'Factura'),
                       ('document', 'Documento'),
                       ('nota', 'Nota de Entrega')]

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('validate', 'Validado'),
        ('cancel', 'Cancelado')], default='draft')

    name = fields.Char('Número')
    code = fields.Many2one('account.petty.cash', 'Caja Chica', ondelete='cascade',
                           help="tildar la opcion para asignar la factura a una caja chica específica")
    transitoria = fields.Many2one('account.account')
    #code_trans = fields.Char('')
    petty_cash_partner = fields.Many2one('res.partner', 'Proveedor', ondelete='cascade',
                                    help="muestra los proveedores")
    rif = fields.Char('Rif', related='petty_cash_partner.vat')

    petty_cash_gastos = fields.Many2one('account.account', 'Tipo de Gasto', ondelete='cascade',
                                         help="muestra los gastos")
    date_petty_cash = fields.Date('Fecha Factura')
    date_account= fields.Date('Fecha Contable')
    cuenta_analitica = fields.Many2one('account.analytic.account', 'Cuenta Analítica')
    etiqueta_analitica = fields.Many2one('account.analytic.tag', 'Etiquetas Analíticas')
    razon_gasto = fields.Text ('Razón del Gasto')
    invoice_nro_ctrl = fields.Char('Número de Control')
    amount_exento = fields.Monetary('Monto Exento')
    amount_total = fields.Monetary('Monto Total')
    amount_gravable = fields.Monetary('Monto Gravable')
    tax = fields.Many2one('account.tax')
   # tax = fields.Many2one('account.tax.group')
    iva = fields.Float('')
    move_id = fields.Many2one("account.move", string="Asiento Contable",
                                         help="asiento de apertura de la factura")
    currency_id = fields.Many2one('res.currency', string='Currency')
    factura_move = fields.Many2one('account.invoice', help="id de la factura que se crea en account invoice(faturas de proveedor)")


    reverse_move_id = fields.Many2one("account.move", string="Asiento de Reversión",
                                         help="asiento de reversion de la factura")

    #campos para saber el saldo disponible de la caja chica
    disponible = fields.Monetary('Monto Disponible Caja Chica')
    apertura = fields. Monetary('Monte de Apertura Caja Chica')



    sin_cred = fields.Boolean(
        'Incluir esta factura en libro de compras', readonly=False,
        help="Set it true if the invoice is VAT excempt (Tax Exempt)")

    petty_cash_account_id = fields.Many2one('account.account', "Account",
                                            help="Cuenta contable de la caja chica")

    type_petty_cash = fields.Selection(TYPE_PETTY_CASH, string='Tipo Documento', default='invoice')



    @api.onchange('code')
    def gastos_petty_cash(self):
        if self.code:
            codigo = self.env['invoice.petty.cash'].search([('code', '=', self.code.id),
                                                                ('state', '=', 'validate')])

            if codigo:
                disponible = codigo[-1].disponible
            else:
                disponible = self.code.disponible

            return {'value': {'transitoria': self.code.petty_cash_trans_account_id.id,
                              'disponible': disponible,
                              'apertura': self.code.petty_cash_amount_open,
                              }}
        #return {'value': {'tax': self.iva_prueba.tax_group_id.name
         #                 }}


    @api.onchange('tax')
    def amount2(self):

       # iva_principal = self.env['account.tax'].search([('tax_group_id', '=', self.tax.id), ('type_tax_use', '=', 'purchase')])

        self.iva = (self.tax.amount * self.amount_gravable) / 100

    @api.onchange('amount_exento')
    def amount3(self):
        if self.amount_exento:
            codigo = self.env['invoice.petty.cash'].search([('code', '=', self.code.id),
                                                            ('state', '=', 'validate')])

            if codigo:
                a = codigo[-1].disponible
            else:
                a = self.code.disponible

            self.disponible = a - self.amount_exento
            if self.disponible < 0:
                raise ValidationError('El Monto Disponible es menor a cero')

            return {'value': {'amount_total': self.amount_exento,
                              }}
        else:
           self.disponible = self.code.disponible


    @api.onchange('amount_gravable', 'tax')
    def amount4(self):
        if self.amount_gravable or self.tax:
            codigo = self.env['invoice.petty.cash'].search([('code', '=', self.code.id),
                                                            ('state', '=', 'validate')])

            if codigo:
                a = codigo[-1].disponible
            else:
                a = self.code.disponible
            self.disponible = a - (self.amount_gravable + self.iva)
            if self.disponible < 0:
                raise ValidationError('El Monto Disponible es menor a cero')
            return {'value': {'amount_total': self.amount_gravable + self.iva,
                          }}
        else:
            self.tax = 0
            self.iva = 0
            self.disponible = self.code.disponible

    @api.onchange('amount_exento', 'amount_gravable', 'tax')
    def amount5(self):
        if self.amount_gravable or self.tax or self.amount_exento:
            if self.amount_gravable:
                codigo = self.env['invoice.petty.cash'].search([('code', '=', self.code.id),
                                                                ('state', '=', 'validate')])

                if codigo:
                    a = codigo[-1].disponible
                else:
                    a = self.code.disponible

                self.disponible = a - (self.amount_exento + self.amount_gravable + self.iva)
                if self.disponible < 0:
                    raise ValidationError('El Monto Disponible es menor a cero')
                return {'value': {'amount_total': self.amount_gravable + self.amount_exento + self.iva
                              }}
            else:
                codigo = self.env['invoice.petty.cash'].search([('code', '=', self.code.id),
                                                                ('state', '=', 'validate')])

                if codigo:
                    a = codigo[-1].disponible
                else:
                    a = self.code.disponible
                self.iva = 0
                self.disponible = a - (self.amount_exento + self.amount_gravable + self.iva)
                return {'value': {'amount_total': self.amount_gravable + self.amount_exento + self.iva
                                  }}
        else:
            self.tax = 0
            self.iva = 0
            self.disponible = self.code.disponible

    def _get_company(self):
        uid = self._uid
        res_company = self.env['res.company'].search([('id', '=', uid)])
        return res_company

    @api.multi
    def sin_fiscal_book(self, cr):

        """
        Añadir Factura en libro de compras"""

        invoice = self.env['invoice.petty.cash'].search([('id', '=', self.ids)])
        invoice.write({'sin_cred': True})

        if self.tax:
            iva = self.iva
            tax = self.tax
            id = self.id
        else:
            iva = 0
            tax = self.env['account.tax'].search([('amount', '=', 0),
                                                  ('type_tax_use', '=', 'purchase')])

        val_invoice = {
            'number': self.type_petty_cash + "/" + self.name,
            'move_name': self.type_petty_cash,
            'supplier_invoice_number': self.name,
            'partner_id': self.petty_cash_partner.id,
            #'rif': self.rif,
            'nro_ctrl': self.invoice_nro_ctrl,
            'date_document': self.date_petty_cash,
            'date_invoice': self.date_account,
            'amount_total': self.amount_total,
            'residual': self.amount_gravable + self.amount_exento + iva,
            'residual_signed': self.amount_total,
            'residual_company_signed': self.amount_total,
            'amount_untaxed': self.amount_total - iva,
            'amount_tax': iva,
            'state': 'open',
            'sin_cred': False,
            'type': 'in_invoice',
            'factura_id': self.id,
        }
        move_obj_invoice = self.env['account.invoice']
        invoice_petty_cash = move_obj_invoice.create(val_invoice)
        company_id = self._get_company()
        self.factura_move = invoice_petty_cash
        uid = self._uid

        invoice_tax = {
            'invoice_id': invoice_petty_cash.id,
            'name': tax.name,
            'tax_id': tax.id,
            'account_id': tax.account_id.id,
            'account_analytic_id': self.cuenta_analitica.id,
            'amount': iva,
            'company_id': company_id.id,
            'base': self.amount_total - iva,
        }
        move_obj_invoice_tax = self.env['account.invoice.tax']
        invoice_tax_petty_cash = move_obj_invoice_tax.create(invoice_tax)

        self.move_invoice_petty_cash_ = {
            'name': self.name,
            'origin': self.name,
            'invoice_id': invoice_petty_cash.id,
            'company_id': company_id.id,
            'account_id': self.petty_cash_gastos.id,
            'ref': self.code.name,
            'account_analytic_id': self.cuenta_analitica.id,
            # 'invoice_line_tax_id': [(6, 0, self.tax.id)],
            'price_unit': self.amount_gravable + self.amount_exento,
            'price_subtotal': self.amount_gravable + self.amount_exento,
            'price_total': self.amount_exento + self.amount_gravable + iva,
        }

        asiento = self.move_invoice_petty_cash_
        move_line_obj = self.env['account.invoice.line']
        move_line_id1 = move_line_obj.create(asiento)

        invoice = self.env['invoice.petty.cash'].search([('id', '=', self.ids)])
        invoice.write({'sin_cred': True})

        self.env.cr.execute(
            """INSERT INTO account_invoice_line_tax
               (invoice_line_id, tax_id)
               VALUES (%s, %s)""", (move_line_id1.id, tax.id))

        if self.etiqueta_analitica:
            self.env.cr.execute(
                """INSERT INTO account_analytic_tag_account_invoice_line_rel
                   (account_invoice_line_id, account_analytic_tag_id)
                   VALUES (%s, %s)""", (move_line_id1.id, self.etiqueta_analitica.id))

    @api.multi
    def validate_invoice_petty_cash(self):


        '''metodo que cambia el estatus de la caja chica de borrador a aprobado'''
        self.write({'state': "validate"})
        petty_cash = self.env['account.petty.cash'].search([('id', '=', self.code.id)])
        petty_cash.write({'disponible': self.disponible})

        #iva_principal = self.env['account.tax'].search([('tax_group_id', '=', self.tax.id), ('type_tax_use', '=', 'purchase')])

        '''se crea el asiento contable para crear el asiento de apertura de las facturas que pertenecen a la caja chica'''
        if self.type_petty_cash == 'invoice':
            type_document = 'FACTURA'
        if self.type_petty_cash == 'document':
            type_document = 'DOCUMENTO'
        if self.type_petty_cash == 'nota':
            type_document = 'NOTA_ENTREGA'

        vals = {
            'name': type_document + "/" + self.name,
            'date': self.date_account,
            'journal_id': self.code.petty_cash_journal_id.id,
            'state': 'posted',
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)
        company_id = self._get_company()

        self.move_petty_cash_ = {
            'account_id': self.transitoria.id,
            'company_id': company_id.id,
            'date_maturity': False,
            'ref': self.code.name,
            'date': self.date_account,
            'partner_id': self.petty_cash_partner.id,
            'analytic_account_id': self.cuenta_analitica.id,
            'move_id': move_id.id,
            'name': self.name,
            'journal_id': self.code.petty_cash_journal_id.id,
            'credit': self.amount_total,
            'debit': 0.0,
        }

        asiento = self.move_petty_cash_
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)


        if self.amount_gravable != 0.00:
            asiento['account_id'] = self.tax.account_id.id
            asiento['credit'] = 0.0
            asiento['debit'] = self.iva

            move_line_id3 = move_line_obj.create(asiento)


        asiento['account_id'] = self.petty_cash_gastos.id
        asiento['credit'] = 0.0
        asiento['debit'] = self.amount_total - self.iva

        move_line_id2 = move_line_obj.create(asiento)


        if move_line_id1 and move_line_id2:
            res = {'move_id': move_id.id,
                   'amount_total': self.amount_total,
                   'name': self.name}
            super(Invoice_petty_cash, self).write(res)


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