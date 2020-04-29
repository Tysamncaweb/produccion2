# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
from odoo import tools
from odoo import fields, models, api,exceptions
from lxml import etree
import time

_MESES = [(1,'Enero'),
          (2,'Febrero'),
          (3,'Marzo'),
          (4,'Abril'),
          (5,'Mayo'),
          (6,'Junio'),
          (7,'Julio'),
          (8,'Agosto'),
          (9,'Septiembre'),
          (10,'Octubre'),
          (11,'Noviembre'),
          (12,'Deciembre')]

class islr_historical_data_report(models.TransientModel):
    _name = 'islr.historical.data.report'
    _description = 'Resumen por concepto'

   # start_period_id = fields.Many2one('account.period', 'Periodo de Inicio')
   # end_period_id = fields.Many2one('account.period', 'Periodo de Fin')
    #date1 = fields.date('Start of period', required=True),
    #date2 = fields.date('End of period', required=True),



    #date1 = lambda *a: time.strftime('%Y-01-01'),
        #'date2 = lambda *a: time.strftime('%Y-%m-%d')
         #    }

    def _get_last_day_of_month(self,month, year):
        if 1 <= month <=12:
            if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
                return 29
            return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
        else:
            return 0

    def _get_name_of_month(self, month):
        if 1 <= month <= 12:
            return [0, 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'][month]
        else:
            return 0

    def _history_x_fiscalyear(self, date1=None,date2=None,partner_id=None):
        report_obj = self.env('islr.wh.historical.data')
#        period_obj = self.env('account.period')
        res = {}
        p_ids = []
        if date1 and date2:
            start = date1.split('-')
            start_str = ('0' + start[1]) if len(start[1]) == 1 else start[1] + '/' + start[0]
            end = date2.split('-')
            end_str = ('0' + end[1]) if len(end[1]) == 1 else end[1] + '/' + end[0]
     #       p_ids = period_obj.search(cr, uid, ['|',('name','=',start_str),('name','=',end_str)])
 #      # elif periods:
 #       #    p_ids = periods
        #if p_ids:
        #    periods.append(p_ids[0])
        # p_ids = period_obj.search(cr, uid, [])
        # if not p_ids in periods:
        #     periods.append(p_ids[0])
        #TODO leer el code desde un parametro del modulo
        if p_ids:
            res = report_obj.get_sumary_data( partner_id, p_ids)
        for r in res:
            mes = int(r.get('name').split('/')[0])
            mes_str = self._get_name_of_month(mes)
            r.update({'mes':mes_str})
            r.update({'fiscal_name':r.get('fiscal_name')})
        if not res:
            raise exceptions.except_orm(('Advertencia!'),('No hay datos para el periodo seleccionado!'))
        return res

    def print_report(self):
        res = {}
        active_ids = self._context and self._context.get('active_ids', []) or False
        data = self.read(self)[0]
        partner_data = {}
        partner = self.env('res.partner').browse(active_ids[0])
        partner_data = {
            'name':partner.name,
            'vat':partner.vat[2] + '-' + partner.vat[3:11] + '-' + partner.vat[11],
            'street':partner.street,
        }
        # if data['date1'] and data['date2']:
        #     res = self._history_x_fiscalyear(cr,uid, data['date1'],data['date2'],active_ids)
        if data['start_period_id'] and data['end_period_id']:
            res = self._history_x_fiscalyear( None, None, active_ids)

        data.update({
            'datos':res,
            'name':partner_data['name'],
            'vat':partner_data['vat'],
            'street':partner_data['street'],
        })
        datas = {
            'ids': active_ids,
            'model': 'hr.payslip.run',
            'form': data,
             }
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'islr.wh.historical.data',
                'datas': datas,
                }

islr_historical_data_report()