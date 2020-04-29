from odoo import models, fields, api, _
class salary_increase_select(models.TransientModel):
    _name = 'salary.increase.select'
    _description = 'New select'

    employee_ids = fields.Many2many(comodel_name='hr.employee',
                                    relation='hr_employeer_increase_rel',
                                    column1='employee_id',
                                    column2='increase_id')

    @api.multi
    def add_employees(self):
        salary_increase_obj = self.env['salary.increase']
        salary_increase = salary_increase_obj.browse(self._context['active_id'])
        employee_ids = [line.employee_id.id for line in salary_increase.employee_ids]
        for wizard in self:
            increase = []
            [increase.append(
                            (0, 0, {
                                'employee_id': employee.id,
                                'vat': employee.identification_id_2,
                                'porcent': salary_increase.wage,
                                'amount': (employee.contract_id.wage * salary_increase.wage)/100  if salary_increase.type_aumento == 'por' and salary_increase.wage else salary_increase.monto,

                            })
                        ) for employee in wizard.employee_ids if employee.id not in employee_ids]

        salary_increase.write({'employee_ids': increase})