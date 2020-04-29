# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

##############################################################################
import time

import time
from lxml import etree
from datetime import time

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import logging
_logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _description = 'Account Invoice Debit Note'



    type = fields.Selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Nota de credito cliente'),
            ('in_refund', 'Nota de credito proveedor'),
            ('in_debit', 'Nota de debito proveedor'),  # Added
            ('out_debit', 'Nota de debito cliente'),
    ], string='Type', readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type', 'out_invoice'),
        track_visibility='always')

    # Modified
    @api.multi
    def _get_analytic_lines(self):
        """ Return a list of dict for creating analytic lines for self[0] """
        company_currency = self.company_id.currency_id
        sign = 1 if self.type in ('out_invoice', 'in_refund') else -1

        iml = self.env['account.invoice.line'].move_line_get(self.id)
        for il in iml:
            if il['account_analytic_id']:
                if self.type in ('in_invoice', 'in_refund', 'in_debit'):
                    ref = self.reference
                else:
                    ref = self.number
                if not self.journal_id.analytic_journal_id:
                    raise except_orm(_('No Analytic Journal!'),
                                     _("You have to define an analytic journal on the '%s' journal!") % (
                                     self.journal_id.name,))
                currency = self.currency_id.with_context(date=self.date_invoice)
                il['analytic_lines'] = [(0, 0, {
                    'name': il['name'],
                    'date': self.date_invoice,
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': currency.compute(il['price'], company_currency) * sign,
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'journal_id': self.journal_id.analytic_journal_id.id,
                    'ref': ref,
                })]
        return iml

    # Modified
    @api.model
    @api.returns('account.analytic.journal', lambda r: r.id)
    def _get_journal(self):
        type_inv = self._context.get('type', 'out_invoice')
        user = self.env.user
        company_id = self._context.get('company_id', user.company_id.id)
        type2journal = {'out_invoice': 'sale', 'out_debit': 'sale', 'in_invoice': 'purchase', 'in_debit': 'purchase',
                        'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}  # Modified
        refund_journal = {'out_invoice': False, 'out_debit': False, 'in_invoice': False, 'in_debit': False,
                          'out_refund': True, 'in_refund': True}  # Modified
        journal_obj = self.env['account.journal']
        res = journal_obj.search([('type', '=', type2journal.get(type_inv, 'sale')),
                                  ('company_id', '=', company_id)],
                                 #  ('refund_journal', '=', refund_journal.get(type_inv, False))],
                                 limit=1)
        return res and res[0] or False  # Modified


    @api.model
    @api.returns('account.analytic.journal', lambda r: r.id)
    def _get_journal_analytic(self, inv_type):
        type2journal = {'out_invoice': 'sale', 'out_debit': 'sale', 'in_invoice': 'purchase', 'in_debit': 'purchase', 'out_refund': 'sale', 'in_refund': 'purchase'}  # Modified
        journal_type = type2journal.get(inv_type, 'sale')
        journal = self.env['account.analytic.journal'].search([('type', '=', journal_type)], limit=1)
        if not journal:
            raise except_orm(_('No Analytic Journal!'),
                             _("You must define an analytic journal of type '%s'!") % (journal_type,))
        return journal[0]


    @api.multi
    def onchange_partner_id(self, type, partner_id,date_invoice=False, payment_term_id=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(type, partner_id, date_invoice=date_invoice, payment_term_id=payment_term_id, partner_bank_id=partner_bank_id, company_id=company_id)

        p = self.env['res.partner'].browse(partner_id)
        bank_id = p.bank_ids and p.bank_ids[0].id or False
        if type in ('in_invoice', 'in_refund', 'in_debit'):  # Modified
            result['value'].update({'partner_bank_id': bank_id})
        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(bank_id)
            result['value'].update(to_update['value'])
        return result

    # Modified
    @api.multi
    def onchange_company_id(self, company_id, part_id, type, invoice_line_ids, currency_id):

        dom = {}
        val = {}
        #val = super(account_invoice, self).onchange_company_id(company_id=company_id, part_id=part_id, type=type, invoice_line_ids=invoice_line_ids, currency_id=currency_id)
        # TODO: add the missing context parameter when forward-porting in trunk
        # so we can remove this hack!
        self = self.with_context(self.env['res.users'].context_get())

        values = {}
        domain = {}

        if company_id and part_id and type:
            p = self.env['res.partner'].browse(part_id)
            if p.property_account_payable and p.property_account_receivable and \
                    p.property_account_payable.company_id.id != company_id and \
                    p.property_account_receivable.company_id.id != company_id:
                prop = self.env['ir.property']
                rec_dom = [('name', '=', 'property_account_receivable'), ('company_id', '=', company_id)]
                pay_dom = [('name', '=', 'property_account_payable'), ('company_id', '=', company_id)]
                res_dom = [('res_id', '=', 'res.partner,%s' % part_id)]
                rec_prop = prop.search(rec_dom + res_dom) or prop.search(rec_dom)
                pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom)
                rec_account = rec_prop.get_by_record(rec_prop)
                pay_account = pay_prop.get_by_record(pay_prop)
                if not rec_account and not pay_account:
                    action = self.env.ref('account.action_account_config')
                    msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                    raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

                if type in ('out_invoice', 'out_refund'):
                    acc_id = rec_account.id
                else:
                    acc_id = pay_account.id
                val= {'account_id': acc_id}

            if self:
                if company_id:
                    for line in self.invoice_line_ids:
                        if not line.account_id:
                            continue
                        if line.account_id.company_id.id == company_id:
                            continue
                        accounts = self.env['account.account'].search([('name', '=', line.account_id.name), ('company_id', '=', company_id)])
                        if not accounts:
                            action = self.env.ref('account.action_account_config')
                            msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
                        line.write({'account_id': accounts[-1].id})
            else:
                for line_cmd in invoice_line_ids or []:
                    if len(line_cmd) >= 3 and isinstance(line_cmd[2], dict):
                        line = self.env['account.account'].browse(line_cmd[2]['account_id'])
                        if line.company_id.id != company_id:
                            raise except_orm(
                                _('Configuration Error!'),
                                _("Invoice line account's company and invoice's company does not match.")
                            )


        account_journal = self.env['account.journal']
        if company_id and type:
            if type in ('out_invoice', 'out_debit'):  # Modified
                journal_type = 'sale'
            elif type in ('out_refund'):
                journal_type = 'sale_refund'
            elif type in ('in_refund', 'in_debit'):  # Modified
                journal_type = 'purchase_refund'
            else:
                journal_type = 'purchase'
            journal_ids = account_journal.search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journal_ids:
                val['journal_id'] = journal_ids.id
            res_journal_default = self.env['ir.values'].get('default', 'type=%s' %(type), ['account.invoice'])
            for r in res_journal_default:
                if r[1] == 'journal_id' and r[2] in journal_ids:
                    val['journal_id'] = r[2]
            if not val.get('journal_id', False):
                raise except_orm(_('Configuration Error !'), (_('Can\'t find any account journal of %s type for this company.\n\nYou can create one in the menu: \nConfiguration\Financial Accounting\Accounts\Journals.') % (journal_type)))
            dom = {'journal_id':  [('id', 'in', journal_ids.ids)]}
        else:
            journal_ids = account_journal.search([])

        if currency_id and company_id:
            currency = self.env['res.currency'].browse(currency_id)
            if currency.company_id and currency.company_id.id != company_id:
                val['currency_id'] = False
            else:
                val['currency_id'] = currency.id
        if company_id:
            company = self.env['res.company'].browse(company_id)
            if company.currency_id.company_id and company.currency_id.company_id.id != company_id:
                val['currency_id'] = False
            else:
                val['currency_id'] = company.currency_id.id
        return {'value': val, 'domain': dom}

    # Modified
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        _logger.info("context: %s", context)
        journal_obj = self.env['account.journal']

        if context.get('active_model', '') in ['res.partner'] and context.get('active_ids', False) and context['active_ids']:
            # partner = self.env(context['active_model']).read( context['active_ids'], ['supplier','customer'])[0]
            partner = self.env[context['active_model']].read(context['active_ids'], ['supplier', 'customer'])
            if partner:
                partner = partner[0]
            if not view_type:
                view_id = self.env['ir.ui.view'].search([('name', '=', 'account.invoice.tree')])
                view_type = 'tree'
            if view_type == 'form':
                if partner:
                    if partner['supplier'] and not partner['customer']:
                        view_id = self.env['ir.ui.view'].search([('name', '=', 'account.invoice.supplier.form')])
                else:
                    view_id = self.env['ir.ui.view'].search([('name', '=', 'account.invoice.form')])
        if view_id:
            if isinstance(view_id, (list, tuple)):
                view_id = view_id[0]
            elif not isinstance(view_id, int):
                view_id = view_id.ids[0]
        res = super(account_invoice,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        type = context.get('journal_type', 'sale')
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search('', [('type', '=', type)], limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select

        if view_type == 'tree':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='partner_id']")
            partner_string = _('Customer')
            if context.get('type', 'out_invoice') in ('in_invoice', 'in_refund', 'in_debit'):  # Modified
                partner_string = _('Supplier')
            for node in nodes:
                node.set('string', partner_string)
            res['arch'] = etree.tostring(doc)
        return res


    # Modified
    @api.multi
    def action_number(self):
        # TODO: not correct fix but required a fresh values before reading it.
        self.write({})

        for inv in self:
            self.write({'internal_number': inv.number})

            if inv.type in ('in_invoice', 'in_refund', 'in_debit'):
                if not inv.reference:
                    ref = inv.number
                else:
                    ref = inv.reference
            else:
                ref = inv.number

            self._cr.execute(""" UPDATE account_move SET ref=%s
                           WHERE id=%s AND (ref IS NULL OR ref = '')""",
                             (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_move_line SET ref=%s
                           WHERE move_id=%s AND (ref IS NULL OR ref = '')""",
                             (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_analytic_line SET ref=%s
                           FROM account_move_line
                           WHERE account_move_line.move_id = %s AND
                                 account_analytic_line.move_id = account_move_line.id""",
                             (ref, inv.move_id.id))

        for inv_id, name in self.name_get():
            ctx = dict(self._context, lang=inv.partner_id.lang)
            if inv.type in ('out_invoice', 'out_refund', 'out_debit'):  # Modified
                message = _('Invoice ') + " '" + name + "' " + _("is validated.")
                self.log(message)
            if inv.type in ('in_invoice'):
                # for line in inv_id.invoice_line_idss:
                #     result = line_obj.asset_create(line_obj)
                # line_obj = self.env['account.invoice.line'].browse(inv_id.invoice_line_idss)
                # result = line_obj.asset_create(line_obj)
                self.env['account.invoice.line'].asset_create(inv.invoice_line_ids)
        self.invalidate_cache()

        return True


    @api.multi
    def invoice_pay_customer(self):
        if not self.ids: return []
        #dummy, view_id = self.env['ir.model.data'].get_object_reference('account_voucher', 'view_vendor_receipt_dialog_form')
        dummy, view_id = self.env['ir.model.data'].get_object_reference('account_voucher', 'view_vendor_payment_form')
        inv = self
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': "new",
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.env['res.partner']._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'default_name':inv.name,
                'default_account_id':inv.account_id.id,
                'close_after_process': True,
                'invoice_type':inv.type,
                'invoice_id':inv.id,
                'default_type': inv.type in ('out_invoice','out_refund','out_debit') and 'receipt' or 'payment', # Added
                'type': inv.type in ('out_invoice','out_refund','out_debit') and 'receipt' or 'payment', # Added
                'journal': inv.journal_id.id or False,


                }
        }
