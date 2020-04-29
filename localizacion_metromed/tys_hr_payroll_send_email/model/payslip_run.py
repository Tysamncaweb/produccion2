# -*- coding: utf-8 -*-

from odoo import fields, api, models

class hr_payslip_run(models.Model):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'

    send = fields.Boolean('Send?', readonly=True)

    @api.multi
    def action_send_email(self):

        template = self.env.ref('tys_hr_payroll_send_email.email_template_slip', False)
        for slip in self.slip_ids:
            if slip.state == 'done':  #esta condicion hace que solo envie las nominas en estado "done"
                template.send_mail(slip.id, force_send=True)
        return True
