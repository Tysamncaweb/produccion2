# encoding: UTF-8
{
    'name': 'Account Advanced Payment',
    'version':'1.0',
    'category': 'account',
    'summary':'Registro de Anticipo para proveedores y clientes',
    'description': '''
Registro de Anticipos para ser aplicados a las facturas de clientes y proveedores,
asi como los reversos de los mismos.
============================
Colaborador: Nathaly Partidas
''',
    'author': 'TYSAMNCA',
    'website': 'https://tysamnca.com',
    #data, es una lista donde se agregan todas las vistas del módulo, es decir los archivos.xml y archivos.csv.
    'data': [
             'view/account_advance_payment.xml',
             'data/sequence_advance_data.xml',
             'view/res_partner_view.xml',
            ],
    #depends,  es una lista donde se agregan los módulos que deberían estar instalados (Módulos dependencia) para que el modulo pueda ser instalado en Odoo.
    'depends': ['base','web','mail','account'],
    'js': [],
    'css': [],
    'qweb' : [],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}
