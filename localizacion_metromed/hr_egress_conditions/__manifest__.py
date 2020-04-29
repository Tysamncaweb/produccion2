# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Motivo de Egreso',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'sequence': 103,
    'summary': 'Show employee egress conditions',
    'description': '''
        Modulo para Motivos de Egreso.\n\n
        Este Modulo crea la funcionalidad de motivos de Egreso de los empleados\n
            - Fecha de Egreso\n
            - Motivo de Egreso\n
    ''',
    'depends': [
        'base_setup',
        'hr',
        'hr_contract'
    ],
    'data': [
        'views/hr_egress_conditions_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}