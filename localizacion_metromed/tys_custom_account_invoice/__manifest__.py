# -*- encoding: utf-8 -*-

{
    'name' : 'Custom Account Invoice',
    'version' : '1.0',
    'author' : 'TYSAMNCA',
    'category' : 'Accounting',
    'description' : """
Personalized account invoice report
===================================================

Colaborador: Jose Angel Eduardo
    """,
    'website':'http://www.tysamnca.com',
    'depends' :['account','sale', 'tys_account_invoice_line'],
    'data': ['views/invoice_report.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}








