from odoo import models, fields, api



class account_issued_check(models.Model):
    _inherit = 'account.issued.check'



    @api.multi
    def print_check(self, data):


        return self.env.ref('l10n_ve_account_check_duo.report_check_duo').report_action(self, data=data, config=False)