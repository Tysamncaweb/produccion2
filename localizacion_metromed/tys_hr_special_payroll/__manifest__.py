# coding: utf-8
##############################################################################
#
# Copyright (c) 2016 Tecnología y Servicios AMN C.A. (http://tysamnca.com/) All Rights Reserved.
# <contacto@tysamnca.com>
# <Teléfono: +58(212) 237.77.53>
# Caracas, Venezuela.
#
# Colaborador: <<nombre colaborador>> <e-mail del colaborador>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    'name': 'Nominas Especiales',
    'version': '1.0',
    'category': 'Recursos Humanos',
    'summary': 'Agrega funcionalidades comunes para el calculo de las nóminas especiales',
    'description': u"""
NÓMINAS ESPECIALES
==================================

Agrega funcionalidades comunes para el cálculo de las nóminas especiales:
    * Cálculo del tiempo de servicio del empleado
    * Cálculo del sueldo promedio
    * Cálculo de alícuota de bono vacacional
    * Cálculo de alícuota de utilidades

    """,

    'author': 'TYSAMNCA',
    'website': 'https://tysamnca.com',
    'depends': ['hr','hr_payroll','hr_contract','hr_config_parameter'],
    'data': ['views/hr_special_payroll_view.xml',
             #'data/hr_special_payroll_data.xml'
              ],
    #'demo': [],
    #'test': [],
    'installable': True,
}
