# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, api, fields
from logging import getLogger

_logger = getLogger(__name__)

class bono(models.TransientModel):
    _inherit = "account.wizard.generacion.txtfile"
    @api.multi
    def print_bono2(self):
        VAR = 0
        VAR2 = 0
        concepto2 = self.concepto.upper()
        totalpago = 0
        if self.bancose == 'activo':
            # /////////////////////////////Creacion del archivo .txt en carpeta local odoo///////////////////////////////////
            file = open("archivo.txt", "w")
            # /////////7////////calculos y ceacion de datos para el .txt/////////////////////////////////////////////////////
            self.invoices = self.env['hr.payslip'].search(
                [('date_to', '<=', self.date_to), ('date_from', '>=', self.date_from)])
            _logger.info("\n\n\n {} \n\n\n".format(self.invoices))

            date_f = str(self.date_imp)

            a = date_f[0:4]
            m = date_f[5:7]
            d = date_f[8:]
            #saco el encabezado
            for invoice in self.invoices:
                # traigo el numero de cuenta
                cuenta = invoice.employee_id.account_number_2
                if cuenta:
                    filtro = cuenta[0:4]
                else:
                    filtro = '1234'

                if filtro == '0171':
                    VAR2 += 1

                    for n in invoice.line_ids:
                        #varsuma = n.total
                        #varsuma = float("{0:.2f}".format(varsuma))..
                        totalpago += n.total
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
            #escribo en el txt
            totalpago = totalpago.replace(".", ",")
            lineas = ['H',
                      ';',
                      VAR2,
                      ';',
                      totalpago,
                      imprimir0,
                      ';',
                      concepto2,
                      ';',
                      self.nlote,
                      ';',
                      d,m,a]
            for l in lineas:
                file.write(str(l))
            file.write('\n')
            for invoice in self.invoices:
                # traigo el numero de cuenta
                cuenta = invoice.employee_id.account_number_2
                if cuenta:
                    filtro = cuenta[0:4]
                else:
                    filtro = '1234'
                if filtro == '0171':
                    letra = invoice.employee_id.nationality
                    ncedu = invoice.employee_id.identification_id_2
                    catcedu = len(ncedu)
                    if catcedu == 7:
                        catce = '00'
                    if catcedu == 8:
                        catce = '0'
                    # catce, es los ceros que se agregan antes de la cedula
                    # ncedu, es el numero de cedula
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
                    totalpago = totalpago.replace(".", ",")
                    VAR += 1
                    # imprimo en el txt
                    lineas = ['P',
                              ';',
                              letra,
                              catce,
                              ncedu,
                              ';',
                              totalpago,
                              imprimir0,
                              ';',
                              concepto2,
                              ';',
                              VAR,
                              ';',
                              '000'
                              ]
                    for l in lineas:
                        file.write(str(l))
                    file.write('\n')


            file.close()
            nombretxt = 'CargaMasivadepagodeNómina.txt'
            nameclass =  'account.wizard.generacion.txtfile'
            return self.imprimir_txt(nombretxt,nameclass)


