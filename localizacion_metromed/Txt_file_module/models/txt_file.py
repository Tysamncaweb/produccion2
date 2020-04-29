# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details..

from datetime import datetime, timedelta
from odoo import models, api, fields
import base64
from logging import getLogger

class men_descarga(models.Model):
    _name = 'men.descarga'
    name = fields.Text("Título", required="True")

class men_valor(models.Model):
    _name = 'men.valor'
    name = fields.Char('Monto Bono de Alimentación')


_logger = getLogger(__name__)


class bono(models.TransientModel):
    _name = "account.wizard.generacion.txtfile"

    facturas_ids = fields.Many2many('hr.payslip', string='Facturas', store=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    bancose = fields.Selection([('activo', 'Banco Activo'),('provin', 'Banco Provincial')], string="Banco a Generar")
    date_imp = fields.Date('Date Imp')
    nlote = fields.Integer()
    concepto = fields.Char(string = "Concepto de pago")

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Archivo Preparado', filters='.xls', readonly=True)
    name = fields.Char('File Name')


    @api.multi
    def print_bono(self):
        if self.bancose == 'provin':
            return self.print_bono1()
        if self.bancose == 'activo':
            return self.print_bono2()

    @api.multi
    def imprimir_txt(self,nombretxt,nameclass):
        # Apertura del archivo TXT generado y enviado a la ventana
        r = base64.b64encode(open("archivo.txt", 'rb').read())
        self.write({'state': 'get', 'report': r, 'name': nombretxt})
        return {
            'name': ("Descarga de archivo"),
            'type': 'ir.actions.act_window',
            'res_model': nameclass,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }