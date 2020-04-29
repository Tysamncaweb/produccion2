# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Contract Aditional Data',
    'version': '1.1',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'sequence': 104,
    'summary': 'Adds aditional fields to hr_contract module',
    'description': '''
        Agrega los siguientes campos adicionales al contrato de los empleados:\n
            * Bono Nocturno\n
            * Dias de Sueldo Pendiente\n
            * Feriados\n
            * Feriados no Laborados\n
            * Horas extraordinarias Diurnas\n
            * Retroactivo de Sueldo\n
            * Aporte Patronal F.A.O.V.\n
            * Aporte Patronal  Fondo de Ahorro\n
            * Aporte Patronal P.I.E.\n
            * Aporte Patronal S.O.S.\n
            * Fondo de Caja de Ahorro\n
            * Horas no Laboradas\n
            * Inasistencias Injustificadas\n
            * Permiso no Remunerados Dias\n
            * Permiso no Remunerados Horas\n
            * Retenciones  F.A.O.V.\n
            * Retenciones Fondo de Ahorro\n
            * Retenciones I.S.L.R.\n
            * Retenciones P.I.E.\n
            * Retenciones  S.O.S.\n
    ''',
    'depends': [
        'base_setup',
        'hr',
        'hr_contract',
        'hr_payroll',
    ],
    'data': [
        'views/hr_contract_add_fields_view1.xml',
        #'views/respamldo.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}