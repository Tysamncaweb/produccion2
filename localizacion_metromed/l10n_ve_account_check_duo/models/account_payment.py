# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class account_abstract_payment(models.AbstractModel):
    _name = "account.abstract.payment"
    _inherit = 'account.abstract.payment'

    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money'),('transfer', 'Internal Transfer')])

    #payment_type_s = fields.Selection([('inbound', 'Cheques de Terceros'),('transfer', 'Internal Transfer')], string="Payment Type", default="inbound")
    defaults_payment_type = fields.Char('defaults_payment_type', default='')

    payment_type_s = fields.Selection(selection="prueba_s",string="Payment Type")

    @api.multi
    def prueba_s(self):
        if self._context.get('default_payment_type'):
            if self._context.get('default_payment_type') == 'inbound':
                return [('inbound', 'Cheques de Terceros'),('transfer', 'Transferencia interna')]
            elif self._context.get('default_payment_type') == 'outbound':
                return [('outbound', 'Enviar dinero'),('inbound', 'Recibir dinero'), ('transfer', 'Transferencia interna')]

    @api.onchange('payment_type_s')
    def guarda_valor(self):
        self.payment_type = self.payment_type_s


    #@api.modelhttps://www.youtube.com/
    #def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
     #   res = super(account_abstract_payment, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
      #  if view_type == 'form' and self._context.get('default_payment_type') and self._context.get('default_payment_type') == 'inbound':
       #     #self.defaults_payment_type = "inbound"
        #    for field in res['fields']:
         #       if field == 'payment_type_s':
          #          valor = res['fields'][field]

        #elif self._context.get('default_payment_type') and self._context.get('default_payment_type') == 'outbound':
         #   self.defaults_payment_type = 'outbound'
        #return res

    #@api.depends('payment_type')
    #def option_type(self):
        #if self.payment_type == 'inbound':

     #       self.payment_type_s = fields.Selection(selection_add=[('inbound', 'Cheques de Terceros')],default="inbound")

        #elif self.payment_type == 'outbound':

         #   self.payment_type_s = fields.Selection(selection_add=[('outbound', ''),('inbound', 'Cheques de Terceros')], default="outbound")





