# coding: utf-8

from odoo.exceptions import UserError
from odoo import models, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def split_invoice(self):
        """
        Split the invoice when the lines exceed the maximum set for the company
        """
        for inv in self:
            if inv.company_id.lines_invoice < 1:
                #raise UserError(_('The number of customer invoice lines must be at least one'))
                raise exceptions.except_orm(_('Error !'),
                    _('Please set an invoice lines value in:\n''Administration->Company->Configuration->Invoice lines'))
            if inv.type in ["out_invoice", "out_refund"]:
                if len(inv.invoice_line_ids) > inv.company_id.lines_invoice:
                        raise exceptions.except_orm(_('Error !'),
                                                    _('Please set an invoice lines value in:\n''Administration->Company->Configuration->Invoice lines'))
                   # inv.compute(date_ref=True)
                   # new_inv.compute(date_ref=True)

        return True

    @api.multi
    def action_date_assign(self):
        """ Return assigned dat
        """
        super(AccountInvoice, self).action_date_assign()
        self.split_invoice()
        return True
