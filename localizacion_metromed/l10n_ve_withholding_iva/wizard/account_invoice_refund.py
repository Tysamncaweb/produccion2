# coding: utf-8
##############################################################################



from odoo.osv import osv


class AccountInvoiceRefund(osv.osv_memory):

    """Refunds invoice"""
    _inherit = 'account.invoice.refund'

    def validate_wh(self, cr, uid, ids, context=None):
        """ Method that validate if invoice has non-yet processed VAT withholds.
        return: True: if invoice is does not have wh's or it does have and
                    those ones are validated.
                False: if invoice is does have and those wh's are not yet
                    validated.
        """
        if context is None:
            context = {}
        res = []
        inv_obj = self.pool.get('account.invoice')

        res.append(super(AccountInvoiceRefund, self).validate_wh(
            cr, uid, ids, context=context))
        res.append(inv_obj.validate_wh_iva_done(cr, uid, ids, context=context))
        return all(res)

AccountInvoiceRefund()
