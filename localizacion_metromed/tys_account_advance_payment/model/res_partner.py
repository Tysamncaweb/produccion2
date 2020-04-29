# coding: utf-8
###########################################################################

from odoo import models, fields


class res_partner(models.Model):
    '''Se crea dos campos para agregar a la ficha del cliente y proveedor las cuentas
     contables de anticipo a cliente y proveedor'''

    _inherit = 'res.partner'

    account_advance_payment_purchase_id = fields.Many2one('account.account','Purchases advance account')
    account_advance_payment_sales_id = fields.Many2one('account.account','Sales advance account')
    journal_advanced_id = fields.Many2one('account.journal','Journal Advanced')

