# coding: utf-8

{
    'name' : 'Split Invoices',
    'version' : '1.0',
    'author' : 'TYSAMNCA',
    'category' : 'Localization',
    'description' : """
Ajustes y modificaciones para el maximo de lineas de factura.
===================================================

    * Permite definir un número máximo de líneas de factura
    * Se debe verificar que el número configurado representa el número de líneas del reporte 
    o el número de items por factura

Colaborador: Kelvis Pernia
    """,
    'website': 'http://www.tysamnca.com',
    'depends' : ['account'],
    'data': ['view/company_view.xml'],
    'test': ['test/spl_test.yml'],
    'installable': True,
    'auto_install': False,
}
