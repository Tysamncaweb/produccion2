# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Config Parameters',
    'version': '1.1',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'sequence': 100,
    'summary': 'Parameters for payroll',
    'description': "Allows to manage parameters for the payroll module",
    'depends': [
        'base_setup',
        'hr_payroll'
    ],
    'data': [
        'views/hr_config_parameter_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}