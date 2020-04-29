# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, api, _, fields
from logging import getLogger


_logger = getLogger(__name__)

class pago_nomina(models.TransientModel):
    _inherit = "account.wizard.generacion.txtfile"
    _name = "account.wizard.empl.afiliacion"


    facturas_ids = fields.Many2many('hr.contract', string='Facturas', store=True)
    date_from2 = fields.Date('Date From')
    date_to2 = fields.Date('Date To')
    agre_actua = fields.Boolean()
    buscaremple = fields.Many2many('hr.employee', string='Empleados')

    @api.multi
    def afilactivo(self,cr):
        self.agregarban = self.env['hr.employee'].search(
            [('fecha_inicio', '<=', self.date_to2), ('fecha_inicio', '>=', self.date_from2)])
        _logger.info("\n\n\n {} \n\n\n".format(self.agregarban))

        self.eliminarban = self.env['hr.employee'].search(
            [('fecha_fin', '<=', self.date_to2), ('fecha_fin', '>=', self.date_from2)])
        _logger.info("\n\n\n {} \n\n\n".format(self.eliminarban))
        # Se crea el archivo Txt
        file = open("archivo.txt", "w")
        #/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # se recorre los empleados segun la fecha de ingreso y el rango de fechas seleccionado quienes deben ser agregados
        for info in self.agregarban:
            cuenta = info.account_number_2
            if cuenta:
                filtro = cuenta[0:4]
            else:
                filtro = '1234'
            if filtro == '0171':
                letra = info.nationality
                ncedu = info.identification_id_2
                catcedu = len(ncedu)
                if catcedu == 7:
                    catce = '00'
                if catcedu == 8:
                    catce = '0'
                # catce, es los ceros que se agregan antes de la cedula
                # ncedu, es el numero de cedula
                # traigo los nombrs y apellidos
                name1 = info.firstname
                name1 = str(name1)
                name1 = name1.upper()
                apellido = info.lastname
                apellido = str(apellido)
                apellido = apellido.upper()
                if name1 == 'FALSE':
                    name1 = ' '
                if apellido == 'FALSE':
                    apellido = ' '

                # imprimo en el txt
                lineas = [letra,
                          catce,
                          ncedu,
                          ';',
                          name1,
                          ' ',
                          apellido,
                          ';',
                          info.account_number_2,
                          ';',
                          'BANCO ACTIVO, BANCO UNIVERSAL, C. A.',
                          ';',
                          info.work_email,
                          ';',
                          info.mobile_phone,
                          ';',
                          'A'

                          ]
                for l in lineas:
                    file.write(str(l))
                file.write('\n')
        #//////////////////////////////////////////////////////////////////////////////////////////////////////////////
        #segun las fechas se busca quienes deben ser eliminados
        for info in self.eliminarban:
            cuenta = info.account_number_2
            if cuenta:
                filtro = cuenta[0:4]
            else:
                filtro = '1234'
            if filtro == '0171':
                letra = info.nationality
                ncedu = info.identification_id_2
                catcedu = len(ncedu)
                if catcedu == 7:
                    catce = '00'
                if catcedu == 8:
                    catce = '0'
                # catce, es los ceros que se agregan antes de la cedula
                # ncedu, es el numero de cedula
                # traigo los nombrs y apellidos
                name1 = info.firstname
                name1 = str(name1)
                name1 = name1.upper()
                apellido = info.lastname
                apellido = str(apellido)
                apellido = apellido.upper()
                if name1 == 'FALSE':
                    name1 = ' '
                if apellido == 'FALSE':
                    apellido = ' '

                # imprimo en el txt
                lineas = [letra,
                          catce,
                          ncedu,
                          ';',
                          name1,
                          ' ',
                          apellido,
                          ';',
                          info.account_number_2,
                          ';',
                          'BANCO ACTIVO, BANCO UNIVERSAL, C. A.',
                          ';',
                          info.work_email,
                          ';',
                          info.mobile_phone,
                          ';',
                          'D'

                          ]
                for l in lineas:
                    file.write(str(l))
                file.write('\n')
#///////////////////////////////////////////////////actualizar funcion segundo llenado/////////////////////////////////////
        #se recorre los empleados para modificacion de datos..
        for info in self.buscaremple:
            cuenta = info.account_number_2
            if cuenta:
                filtro = cuenta[0:4]
            else:
                filtro = '1234'
            if filtro == '0171':
                letra = info.nationality
                ncedu = info.identification_id_2
                catcedu = len(ncedu)
                if catcedu == 7:
                    catce = '00'
                if catcedu == 8:
                    catce = '0'
                # catce, es los ceros que se agregan antes de la cedula
                # ncedu, es el numero de cedula
                # traigo los nombrs y apellidos
                name1 = info.firstname
                name1 = str(name1)
                name1 = name1.upper()
                apellido = info.lastname
                apellido = str(apellido)
                apellido = apellido.upper()
                if name1 == 'FALSE':
                    name1 = ' '
                if apellido == 'FALSE':
                    apellido = ' '

                 # imprimo en el txt
                lineas = [letra,
                          catce,
                          ncedu,
                          ';',
                          name1,
                          ' ',
                          apellido,
                          ';',
                          info.account_number_2,
                          ';',
                          'BANCO ACTIVO, BANCO UNIVERSAL, C. A.',
                          ';',
                          info.work_email,
                          ';',
                          info.mobile_phone,
                          ';',
                          'A'

                          ]
                for l in lineas:
                    file.write(str(l))
                file.write('\n')


        file.close()
        nombretxt = 'BeneficiarioparalaNómina.txt'
        nameclass = 'account.wizard.empl.afiliacion'
        return self.imprimir_txt(nombretxt, nameclass)





