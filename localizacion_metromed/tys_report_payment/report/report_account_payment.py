from odoo import models, api, _
from odoo.exceptions import UserError, Warning


class ReportAccountPayment(models.AbstractModel):
    _name = 'report.tys_report_payment.template_account_payment'
    # _inherit = 'report.abstract_report'
    # _template = 'l10n_ve_withholding_iva.template_wh_vat'

    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['account.payment'].browse(docids)}
        res = dict()
        return {
            'data': data['form'],
            'model': self.env['report.tys_report_payment.template_account_payment'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
        }


    def _get_islr_invoice_amount_ret(self, ids):

        ids = isinstance(ids, (int)) and [ids] or (isinstance(ids, (list)) and ids) or [ids.id]
        iwsl_obj = self.env['islr.wh.doc.line'].search([('invoice_id', 'in', ids)])
        estado = ''
        amount_ret_local = 0.0

        for i in iwsl_obj:
            estado = i.islr_wh_doc_id.state

        if estado == 'done':
            for i in iwsl_obj:
                amount_ret_local = i.islr_wh_doc_id.amount_total_ret
        return amount_ret_local


    def _get_iva_invoice_amount_ret(self, ids):

        ids = isinstance(id, (int)) and [ids] or (isinstance(ids, (list)) and ids) or [ids.id]

        iwsl_obj = self.env['account.wh.iva.line'].search([('invoice_id', 'in', ids)])

        estado = iwsl_obj.retention_id.state
        amount_ret_local = 0.0

        if estado == 'done':
            for i in iwsl_obj:
                amount_ret_local = i.retention_id.total_tax_ret

        return amount_ret_local
