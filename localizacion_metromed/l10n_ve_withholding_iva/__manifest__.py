# coding: utf-8
###########################################################################

{
    "name": "Management withholding vat based in the Venezuelan tax laws",
    "version": "1.2",
    "author": 'TYSAMNCA',
    "category": 'Generic Modules/Accounting',
    "depends": ['base_vat','base','account','l10n_ve_fiscal_requirements',
    "l10n_ve_withholding",'web'],
    'description' : """
Administración de las retenciones de IVA.
===================================================

Colaborador: Kelvis Pernia
    """,
    'website': 'http://www.tysamnca.com',
    'data': [
        #'data/l10n_ve_withholding_iva_data_sequence.xml',
        'security/wh_iva_security.xml',
        'security/ir.model.access.csv',
        #'report/withholding_vat_report.xml',
        'wizard/wizard_retention_view.xml',
        #'wizard/wizard_wh_nro_view.xml',
        'view/generate_txt_view.xml',
        'view/account_invoice_view.xml',
        'view/account_view.xml',
        'view/partner_view.xml',
        'view/res_company_view.xml',
        'view/wh_iva_view.xml',
        'report/withholding_vat_report.xml',
        #'report/txt_wh_report.xml',
    ],
    'installable': True,
}
