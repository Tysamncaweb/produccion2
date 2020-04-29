from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date, timedelta

from odoo.exceptions import ValidationError
import urllib
from odoo import http


class report_callcenter_all(models.Model):
    _name = "report.callcenter"
    _description = "Report CallCenter"

    date_from = fields.Date(string='Fecha Inicio')
    date_to = fields.Date(string='Fecha Fin')
    sede = fields.Many2one('headquarter')
    all = fields.Boolean('Todas',defautl = False)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    services = fields.Many2many('service.type', string='Reporte', store=True)


   # @http.route('/example', type='http', auth='public', website=True)
   # def render_example_page(self):
    #    prueba = http.request.env['report.callcenter'].sudo().search([])
     #   return http.request.render('tys_calling.tys_calling.report_services_sede', {'pruebas': prueba})



    @api.multi
    def print_facturas(self, data):
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
                             'model': 'report.tys_calling.report_services_sede',
                             'form': {
                                 'datas': datas,
                                 'date_from': self.date_from,
                                 'date_to': self.date_to,
                                 'sede': self.sede.id,
                                 'all':self.all,
                             },
                             'context': self._context
                        }
                return self.env.ref('tys_calling.report_services_for_sede').report_action(self, data=data, config=False)
            else:
                raise ValidationError('Advertencia! No existen llamadas entre las fechas seleccionadas')


        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.


class ReportAttendanceRecap(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.tys_calling.report_services_sede'


    @api.model
    def get_report_values(self, docids, data=None):
        date_start = datetime.strptime(data['form']['date_from'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_to'], DATE_FORMAT)
        sede = data['form']['sede']
        all = data['form']['all']
        # date_diff = (date_end - date_start).days

        docs = []
        service = []
        country = []
        service_sede = []
        if all == True:
            sedes = self.env['headquarter'].search([('id', '!=', 0)])
        else:
            sedes = self.env['headquarter'].search([('id', '=', sede)])
        services = self.env['service.type'].search([('id', '!=', 0)])
        calling = self.env['calling'].search([('id', '!=', 0), ('calling_date', '>=', date_start.strftime(DATETIME_FORMAT)),
                ('calling_date', '<=', date_end.strftime(DATETIME_FORMAT))])
        count = 0
        d = 0
        cant_servicios = 0

        for sede in sedes:
            d += 1
            presence_count = self.env['calling'].search_count([
                ('calling_headquarter', '=', sede.id),
                ('calling_date', '>=', date_start.strftime(DATETIME_FORMAT)),
                ('calling_date', '<=', date_end.strftime(DATETIME_FORMAT)),
            ])

            docs.append({
                'sede': sede.name,
                'id': sede.id,

            })

            for servicios in services:
                self.env.cr.execute("SELECT COUNT(calling_service_type) FROM calling WHERE calling_headquarter=%s AND calling_date>=%s AND calling_date<=%s AND calling_service_type=%s AND state!='cancel'", (sede.id, date_start, date_end, servicios.id))
                var1 = self.env.cr.fetchone()[0]
                count += 1
                country.append(var1)


            self.env.cr.execute("SELECT COUNT(state) FROM calling WHERE calling_headquarter=%s AND calling_date>=%s AND calling_date<=%s AND state='cancel'",(sede.id, date_start, date_end,))
            var3 = self.env.cr.fetchone()[0]
            count += 1
            country.append(var3)


        for servicios in services:
            self.env.cr.execute("SELECT COUNT(calling_service_type) FROM calling WHERE calling_service_type=%s AND calling_date>=%s AND calling_date<=%s AND state!='cancel'",(servicios.id, date_start, date_end))
            var2 = self.env.cr.fetchone()[0]
            service_sede.append(var2)

        self.env.cr.execute("SELECT COUNT(state) FROM calling WHERE calling_date>=%s AND calling_date<=%s AND state='cancel'",( date_start, date_end))
        var4 = self.env.cr.fetchone()[0]
        service_sede.append(var4)

        for type_service in services:
            cant_servicios += 1
            service.append({
                'services': type_service.service_type_name,
                'id': type_service.id,

            })


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': date_end.strftime(DATE_FORMAT),
            'docs': docs,
            'service': service,
            'country': country,
            'd': d,
            'count': count,
            'service_sede': service_sede,
            'cant_servicios': cant_servicios,

        }






