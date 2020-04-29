# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 29/07/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_payroll_account

{
    'name': 'HR Payroll Analytic Account',
    'description': u'''\
Modificación del método process_sheet de hr_payroll_account
============================

V1.1.1.\r\n
* Sobre escribe el método process_sheet para que utilice la cuenta analítica especificada en el contrato del empleado.\r\n
* Coloca como abligatorio el campo cuenta analítica en el contrato del empleado
''',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'data': [
        'views/hr_payroll_analytic_account_view.xml',
        ],
    'depends': ['hr_payroll','hr_payroll_account'],
    'installable': True,
}