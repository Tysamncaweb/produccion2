{
    "name": "Local Withholding Venezuela",
    "version": "0.2",
    "author": "Tysamnca",
    "category": 'Generic Modules/Accounting',
    "depends": ["base_vat","base","account",'l10n_ve_fiscal_requirements'],
  #  'test': [
  #      'test/awm_customer.yml',
  #      'test/awm_supplier.yml',
  #  ],
    'data': [
  #      'security/wh_muni_security.xml',
  #      'security/ir.model.access.csv',
  #      'data/wh_muni_sequence.xml',
        'view/account_invoice_view.xml',
        'view/partner_view.xml',
        'view/wh_muni_view.xml',
  #      'data/wh_muni_sequence.xml',
  #      'report/wh_muni_report.xml',
  #      'workflow/l10n_ve_wh_muni_wf.xml',
    ],
  #  'demo': [
  #      'demo/demo_accounts.xml',
  #      'demo/demo_journal.xml',
  #      'demo/demo_partners.xml',
  #  ],
    'installable': True,
}