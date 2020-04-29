# -*- coding: utf-8 -*-

from odoo import api, fields, models
from .import num2cad

class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('amount_total')
    def _convert_amount(self):
        #result=dict.fromkeys(self._ids, False)
        for obj in self:
            if obj.amount_total:
                monto=str(obj.amount_total)
                cadena= num2cad.EnLetras(monto)
                letra = cadena.escribir
                obj.monto_letra= letra
            else:
                obj.monto_letra = False
            #return result
    monto_letra = fields.Char(string='Monto En Letra',compute='_convert_amount')



#class hr_contract(models.Model):
 #       _inherit = "hr.contract"

# funciom monto en letra
  #      @api.multi
   #     @api.depends('wage')
    #    def _conver_mont(self):
     #       for obj in self:
      #          if obj.wage:
       #             monto = str(obj.wage)
        #            cadena = num2cad.EnLetras(monto)
         #           letra = cadena.escribir
          #          obj.wage_Letter = letra
           #     else:
            #        obj.wage_Letter = False

     #   wage_Letter = fields.Char(string='Salario en letra', compute='_conver_mont', store='True')




