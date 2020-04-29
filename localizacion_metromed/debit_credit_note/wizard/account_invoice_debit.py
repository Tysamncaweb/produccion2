# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError

class AccountInvoiceDebit(models.TransientModel):

    """Debits Note from Invoice"""

    _name = "account.invoice.debit"
    _description = "Invoice Debit Note"
    date = fields.Date('Operation Date',
                       help='''This date will be used as the invoice date
                       for Refound Invoice and Period will be chosen
                       accordingly!
                       ''', default=lambda *t: time.strftime('%Y-%m-%d'))
    period = fields.Date('Period', default=lambda *t: time.strftime('%Y-%m-%d'))

    @api.onchange('date')
    def _get_journal(self):
        obj_journal = self.env['account.journal']
        user_obj = self.env['res.users']
        context = dict(self._context or {})
        inv_type = self._context.get('type', 'out_invoice')
        company_id = user_obj.browse(self._uid).company_id.id
        type = (inv_type == 'out_invoice') and 'sale' or \
               (inv_type == 'out_refund') and 'sale' or \
               (inv_type == 'in_invoice') and 'purchase' or \
               (inv_type == 'in_refund') and 'purchase'
        journal = obj_journal.search([('type', '=', type),
                                      ('company_id', '=', company_id)], limit=1)
        self.journal_id = journal and journal[0] or False

    journal_id = fields.Many2one('account.journal',
                                 'Refund Journal',
                                 help='''You can select here the journal
                                 to use for the refund invoice
                                 that will be created. If you
                                 leave that field empty, it will
                                 use the same journal as the
                                 current invoice.
                                 ''')
    description = fields.Char('Description', size=128, required=True)
    comment = fields.Text('Comment', required=True)

    @api.one
    def _get_orig(self, inv, ref):
        """Return  default origin value
        """
        nro_ref = ref
        if inv.type == 'out_invoice':
            nro_ref = inv.number
        orig = _('INV:') + (nro_ref or '') + _('- DATE:') + (
            inv.date_invoice or '') + (' TOTAL:' + str(inv.amount_total) or '')
        return orig

    @api.one
    def compute_debit(self):
        """@param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        inv_obj = self.env['account.invoice']
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        res_users_obj = self.env['res.users']
        context = dict(self._context or {})
        invoice = {}

        for form in self:
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(self._uid).company_id
            journal_id = form.journal_id.id
            for inv in inv_obj.search([('id','=',self._context.get('active_ids'))]):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise ValidationError(_('Can not create a debit note from '
                                            'draft/proforma/cancel invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise ValidationError(_('Cannot %s invoice which is already '
                                            'reconciled, invoice should be '
                                            'unreconciled first. You can only '
                                            'refound this invoice.') % (mode))

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form.date:
                    date = form.date
                else:
                    date = inv.date_invoice
                if form.description:
                    description = form.description
                else:
                    description = inv.name

                invoice_lines = inv_line_obj.browse(inv.id)
                invoice_lines = inv_obj._refund_cleanup_lines(invoice_lines)
                tax_lines = inv_tax_obj.search([('invoice_id','=',inv.id)])
                tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                # Add origin, parent and comment values
                orig = self._get_orig(inv, inv.reference)
                invoice.update({
                    'type': inv.type == 'in_invoice' and 'in_refund' or
                            inv.type == 'out_invoice' and 'out_refund',
                    'date_invoice': date,
                    'state': 'draft',
                    'number': False,
                    'invoice_line': invoice_lines,
                    'tax_line': tax_lines,
                    'period': period,
                    'parent_id': inv.id,
                    'name': description,
                    'origin': orig,
                    'comment': form['comment'],
                    'partner_id': False,
                    'account_id': False,
                    'currency_id': False,
                    'payment_term_id': False,
                    'journal_id': False
                })

                invoice.update({'partner_id': (inv.partner_id and inv.partner_id.id)  and inv.partner_id.id})
                invoice.update({'account_id': (inv.account_id and inv.account_id.id) and inv.account_id.id})
                invoice.update({'currency_id': (inv.currency_id and inv.currency_id.id) and inv.currency_id.id})
                invoice.update({'payment_term_id': (inv.payment_term_id and inv.payment_term_id.id) and inv.payment_term_id.id})
                invoice.update({'journal_id': (inv.journal_id and inv.journal_id.id) and inv.journal_id.id})
                inv_id = inv_obj.create(invoice)
                # we compute due date
                if inv.payment_term_id.id:
                    data = inv_obj.onchange_payment_term_date_invoice(
                           [inv_id], inv.payment_term_id.id, date)
                    if 'value' in data and data['value']:
                        inv_obj.write([inv_id], data['value'])
                created_inv.append(inv_id.id)
            # we get the view id

            '''
            xml_id = (inv.type == 'out_refund') and 'action_invoice_tree1' or \
                     (inv.type == 'in_refund') and 'action_invoice_tree2' or \
                     (inv.type == 'out_invoice') and 'action_invoice_out_refund' or \
                     (inv.type == 'in_invoice') and 'action_invoice_in_refund'
            # we get the model
            result = mod_obj.get_object_reference('account', xml_id)
            id = result and result[1] or False
            #we read the act window
            result = act_obj.browse(id)
             we add the new invoices into domain list
            invoice_domain = safe_eval(result['domain'])
            Evaluar la necesidad de este dominio para las vistas
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            '''
        return True

    @api.one
    def invoice_debit(self):
        return self.compute_debit()
