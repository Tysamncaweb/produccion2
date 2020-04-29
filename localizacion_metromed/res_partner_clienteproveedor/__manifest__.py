# -*- coding: UTF-8 -*-

{
    "name": "res_partner_clienteproveedor",
    "version": "1.0",
    "author": "uedwin, itobetter@gmail.com",
    'depends' : [#"hr",
                 "base","base_vat"],
    "data": [
        'view/res_partner_view.xml',
             ],
    'category': 'Purchase Management',
    "description": """
    Modifica la clase res_partner agregando funcionalidad
    """,
    'installable': True,
}
