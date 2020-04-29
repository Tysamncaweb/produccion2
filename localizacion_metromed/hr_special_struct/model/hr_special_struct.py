#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, tools, api, _ , exceptions

class hr_payslip_struct(models.Model):
    _inherit = "hr.payslip.run"
    _description = "Nomina Especial"

    check_special_struct = fields.Boolean('Nomina Especial')
    struct_id = fields.Many2one('hr.payroll.structure', 'Tipo de Nomina Especial', states={'draft': [('readonly', False)]} )

    @api.onchange('check_special_struct')
    def onchange_check_special_struct(self):
        res = {}
        if self.check_special_struct == False:
           res = {'value': {'struct_id_payroll': False}}
        return res

class hr_payroll_structure_special(models.Model):
    _inherit = 'hr.payroll.structure'
    _description = "Employee familiar"

    STRUCT_CATEGORY = [
        ('normal', 'Normal'),
        ('especial', 'Especial'),
    ]

    PAYROLL_CATEGORY =[
        ('ticket', 'Cestatickets'),
        ('fideicomiso', 'Fideicomiso'),
        ('vacaciones', 'Vacaciones'),
        ('utilidad', 'Utilidades'),
        ('liquidacion', 'Liquidaciones'),
        ('militar', 'Militar'),
        ('habitacional', 'Banavih'),
        ('gurderia', 'Guarderia'),
    ]

    # DEDUCTION_MODE = [
    #     ('star_m', 'Primera quincena'),
    #     ('end_m', 'Fin de mes'),
    #     ('iq', 'Cada pago')
    # ]

    struct_category = fields.Selection(STRUCT_CATEGORY, 'Categoria de Nomina', select=True, required=True)
    struct_id_payroll_category = fields.Selection(PAYROLL_CATEGORY, 'Referencia de Nomina')
    struct_id_reference = fields.Many2one('hr.payroll.reference', 'Referencia de Nomina')
    # deductions_pay_mode = fields.Selection(DEDUCTION_MODE, 'Deducciones a:',default='iq')

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def get_all_structures(self):
        # ret = super(hr_contract, self).get_all_structures(cr, uid, contract_ids, context=context)
        #is_special = self._context.get('is_special', False)
        active_id = self._context.get('active_id', False)
        special_fields = self.env['hr.payslip.run'].search([('id', '=', active_id)])
        is_special = special_fields.check_special_struct
        if is_special:
            #hrpr = self.env['hr.payslip.run'].search([('id', '=', active_id)])
            structure_ids = [special_fields.struct_id.id]
        else:
            #Si es una nomina especial asigna el mismo id de nomina a cada contrato
            #if hrpr.check_special_struct and hrpr.struct_id:
           #     structure_ids = [hrpr.struct_id.id]
           # else:
            structure_ids = [contract.struct_id.id for contract in self if contract.struct_id]

        if not structure_ids:
            return []
        local_parent = self.env['hr.payroll.structure']._get_parent_structure()
        if local_parent:
            return list(set(local_parent.id))
        return structure_ids


class hr_payslip_employees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    #@api.multi
    #def compute_sheet(self):
        #ctx = self.env.context.copy()
        #active_id = self._context.get('active_id', False)
        #hrpr = self.env['hr.payslip.run'].search([('id','=',active_id)])
        #is_special =
        #if hrpr.check_special_struct if hrpr else False:
        #    ctx.update({'is_special':1,
        #                    'special_id' : hrpr.struct_id.id})
        #    self.with_context(ctx)
   #     self.context.update({'come_from': 'hr.payslip.employees'})
    #    ret = super(hr_payslip_employees, self).compute_sheet()

   #     return ret
    '''
    @api.multi
    def compute_sheet(self):
        local_context = self._context.copy()
        active_id = local_context.get('active_id', False)
        special_fields = self.env['hr.payslip.run'].search([('id','=', active_id)])
        is_special = special_fields.check_special_struct #if special_fields.check_special_struct else False
        if is_special:
            local_context.update({'is_special':1,
                            'special_id' : special_fields.struct_id.id})
        local_context.update({'come_from': 'hr.payslip.employees'})
        self.with_context(local_context)
        ret = super(hr_payslip_employees, self).compute_sheet()

        return ret
    '''

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                            (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
        #get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        payslip_run_obj = self.env['hr.payslip.run']
        for ps in self:
            for psr in payslip_run_obj.browse(ps.payslip_run_id.id):
                is_special = psr.check_special_struct
                if is_special:
                    self.struct_id = psr.struct_id.id
                    self.with_context({'is_special': 1, 'special_id': psr.struct_id.id})

        if len(contracts) == 1 and payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        #get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return list(result_dict.values())

'''
    @api.multi
    def compute_sheet(self):
   #     ctx = self.context.copy()
        payslip_run_obj = self.env['hr.payslip.run']
        come_from = self._context.get('come_from', False)
        if come_from and come_from == 'payoff':
            for ps in self:
                self.with_context({'is_special': 1, 'special_id': ps.struct_id.id,'slip_id':self.ids[0]})
        else:
            for ps in self:
                for psr in payslip_run_obj.browse(ps.payslip_run_id.id):
                    is_special = psr.check_special_struct
                    if is_special:
                        self.struct_id = psr.struct_id.id
                        self.with_context({'is_special': 1,'special_id': psr.struct_id.id})
        ret = super(hr_payslip, self).compute_sheet()
        return ret
'''

class hr_payroll_reference(models.Model):
    _name = 'hr.payroll.reference'
    _description = "Referencia para Nominas Especiales"

    name = fields.Char('Referencia de Nómina', size=20)
    description = fields.Char('Descripcion de la Referencia de Nómina')