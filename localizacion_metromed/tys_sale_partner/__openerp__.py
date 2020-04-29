#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Luis Torres.
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Torres
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name" : "Datos del Cliente en Venta",
     'version' : '1.0',
    'author' : 'TYSAMNCA',
    'website': 'http://www.tysamnca.com',
    "category": "Stock",
    "summary": "Modifica sale",
    "description": """

==============================================\n
\n
     -Se agregan los Campos RIF y CODIGO del cliente en Pedido de Venta.
==============================================\n
    colaborador: Edwin Uranga
                   """,
    "depends" : ["base", "sale", "delivery",
                 "tys_product_pricelist_type"
                ],
    'data': [
        "view/sale_view.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
