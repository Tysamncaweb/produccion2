# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Petty_Cash',
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',
    'summary': 'Petty_Cash_Module',
    'description': """
Small Box Module.
======================
Con este módulo se realizara el registro y manejo de Caja Chica en odoo 11
    """,
    'depends': ['base','account'],
    'data': [

        'wizard/increase_amount_wizard_view.xml',
        'wizard/decrease_amount_wizard_view.xml',
        'wizard/reverse_asiento.xml',
        'report/report_replacement_petty_cash.xml',
        'view/account_invoice_inherit.xml',
        'view/account_petty_cash_view.xml',
        'view/invoice_petty_cash_view.xml',
        'view/replacement_petty_cash_view.xml',


        #'view/information_Petty_Cash_report.xml',
        #'report/report_Petty_Cash.xml',
    ],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}
