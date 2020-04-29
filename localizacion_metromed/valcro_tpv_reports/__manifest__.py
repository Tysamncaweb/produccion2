# -*- coding: utf-8 -*-
{
    'name': "Valcro TPV Reports",

    'summary': """Valcro_TPV_Reports""",

    'description': """
       Reportes en TPV para la empresa Valcro
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report_session_consolidated.xml',
	    'report/report_session_details.xml',
        'report/report_preliminary_squad.xml',
        'wizard/wizard_session_details.xml',
        'wizard/wizard_preliminary_squad.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
