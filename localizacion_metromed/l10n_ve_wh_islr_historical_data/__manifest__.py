# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 15/09/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de akr_account_retention_book

{
    'name': 'Histórico de Retenciones de ISLR',
    'description': '''\
Histórico de Retenciones de ISLR
================================

V1.1.1.
Permite generar el reporte del libro de retenciones
''',
    'author': 'TYSAMNCA',
    'category': 'Account',
    'data': [
      #  'views/l10n_ve_wh_islr_historical_data_view.xml',
      #  'views/islr_historical_data_view.xml',
      #  'wizard/islr_historical_data_wizard_view.xml',
        ],
    'depends': ["base","l10n_ve_withholding_islr"],
    'installable': True,
}