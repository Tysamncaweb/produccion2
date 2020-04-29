# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, api, fields
from logging import getLogger

_logger = getLogger(__name__)

class bono(models.TransientModel):
    _inherit = "account.wizard.generacion.txtfile"
    @api.multi
    def print_bono1(self):
        if self.bancose == 'provin':
            # /////////////////////////////Creacion del archivo .txt en carpeta local odoo.///////////////////////////////////
            file = open("archivo.txt", "w")
            # /////////7////////calculos y ceacion de datos para el .txt/////////////////////////////////////////////////////
            self.invoices = self.env['hr.payslip'].search(
                [('date_to', '<=', self.date_to), ('date_from', '>=', self.date_from)])
            _logger.info("\n\n\n {} \n\n\n".format(self.invoices))

            for invoice in self.invoices:
                # traigo el numero de cuenta
                cuenta = invoice.employee_id.account_number_2
                if cuenta:
                    filtro = cuenta[0:4]
                else:
                    filtro = '1234'
                if filtro == '0108':
                    letra = invoice.employee_id.nationality
                    ncedu = invoice.employee_id.identification_id_2
                    catcedu = len(ncedu)
                    if catcedu == 8:
                        catce = '00'
                    if catcedu == 7:
                        catce = '000'
                    # catce, es los ceros que se agregan antes de la cedula
                    # ncedu, es el numero de cedula

                    # traigo los nombrs y apellidos
                    name1 = invoice.employee_id.firstname
                    name1 = str(name1)
                    name1 = name1.upper()
                    name2 = invoice.employee_id.firstname2
                    name2 = str(name2)
                    name2 = name2.upper()
                    apellido = invoice.employee_id.lastname
                    apellido = str(apellido)
                    apellido = apellido.upper()
                    apellido2 = invoice.employee_id.lastname2
                    apellido2 = str(apellido2)
                    apellido2 = apellido2.upper()
                    if name1 == 'FALSE':
                        name1 = ' '
                    if name2 == 'FALSE':
                        name2 = ' '
                    if apellido == 'FALSE':
                        apellido = ' '
                    if apellido2 == 'FALSE':
                        apellido2 = ' '


                    # calculo del  monto total de nomina
                    busqueda = self.env['hr.salary.rule.category'].search([('id', '!=', 0)])
                    if busqueda:
                        for a in busqueda:
                            if a.name == 'Net':
                                ttotal = a.id
                    busqueda2 = self.env['hr.payslip.line'].search([('id', '!=', 0)])
                    for vip in invoice.line_ids:
                        for vip2 in busqueda2:
                            if vip == vip2:
                                if vip2.category_id.id == ttotal:
                                    totalpago = vip2.total

                    totalpago = float("{0:.2f}".format(totalpago))
                    totalpago = str(totalpago)
                    for i in range(0, len(totalpago)):
                        if (totalpago[i] == '.'):
                            cds = totalpago[i + 1:]
                    if len(cds) == 2:
                        ceroextra = '0'
                        imprimir0 = ''
                    else:
                        ceroextra = ''
                        imprimir0 = '0'

                    totalpago = totalpago.replace(".", "")
                    totalpago= str(totalpago).zfill(14) #agrega ceros delente del pago segun lo establecido por el banco en su formato
                    # imprimo en el txt
                    lineas = [cuenta,
                              ' ',
                              letra,
                              catce,
                              ncedu,
                              ' ',
                              ceroextra,
                              totalpago,
                              imprimir0,
                              ' ',
                              name1,
                              ' ',
                              name2,
                              ' ',
                              apellido,
                              ' ',
                              apellido2
                              ]
                    for l in lineas:
                        file.write(str(l))
                    file.write('\n')

            file.close()
            nombretxt = 'Banco Provincial Pago Nómina período de %s a %s.txt'%(self.date_from,self.date_to)
            nameclass = 'account.wizard.generacion.txtfile'
            return self.imprimir_txt(nombretxt, nameclass)


