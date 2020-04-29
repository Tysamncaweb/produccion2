# -*- coding: utf-8 -*-

from odoo import fields, api, models


class hr_payslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip']

    @api.multi
    def action_send_email(self):

        template = self.env.ref('tys_hr_payroll_send_email.email_template_slip')
        for slip in self:
            template.send_mail(slip.id, force_send=True)
        return True
