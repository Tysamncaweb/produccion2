# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Employee Name',
    'version': '1.1',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'sequence': 107,
    'summary': 'Agrega 2 nombre y 2 apellidos al empleado.',
    'description': "Permite agregar los 2 nombre y los 2 apellidos del empleado de forma separada",
    'depends': [
        'base_setup',
        'hr'
    ],
    'data': [
        'views/hr_payroll_employee_name_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}