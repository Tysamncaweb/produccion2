# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details..
{
    'name': 'hr_payslip_run_total',
    'version': '1.0',
    'summary': 'Agrega totales de deducciones y asignaciones al procesamiento de nómina',

    'description': """

    """,
    'author': 'Tysamnca',
    'collaborator': 'Yorman Pineda',
    'category': 'paysaliprun',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['base','hr_payroll','hr_datos_rrhh'],
    'data': [

        'views/hr_payslip_run_vist.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
