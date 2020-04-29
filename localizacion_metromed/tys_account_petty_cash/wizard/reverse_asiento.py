# coding: utf-8
###########################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import fields, models, api, exceptions


class ReverseInvoice_petty_cash(models.Model):
    _name = 'reverse.invoice.petty.cash'
    _description = 'Reverse Invoice petty cash'

    #campos para la reversion del asiento contable
    date = fields.Date('Fecha de Reversión')
    reverse_move_id = fields.Many2one("account.move", string="Asiento de Reversión",
                                         help="asiento de reversion de la factura")

    def asiento_de_reversion(self, docids):
        estado = self.env['invoice.petty.cash'].search([('id', '=', docids['active_id'])])
        petty_cash = self.env['account.petty.cash'].search([('id', '=', estado.code.id)])
        petty_cash.write({'disponible': estado.disponible + estado.amount_total})
        estado.write({'state': 'draft',
                      'sin_cred': False,
                      'date': self.date,
                      'disponible': estado.disponible + estado.amount_total,
                      'amount_exento': 0.00,
                      'amount_gravable': 0.00,
                      'amount_total': 0.00,
                      'iva': 0.00,
                      'tax': 0,
                      })

        factura = self.env['account.invoice'].search([('id', '=', estado.factura_move.id)])
        factura.write({'state': 'cancel'})


        bus = self.env['account.move'].search([('id', '=', estado.move_id.id)])
        reverse_ids = bus.reverse_moves(self.date, bus.journal_id)
        move_id = reverse_ids[0]
        estado.write({'reverse_move_id': move_id})