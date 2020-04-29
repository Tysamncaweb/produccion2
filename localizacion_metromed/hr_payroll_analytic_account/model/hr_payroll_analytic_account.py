# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Change: jeduardo **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################

import time

from odoo import fields, models, api, exceptions
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _

class hr_salary_rule_account(models.Model):
    _inherit = 'hr.salary.rule'

   # account_debit_indirect = fields.Many2one('account.account', 'Cuenta deudora indirecta')
    account_debit = fields.Many2one('account.account', 'Cuenta deudora directa', required=True)
    account_credit = fields.Many2one('account.account', 'Cuenta Acreedora', required=True)



class hr_contract_account(models.Model):

    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    type_nom = fields.Selection([('direct', 'Directo'), ('indirect', 'Indirecto')], required=True, string="Mano de Obra")





class hr_payslip(models.Model):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    @api.multi
    def process_sheet(self):
        move_pool = self.env['account.move']
       # period_pool = self.env('account.period')
        precision = self.env['decimal.precision'].precision_get('Payroll')
        timenow = time.strftime('%Y-%m-%d')
        account_analytic_id = 0

        for slip in self.browse():
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
           # if not slip.period_id:
            #    search_periods = period_pool.find(cr, uid, slip.date_to, context=context)
             #   period_id = search_periods[0]
           # else:
            #    period_id = slip.period_id.id

            default_partner_id = slip.employee_id.address_id.id
            account_analytic_id = slip.contract_id.analytic_account_id
            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'date': timenow,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
             #   'period_id': period_id,
            }

            for line in slip.details_by_salary_rule_category:
                amt = slip.credit_note and -line.total or line.total
                if float_is_zero(amt, precision_digits=precision):
                    continue
                partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
                debit_account_id = line.salary_rule_id.account_debit.id if slip.contract_id.type_nom == 'direct' else line.salary_rule_id.account_debit_indirect.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:

                    debit_line = (0, 0, {
                    'name': line.name,
                    'date': timenow,
                    'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable')) and partner_id or False,
                    'account_id': debit_account_id,
                    'journal_id': slip.journal_id.id,
              #      'period_id': period_id,
                    'debit': amt > 0.0 and amt or 0.0,
                    'credit': amt < 0.0 and -amt or 0.0,
                    'analytic_account_id': account_analytic_id and account_analytic_id.id or False,
                    'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:

                    credit_line = (0, 0, {
                    'name': line.name,
                    'date': timenow,
                    'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in ('receivable', 'payable')) and partner_id or False,
                    'account_id': credit_account_id,
                    'journal_id': slip.journal_id.id,
               #     'period_id': period_id,
                    'debit': amt < 0.0 and -amt or 0.0,
                    'credit': amt > 0.0 and amt or 0.0,
                    'analytic_account_id': account_analytic_id and account_analytic_id.id or False,
                    'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise exceptions.except_orm(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                #    'period_id': period_id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise exceptions.except_orm(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                 #   'period_id': period_id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)

            move.update({'line_id': line_ids})
            move_id = move_pool.create(move)
            self.write([slip.id], {'move_id': move_id})
            if slip.journal_id.entry_posted:
                move_pool.post([move_id])
        return self.write({'paid': True, 'state': 'done'})



# class hr_payslip_run(osv.osv):
#
#     _inherit = 'hr.payslip.run'
#     _description = 'Payslip Run'
#     _columns = {
#         'journal_id': fields.many2one('account.journal', 'Salary Journal', states={'draft': [('readonly', False)]}, readonly=True, required=True),
#         'move_id': fields.many2one('account.move', 'Accounting Entry', readonly=True),
#     }
#
#     def _get_default_journal(self, cr, uid, context=None):
#         model_data = self.env('ir.model.data')
#         res = model_data.search(cr, uid, [('name', '=', 'expenses_journal')])
#         if res:
#             return model_data.browse(cr, uid, res[0]).res_id
#         return False
#
#     _defaults = {
#         'journal_id': _get_default_journal,
#     }
#
#     def hr_verify_sheet_multiple(self, cr, uid, ids, context=None):
#         move_pool = self.env('account.move')
#         period_pool = self.env('account.period')
#         precision = self.env('decimal.precision').precision_get(cr, uid, 'Payroll')
#         timenow = time.strftime('%Y-%m-%d')
#
#         for slip_run in self.browse(cr, uid, ids, context=context):
#
#             line_ids = []
#             debit_sum = 0.0
#             credit_sum = 0.0
#             ctx = dict(context or {}, account_period_prefer_normal=True)
#             search_periods = period_pool.find(cr, uid, slip_run.date_end, context=ctx)
#             period_id = search_periods[0]
#
#             res_company = self.env('res.company')
#             default_partner_id = res_company._company_default_get(cr, uid, 'purchase.order', context=context)
#             default_partner_id = res_company.browse(cr, uid, default_partner_id, context=context)
#
#             name = _('Payslip of %s') %(default_partner_id.name)
#             move = {
#                 'narration': name,
#                 'date': timenow,
#                 'ref': slip_run.name,
#                 'journal_id': slip_run.journal_id.id,
#                 'period_id': period_id,
#                 }
#
#             salary_rule_ids = {}
#
#             for slip in slip_run.slip_ids:
#                 for line in slip.line_ids:
#
#                     if not salary_rule_ids.has_key(line.salary_rule_id.id):
#                         salary_rule_ids[line.salary_rule_id.id] = {
#
#                             line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id: {
#                                 line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0: {
#
#                                     'amount': line.total,
#                                     'credit_note': slip.credit_note,
#                                 }
#                             },
#
#
#                         }
#
#                     elif not salary_rule_ids[line.salary_rule_id.id].has_key(line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id):
#                         salary_rule_ids[line.salary_rule_id.id].update({
#                             line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id: {
#                                 line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0: {
#                                     'amount':line.total,
#                                     'credit_note':slip.credit_note,
#                                 }
#                             },
#                         })
#
#                     elif not salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id].has_key(line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0):
#                         salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id].update({
#                             line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0:{
#
#                                 'amount':line.total,
#                                 'credit_note':slip.credit_note,
#                             }
#                         })
#
#
#
#                     elif salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id].has_key(line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0):
#                         salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id][line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0].update({
#
#                             'amount': salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id or line.salary_rule_id.account_debit_indirect.id][line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0]['amount'] + line.total if slip.contract_id.tipo_mano_obra == 'directa' else salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.idline.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id][line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG','PRIM','OTRO','BON','ASN','ASB']  else 0]['amount'],
#                             'credit_note': salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id or line.salary_rule_id.account_debit_indirect.id][line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG', 'PRIM', 'OTRO', 'BON', 'ASN', 'ASB', 'VIV', 'ANT']  else 0]['credit_note'] + slip.credit_note if slip.credit_note > 0 and slip.contract_id.tipo_mano_obra == 'directa' else salary_rule_ids[line.salary_rule_id.id][line.salary_rule_id.account_debit.id if slip.contract_id.tipo_mano_obra == 'directa' else line.salary_rule_id.account_debit_indirect.id][line.contract_id.analytic_account_id.id if line.category_id.code in ['ASG','PRIM','OTRO','BON','ASN','ASB']  else 0]['credit_note'],
#
#                         })
#
#             hr_salar_rule_obj = self.env('hr.salary.rule')
#             for rule in hr_salar_rule_obj.browse(cr, uid, salary_rule_ids.keys()):
#                 for debit_account_id, analytics_and_amounts in salary_rule_ids[rule.id].items():
#                     for account_analytic_id, amounts in analytics_and_amounts.items():
#
#                         if amounts['credit_note'] > 0 or amounts['amount'] >0:
#                             amt = amounts['credit_note'] and -amounts['amount'] or amounts['amount']
#                             partner_id = default_partner_id
#                             credit_account_id = rule.account_credit.id if rule.account_credit else False
#
#                             if debit_account_id:
#                                 debit_line = (0, 0, {
#                                     'name': rule.name,
#                                     'date': timenow,
#                                     'partner_id': (
#                                                       rule.register_id.partner_id or rule.account_debit.type in (
#                                                   'receivable', 'payable')) and partner_id or False,
#                                     'account_id': debit_account_id,
#                                     'journal_id': slip_run.journal_id.id,
#                                     'period_id': period_id,
#                                     'debit': amt > 0.0 and amt or 0.0,
#                                     'credit': amt < 0.0 and -amt or 0.0,
#                                     'tax_code_id': rule.account_tax_id and rule.account_tax_id.id or False,
#                                     'tax_amount': rule.account_tax_id and amt or 0.0,
#                                     'analytic_account_id':account_analytic_id if account_analytic_id != 0 else False,
#                                 })
#                                 line_ids.append(debit_line)
#                                 debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
#
#                             if credit_account_id:
#                                 credit_line = (0, 0, {
#                                     'name': rule.name,
#                                     'date': timenow,
#                                     'partner_id': (
#                                                       rule.register_id.partner_id or rule.account_credit.type in (
#                                                   'receivable', 'payable')) and partner_id or False,
#                                     'account_id': credit_account_id,
#                                     'journal_id': slip_run.journal_id.id,
#                                     'period_id': period_id,
#                                     'debit': amt < 0.0 and -amt or 0.0,
#                                     'credit': amt > 0.0 and amt or 0.0,
#                                     'analytic_account_id': rule.analytic_account_id and rule.analytic_account_id.id or False,
#                                     'tax_code_id': rule.account_tax_id and rule.account_tax_id.id or False,
#                                     'tax_amount': rule.account_tax_id and amt or 0.0,
#
#                                 })
#                                 line_ids.append(credit_line)
#                                 credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
#
#                 if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
#                     acc_id = slip_run.journal_id.default_credit_account_id.id
#                     if not acc_id:
#                         raise osv.except_osv(_('Configuration Error!'),
#                                              _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
#                                              slip.journal_id.name))
#                     adjust_credit = (0, 0, {
#                         'name': _('Adjustment Entry'),
#                         'date': timenow,
#                         'partner_id': False,
#                         'account_id': acc_id,
#                         'journal_id': slip_run.journal_id.id,
#                         'period_id': period_id,
#                         'debit': 0.0,
#                         'credit': debit_sum - credit_sum,
#                     })
#                     line_ids.append(adjust_credit)
#
#                 elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
#                     acc_id = slip_run.journal_id.default_debit_account_id.id
#                     if not acc_id:
#                         raise osv.except_osv(_('Configuration Error!'),
#                                              _('The Expense Journal "%s" has not properly configured the Debit Account!') % (
#                                              slip_run.journal_id.name))
#                     adjust_debit = (0, 0, {
#                         'name': _('Adjustment Entry'),
#                         'date': timenow,
#                         'partner_id': False,
#                         'account_id': acc_id,
#                         'journal_id': slip_run.journal_id.id,
#                         'period_id': period_id,
#                         'debit': credit_sum - debit_sum,
#                         'credit': 0.0,
#                     })
#                     line_ids.append(adjust_debit)
#             move.update({'line_id': line_ids})
#             move_id = move_pool.create(cr, uid, move, context=context)
#
#             slip_run.write({'move_id': move_id, 'period_id': period_id})
#             [slip.write({'move_id': move_id, 'period_id': period_id}) for slip in slip_run.slip_ids]
#             if slip_run.journal_id.entry_posted: move_pool.post(cr, uid, [move_id], context=context)
#
#         return super(hr_payslip_run, self).hr_verify_sheet_multiple(cr, uid, ids, context=context)
#
#
# hr_payslip_run()
