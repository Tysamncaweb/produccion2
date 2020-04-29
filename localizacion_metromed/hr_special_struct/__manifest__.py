# -*- encoding: UTF-8 -*-
#    Create:  randara** 19/07/2016 **  **
#    type of the change:  New module
#    Comments: Creacion del modulo de hr_special_splip

{
    'name' : 'hr_special_struct',
    'version' : '1.0',
    'author' : 'TYSAMNCA',
    'website': 'http://www.tysamnca.com',
    'category' : 'Human Resources',
    'depends': ["hr_payroll", "hr", "base" ],
    'description': """

Modulo para Nominas Especiales.\n
==============================================\n
Colaboracion: Rafael A Andara D\n
\n
Este Modulo crear la funcionalidad de nominas Especiales donde se pueden definir y configurar nominas de pago\n
no continuo y no especificado en el contrato es util para nominas tipo\n
    - Cestatiket\n
    - Liquidacion\n
    - Utilidades\n
    - Pago de Guarderias\n
    Entre otras.\n
    """,
    'data': [ "views/hr_special_struct.xml"
         ],
    'installable': True,
    'auto_install': True,

}
