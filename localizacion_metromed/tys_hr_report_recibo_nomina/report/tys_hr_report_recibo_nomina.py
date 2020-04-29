from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.tys_hr_report_recibo_nomina.template_hr_payroll_summary_report'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip.run'].browse(docids)}
        res = dict()
        docs = []

