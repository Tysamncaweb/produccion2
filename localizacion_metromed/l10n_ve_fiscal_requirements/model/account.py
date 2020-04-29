# coding: utf-8

from odoo import fields,models, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(
            [('sale', 'Sale'), ('sale_refund', 'Sale Refund'),
             ('purchase', 'Purchase'), ('purchase_refund', 'Purchase Refund'),
             ('cash', 'Cash'), ('bank', 'Bank and Cheques'),
             ('general', 'General'),
             ('situation', 'Opening/Closing Situation'),
             ('sale_debit', 'Sale Debit'),
             ('purchase_debit', 'Purchase Debit')],
            'Type', size=32, required=True,
            help="Select 'Sale' for customer invoices journals."
                 " Select 'Purchase' for supplier invoices journals."
                 " Select 'Cash' or 'Bank' for journals that are used in"
                 " customer or supplier payments."
                 " Select 'General' for miscellaneous operations journals."
                 " Select 'Opening/Closing Situation' for entries generated"
                 " for new fiscal years."
                 " Select 'Sale Debit' for customer debit note journals."
                 " Select 'Purchase Debit' for supplier debit note journals.")