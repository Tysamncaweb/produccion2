from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date, timedelta

from odoo.exceptions import ValidationError
import urllib
from odoo import http


class servicios_callcenter(models.Model):
    _name = "servicios.callcenter"
    _description = "Report Servicios CallCenter"


    date_from = fields.Date(string='Fecha Inicio')
    date_to = fields.Date(string='Fecha Fin')
    servicio = fields.Many2one('service.type')
    all_services = fields.Boolean('Servicios',defautl = False)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

    @api.multi
    def print_servicios(self, data):
        #pruebas = self.env['calling'].search([('state', '=', 'active')])
       # self.nuevo = self.env['account.invoice'].search([('type','=','out invoice')])
        """Call when button 'Print_facturas' clicked.
        """


        if self.date_from and self.date_to:
            fecha_inicio = self.date_from
            fecha_fin = self.date_to

            if datetime.strptime(fecha_inicio, DATE_FORMAT) >= datetime.strptime(fecha_fin, DATE_FORMAT):
                raise ValidationError('Advertencia! La fecha de inicio no puede ser superior a la fecha final')

            fecha_actual = str(date.today())
            if datetime.strptime(fecha_inicio, DATE_FORMAT) > datetime.strptime(fecha_actual, DATE_FORMAT):
                raise ValidationError('Advertencia! La fecha de inicio no puede ser mayor a la fecha actual')
            elif datetime.strptime(fecha_fin, DATE_FORMAT) > datetime.strptime(fecha_actual, DATE_FORMAT):
                raise ValidationError('Advertencia! La fecha de final no puede ser mayor a la fecha actual')

            calling_obj = self.env['calling']
            calling_ids = calling_obj.search(
                [('calling_date', '>=', fecha_inicio), ('calling_date', '<=', fecha_fin)])
            if calling_ids:
                ids = []
                for id in calling_ids:
                    ids.append(id.id)
                datas = self.read(self.ids)[0]
                data = {
                             'ids': ids,
                             'model': 'report.tys_calling.report_servicios',
                             'form': {
                                 'datas': datas,
                                 'date_from': self.date_from,
                                 'date_to': self.date_to,
                                 'servicio':self.servicio.id,
                                 'all_services':self.all_services
                             },
                             'context': self._context
                        }
                return self.env.ref('tys_calling.report_services_for_servicios').report_action(self, data=data, config=False)
            else:
                raise ValidationError('Advertencia! No existen llamadas entre las fechas seleccionadas')

class ReportServicios(models.AbstractModel):

    _name = 'report.tys_calling.report_servicios'


    @api.model
    def get_report_values(self, docids, data=None):
        date_start = datetime.strptime(data['form']['date_from'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_to'], DATE_FORMAT)
        servicio = data['form']['servicio']
        all_services = data['form']['all_services']
        # date_diff = (date_end - date_start).days

        docs = []
        service_adicionales = []
        total_servicios = []
        servicios_atendidos = []
        if all_services == True:
            servicios = self.env['service.type'].search([('id','!=',0)])
            d=3
        else:
            servicios = self.env['service.type'].search([('id', '=', servicio)])
            d = 0
        type_servicios_adicionales = []
        status = ['progress', 'complete', 'cancel']
        #servicios = self.env['service.type'].search([('id', '!=', 0)])
       # servicios_adicionales = self.env['additional.service.type'].search([('id', '!=', 0)])

        count_atendidos = 0

        count_adicionales = 0
        variable = 0

        for servicio in servicios:
            for estado in status:

                self.env.cr.execute(
                    "SELECT COUNT(state) FROM calling WHERE calling_service_type=%s AND calling_date>=%s AND calling_date<=%s  AND state=%s",
                    (servicio.id, date_start, date_end, estado,))
                atendidos = self.env.cr.fetchone()[0]
                count_atendidos += 1
                servicios_atendidos.append(atendidos)

            docs.append({
                'servicios': servicio.service_type_name,
            })

        '''for ser_adicionales in servicios_adicionales:
            for estado in status:
                self.env.cr.execute(
                    "SELECT COUNT(state) FROM calling WHERE calling_additional_service_type=%s AND calling_date>=%s AND calling_date<=%s  AND state=%s",
                    (ser_adicionales.id, date_start, date_end, estado,))
                adicionales_atendidos = self.env.cr.fetchone()[0]
                count_adicionales += 1
                type_servicios_adicionales.append(adicionales_atendidos)

            service_adicionales.append({
                'service_adicionales': ser_adicionales.additional_service_type_name,
            })'''

        # -------------------TOTALES DE LOS SERVICIOS ATENDIDOS, COMPLETADOS Y CANCELADOS --------------
        for estado in status:
            """self.env.cr.execute(
                "SELECT COUNT(state) FROM calling WHERE calling_additional_service_type!=%s AND calling_date>=%s AND calling_date<=%s AND state=%s",
                (variable, date_start, date_end, estado,))
            total_atendidos = self.env.cr.fetchone()[0]"""
            self.env.cr.execute(
                "SELECT COUNT(state) FROM calling WHERE calling_service_type!=%s AND calling_date>=%s AND calling_date<=%s AND state=%s",
                (variable, date_start, date_end, estado,))
            total_adicionales = self.env.cr.fetchone()[0]
            total_servicios.append(total_adicionales)


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': date_end.strftime(DATE_FORMAT),
            'docs': docs,
            'count_atendidos': count_atendidos,
            'd': d,
            #'service_adicionales': service_adicionales,
            'servicios_atendidos': servicios_atendidos,
           # 'type_servicios_adicionales': type_servicios_adicionales,
           # 'count_adicionales': count_adicionales,
            'total_servicios': total_servicios,

        }
