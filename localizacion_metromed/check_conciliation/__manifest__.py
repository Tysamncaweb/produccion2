# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Creado: 28/12/2015
# Requerimiento CAVIM nro 1-01-03-0010:
# "Agregar proceso de conciliacion de cheques y estado 'PAGADO' a los cheques cuando sean
#  cobrados por los proveedores"
#
# autor: Roger Sosa.
#
##############################################################################

{
    'name': 'Conciliacion de Cheques',
    'version': '1.0',
    'depends': ['account', 'account_voucher','l10n_ve_account_check_duo'],
    'author': 'Colaboradores: Michel Castillo y Maria Carreño',
    'description': """
        A traves de este modulo se implanta la solucion al requerimiento nro 1-01-03-0010
        \n- Se añade proceso de conciliacion de cheques, asignando una cuenta transitoria a la chequera
        \n- El asiento contable del cheque emitido se hace contra la cuenta transitoria, y no sobre el banco directamente
        \n- Cuando se confirma el cobro del cheque, se realiza el asiento desde la transitoria contra el banco
        \n- Se añade el estatus "PAGADO" a los cheques
    """,
    'demo': [],
    'test': [],
    'data': ['view/account_checkbook_view.xml',
             'view/account_check_duo_view.xml'
              ], #, 'check_conciliation_sequence.xml'
    'auto_install': False,
    'installable': True,
    'application': False,
}