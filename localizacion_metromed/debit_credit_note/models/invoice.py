# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api
from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    parent_id = fields.Many2one('account.invoice', 'Parent Invoice',
                                #readonly=True,
                                states={'draft': [('readonly', False)]},
                                help='''This is the main invoice that has
                                generated this credit note
                                ''')
    child_ids = fields.One2many('account.invoice', 'parent_id',
                                'Debit and Credit Notes', #readonly=True,
                                states={'draft':[('readonly', False)]},
                                help='''These are all credit and debit
                                to this invoice
                                ''')

    @api.one
    def copy(self, default={}):
        """ Allows you to duplicate a record,
        child_ids, nro_ctrl and reference fields are
        cleaned, because they must be unique
        """
        default.update({
            'child_ids': [],
        })
        return super(AccountInvoice, self).copy(default)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('price_unit')
    def _change_price_unit(self):
        '''
        Se usa este metodo para evitar que, al generar una nota de credito, se coloque un monto superior al de la
        factura original.
        '''
        res = {}
        if self.invoice_id.type in ['in_refund', 'out_refund']:
            line_id = self._origin._ids[0]
            query = "SELECT price_unit FROM account_invoice_line WHERE id=%s" % (line_id)
            self.env.cr.execute(query)
            valor_original = self.env.cr.fetchall()[0][0]
            monto = self.price_unit
            res = {'value': {'price_unit': valor_original}}
            if monto > valor_original:
                res.update({'warning': {'title': "¡Advertencia!", 'message': "No puede ingresar un monto mayor al de "
                                        "la factura origina!"}})
            else:
                res['value']['price_unit'] = monto
        return res