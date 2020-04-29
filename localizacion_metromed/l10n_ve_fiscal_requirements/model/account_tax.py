# coding: utf-8


from odoo import fields,models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    appl_type = fields.Selection(
            [('exento', 'Exempt'),
             ('sdcf', 'Not entitled to tax credit'),
             ('general', 'General Aliquot'),
             ('reducido', 'Reducted Aliquot'),
             ('adicional', 'General Aliquot + Additional')],
            'Aliquot Type',
            required=False,
            help='Specify the aliquote type for the tax so it can be processed'
                 ' accrordly when the sale/purchase book is generatred')
