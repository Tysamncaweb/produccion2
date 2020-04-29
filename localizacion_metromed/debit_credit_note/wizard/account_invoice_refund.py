# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, api
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from odoo.osv.orm import browse_null
# Commented due to migration process, please when this module is migrated to v8
# to ensure the functionaliity is working bring alive this import.
# import workflow


class AccountInvoiceRefund(models.TransientModel):

    """Refunds invoice"""
    _inherit = 'account.invoice.refund'

    @api.one
    def _get_journal(self):
        obj_journal = self.env['account.journal']
        user_obj = self.env['res.users']
        if self._context:
            context = self._context
        inv_type = context.get('type', 'out_invoice')
        company_id = user_obj.browse(self._uid).company_id.id
        type = (inv_type == 'out_invoice') and 'sale_refund' or \
               (inv_type == 'out_refund') and 'sale' or \
               (inv_type == 'in_invoice') and 'purchase_refund' or \
               (inv_type == 'in_refund') and 'purchase'
        journal = obj_journal.search([('type', '=', type),
                  ('company_id', '=', company_id)], limit=1,
                  context=context)
        return journal and journal[0] or False

    @api.one
    def _get_orig(self, inv):
        """Return  default origin value
        """
        nro_ref = ''
        if inv.type == 'out_invoice':
            nro_ref = inv.number
        orig = _('INV REFUND:') + (nro_ref or '') + _('- DATE:') + (
            inv.date_invoice or '') + (' TOTAL:' + str(inv.amount_total) or '')
        return orig

    @api.one
    def compute_refund(self, mode='refund'):
        """@param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs
        """
        inv_obj = self.env['account.invoice']
        account_m_line_obj = self.env['account.move.line']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        res_users_obj = self.env['res.users']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(self._uid).company_id
            journal_id = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise ValidationError(_('Cannot %s draft/proforma/cancel '
                                            'invoice.' % (mode)))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise ValidationError(_('Cannot %s invoice which is '
                                            'already reconciled, invoice '
                                            'should be unreconciled first, '
                                            'You can only refound this '
                                            'invoice.') % (mode))

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form.date:
                    date = form.date
                else:
                    date = inv.date_invoice

                description = form.description or inv.name

                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)

                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            account_m_line_obj += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    refund = inv_obj.browse(refund.id)
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            account_m_line_obj += tmpline
                    account_m_line_obj.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                            'parent_id': inv.id
                        })
                        for field in inv_obj._get_refund_common_fields():
                            if inv_obj._fields[field].type == 'many2one':
                                invoice[field] = invoice[field] and invoice[field][0]
                            else:
                                invoice[field] = invoice[field] or False
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
            '''
            xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                     inv.type == 'out_refund' and 'action_invoice_tree1' or \
                     inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                     inv.type == 'in_refund' and 'action_invoice_tree2'
            subject = _("Credit Note")
            body = description
            refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            #invoice_domain.append(('id', 'in', created_inv))
            #result['domain'] = invoice_domain
            return True
            '''
        return True

    def invoice_refund(self):
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        return self.compute_refund(data_refund)
