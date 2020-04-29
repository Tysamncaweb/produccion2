# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Report Payroll Summary',
    'version' : '2.0',
    'summary': 'Generate summary payroll report',
    'sequence': 30,
    'description': """
This module generates a sumary payroll report for METROMED company
Colaboradores: María Carreño / José Ángel Eduardo
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll'],
    'data': [
        'report/hr_payroll_summary_report.xml',

    ],
    'qweb': [
        #"static/src/xml/account_reconciliation.xml",
        #"static/src/xml/account_payment.xml",
        #"static/src/xml/account_report_backend.xml",
        #"static/src/xml/account_dashboard_setup_bar.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}