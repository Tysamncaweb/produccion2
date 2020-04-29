# coding: utf-8
from odoo import fields, models, api

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'

    STATES_VALUES = [
            ('draft', 'Draft'),
            ('done', 'Confirmado'),
            ('close', 'Close'),
        ]

    state = fields.Selection(STATES_VALUES, 'Status', select=True, readonly=True, copy=False)

    @api.multi
    def hr_payslip_multi(self):

        for payslip in self.slip_ids:
            payslip.action_payslip_done()
        return self.write({'paid': True, 'state': 'done'})

