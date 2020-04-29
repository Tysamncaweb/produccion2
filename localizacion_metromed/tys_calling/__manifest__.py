# encoding: UTF-8
# Create:  jeduardo** 26/08/2017 **  **
# type of the change:  Creacion
# Comments: Creacion del modulo de calling
#Contiene un diccionario en Python para agregar las descripciones del módulo, como autor, versión, etc.
{
    'name': 'Calling',
    'version':'1.0',
    'category': 'Call Canter',
    'summary':'Registro Basico de LLamadas',
    'description': '''\
Registro Básico de llamadas
============================

V1.1.1.\n
Permite registrar y hacer seguimiento de las llamadas recibidas por el call center\n
''',
    'author': 'TYSAMNCA',
    'website': 'https://tysamnca.com',
    #data, es una lista donde se agregan todas las vistas del módulo, es decir los archivos.xml y archivos.csv.
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'views/calling_view.xml',
             'views/clients_view.xml',
             'views/res_partner_view.xml',
             'views/news_view.xml',
             'wizard/menu_report_view.xml',
             'wizard/menu_services_clientes_wizard.xml',
             'wizard/menu_services_wizard.xml',
             'report/report_sede_pdf_view.xml',
             'report/report_clientes_pdf_view.xml',
             'report/report_servicios_pdf_view.xml',
             'data/tys_calling_data.xml',
            ],
    #depends,  es una lista donde se agregan los módulos que deberían estar instalados (Módulos dependencia) para que el modulo pueda ser instalado en Odoo.
    'depends': ['base','web','mail','hr','fleet','tys_l10n_ve','sale'],
    'js': [],
    'css': [],
    'qweb' : [],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}