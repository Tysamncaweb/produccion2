# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Historico de Departamentos',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Recursos Humanos',
    'sequence': 104,
    'summary': 'Mostrar datos históricos para cambios de departamento',
    'description': '''
        Mostrar datos históricos para cambios de departamento
    ''',
    'depends': [
        'base_setup',
        'hr',
    ],
    'data': [
        'views/hr_department_history_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}