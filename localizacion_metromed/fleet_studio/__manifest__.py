# encoding: UTF-8
# Create:  jeduardo** 26/08/2017 **  **
# type of the change:  Creacion
# Comments: Creacion del modulo de calling
#Contiene un diccionario en Python para agregar las descripciones del módulo, como autor, versión, etc.
{
    'name': 'Fleet y Firma',
    'version':'1.0',
    'category': 'Flota',
    'summary':'Cambios de odoo.studio en Flota y firmas',
    'description': '''\
Cambios de odoo.studio en Flota y firmas
============================


\n
''',
    'author': 'TYSAMNCA',
    'website': 'https://tysamnca.com',
    #data, es una lista donde se agregan todas las vistas del módulo, es decir los archivos.xml y archivos.csv.
    'data': [
             'views/fleet_view.xml',
            ],
    #depends,  es una lista donde se agregan los módulos que deberían estar instalados (Módulos dependencia) para que el modulo pueda ser instalado en Odoo.
    'depends': ['base','fleet', 'website_sign', 'tys_calling'],
    'css': [],

    #'installable': True,
    #'auto_install': False,
    'application': True,
}