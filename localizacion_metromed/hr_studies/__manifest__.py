# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 28/04/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_salary_rule_direct_account
# 'views/hr_salary_rule_view.xml',
{

    'name': 'hr_studies',
    'description': '''\
Module for adding study and academic info
============================

Modulo for adding study and academic info V1.1.0

''',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'data': [
            'view/studies_view.xml'
        ],
    'depends': ['base', 'hr'],
    'installable': True,


}