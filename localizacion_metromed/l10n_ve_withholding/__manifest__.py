{
    "name": "Management withholdings Venezuelan laws",
    "version": "0.2",
    "author": "Tysamnca",
    "license": "AGPL-3",
    "website": "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "depends": ["l10n_ve_fiscal_requirements"],
    'data': [
     #   'security/withholding_security.xml',
    #    'security/ir.model.access.csv',
        #'data/l10n_ve_withholding_data.xml',
        'view/l10n_ve_withholding_view.xml',
        # 'workflow/wh_action_server.xml', # Discontinued in v8 migration
    ],
    'test': [
   #     'test/account_supplier_invoice.yml',
  #      'test/wh_pay_invoice.yml',
    ],
    'installable': True,
}