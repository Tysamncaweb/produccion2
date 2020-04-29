# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HrDepartmentHistory(models.Model):
    _name = 'hr.department.history'
    _description = 'Employees department changes historical data'
    _order = 'date_register'

    #fields
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')
    employee_ci = fields.Char(string='Employee Id', comodel_name='hr_employee')
    department_last = fields.Char(string='Last Department')
    department_new = fields.Char(string='New Department')
    date_register = fields.Date(string='Date', default=lambda self: date.today())

class Employee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Save employee department change on module hr.department.history'

    @api.multi
    def create(self, data):
        obj_employee = super(Employee, self).create(data)
        hr_dept = {
            'employee_id': obj_employee.id,
            'employee_ci': obj_employee.identification_id_2,
            #'employee_ci: obj_employee.identification_id_2,
            'department_last': '',
            'department_new': obj_employee.department_id.name,
        }
        obj_department_history = self.env['hr.department.history']
        obj_department_history.create(hr_dept)
        return obj_employee

    @api.multi
    def write(self, data):
        super(Employee, self).write(data)
        obj_employee = self
        obj_department_history = self.env['hr.department.history']
        employee_history = obj_department_history.search([('employee_id','=',obj_employee.id)])
        last_id = sorted(employee_history)
        old_department = ''
        new_department = obj_employee.department_id.name
        if len(employee_history) != 0:
            employee_history_last = last_id[-1]
            if(employee_history_last.department_new != obj_employee.department_id.name):
                new_department = obj_employee.department_id.name
                old_department = employee_history_last.department_new
            else:
                return True
        hr_dep = {
            'employee_id': obj_employee.id,
            'employee_ci': obj_employee.identification_id_2,
            'department_last': old_department,
            'department_new': new_department,
        }
        obj_department_history.create(hr_dep)
        return True