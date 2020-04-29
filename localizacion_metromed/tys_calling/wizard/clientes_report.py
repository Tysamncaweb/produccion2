from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date, timedelta

from odoo.exceptions import ValidationError
import urllib
from odoo import http


class clientes_callcenter(models.Model):
    _name = "clientes.callcenter"
    _description = "Report Clientes CallCenter"


    date_from = fields.Date(string='Fecha Inicio')
    date_to = fields.Date(string='Fecha Fin')
    cliente = fields.Many2one('res.partner')
    all_clients = fields.Boolean('Clientes',defautl = False)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

    @api.multi
    def print_clientes(self, data):
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
                             'model': 'report.tys_calling.report_services_clientes',
                             'form': {
                                 'datas': datas,
                                 'date_from': self.date_from,
                                 'date_to': self.date_to,
                                 'cliente':self.cliente.id,
                                 'all_clients':self.all_clients,
                             },
                             'context': self._context
                        }
                return self.env.ref('tys_calling.report_services_for_clientes').report_action(self, data=data, config=False)
            else:
                raise ValidationError('Advertencia! No existen llamadas entre las fechas seleccionadas')

class ReportServiciosClientes(models.AbstractModel):

    _name = 'report.tys_calling.report_services_clientes'


    @api.model
    def get_report_values(self, docids, data=None):
        date_start = datetime.strptime(data['form']['date_from'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_to'], DATE_FORMAT)
        cliente = data['form']['cliente']
        all_clients = data['form']['all_clients']

        # date_diff = (date_end - date_start).days

        docs = []
        servicios_clientes = []
        total_servicios = []
        service_sede = []
        status = ['progress', 'complete', 'cancel']
        if all_clients == True:
            clientes = self.env['res.partner'].search([('customer','=',True),('active_client','=',True)])
            d = 3
        else:
            clientes = self.env['res.partner'].search([('id', '=', cliente)])
            d = 0
        count_atendidos = 0
        cant_servicios = 0

        for nombres_clientes in clientes:
            for estado in status:
                self.env.cr.execute(
                    "SELECT COUNT(state) FROM calling WHERE calling_client=%s AND calling_date>=%s AND calling_date<=%s  AND state=%s",
                    (nombres_clientes.id, date_start, date_end, estado))
                atendidos = self.env.cr.fetchone()[0]
                count_atendidos += 1
                servicios_clientes.append(atendidos)

            docs.append({
                'nombres_clientes': nombres_clientes.name,
            })

    #-------------------TOTALES DE LOS SERVICIOS POR CLIENTES--------------
        for estado in status:
            self.env.cr.execute(
                "SELECT COUNT(state) FROM calling WHERE calling_date>=%s AND calling_date<=%s AND state=%s",
                (date_start, date_end, estado))
            total_atendidos = self.env.cr.fetchone()[0]
            total_servicios.append(total_atendidos)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': date_end.strftime(DATE_FORMAT),
            'docs': docs,
            'count_atendidos': count_atendidos,
            'servicios_clientes': servicios_clientes,
            'all_clients':all_clients,
            'd': d,
           # 'total_servicios': total_servicios,

        }
