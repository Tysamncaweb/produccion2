# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Gastos_Petty_Cash',
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',
    'summary': 'Petty_Cash_Module',
    'description': """
Small Box Module.
======================
Carga los datos para la tabla de gastos""",
    'depends': ['base','account'],
    'data': [
        'view/gastos_petty_cash_data.xml',
    ],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}
