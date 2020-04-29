# coding: utf-8

{
    'name': 'Venezuela Fiscal Requirements',
    'version' : '1.0',
    'author' : 'TYSAMNCA',
    'category' : 'Localization',
    'description' : """

 Agrega los requerimientos fiscales exigidos por las leyes venezolanas
 
Colaborador: Kelvis Pernia
    """,

    'depends': [
        'account',
        'base_vat',
        'account_accountant',
        'account_voucher',
        'account_cancel',
        'debit_credit_note'
    ],
    'data': [

        'data/l10n_ut_data.xml',
        'data/seniat_url_data.xml',

        'security/security_view.xml',
        'security/ir.model.access.csv',

        'wizard/wizard_invoice_nro_ctrl_view.xml',
        'wizard/update_info_partner.xml',
        'wizard/search_info_partner_seniat.xml',
        'wizard/wizard_nro_ctrl_view.xml',

        'view/res_company_view.xml',
        'view/l10n_ut_view.xml',

        #'view/partner_view.xml',

        'view/account_inv_refund_nctrl_view.xml',
        'view/account_tax_view.xml',
        'view/account_invoice_view.xml',
    ],
    'installable': True,
}

