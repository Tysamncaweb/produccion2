# coding: utf-8
# from openerp import fields, models, api
from datetime import datetime, timedelta, date
import calendar
from odoo import fields, api, exceptions, models
from dateutil import relativedelta, rrule
#from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(models.Model):
    _inherit ='hr.payslip'

    @api.multi
    def get_years_service(self, date_start=None, date_end=None):
        dias = 0
        meses = 0
        anios = 0
        res = {}
        if date_start and date_end:
            antiguedad = relativedelta.relativedelta(datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT),
                                                     datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT))
            res = {
                'dias': antiguedad.days,
                'meses': antiguedad.months,
                'anios': antiguedad.years,
            }
        return res

    # @api.v7	06/05/2015
    def get_dias_bono_vacacional(self, tiempo_servicio):
        res = {}
        pay_days = []
        service_year = []
        asignacion = asignacionR = 0
        min_days = 0
        max_days = 0
        step_days = 0
        config_param = self.env['hr.config.parameter']
        if tiempo_servicio:
            min_days = int(config_param._hr_get_parameter('hr.payroll.vacation.min'))
            max_days = int(config_param._hr_get_parameter('hr.payroll.vacation.max'))

         #Si hay algun cambio en la ley de los dias que corresponden segun el tiempo de servicio para los dias de bono vacacional, se debe colocar Step_days y agregarlo como parametro
            #step_days = config_param._hr_get_parameter('hr.payroll.vacation.step')

            pay_days = min_days + ((tiempo_servicio['anios'] - 1) if tiempo_servicio['anios'] > 0 else 0) #* step_days
            pay_days = pay_days if pay_days < max_days else max_days

            if tiempo_servicio['anios'] == 0 and tiempo_servicio['meses'] >= 3:  # antiguedad menor a un anio y mayor a 3 meses
                asignacion = (float(tiempo_servicio['meses']) / float(12)) * float(pay_days)
                asignacionR = pay_days
            #TODO establecer la accion cuando tiene menos de 3 meses de antiguedad
            else:
                asignacion = pay_days
                asignacionR = asignacion
        else:
            raise exceptions.except_orm((u'No se han calculado los días de bono vacacional, debido a que\n'
                           u' no se ha cargado la lista de días a pagar por años de servicio.\n'
                           u' Por favor consulte con el administrador!'))
        res = {
            'asignacion': asignacion,
            'asignacionR': asignacionR,
        }
        return res

    # @api.v7
    def calculo_sueldo_promedio(self, employee_id, fecha_desde, meses, tipo_nomina=None, limite=None):
        config_obj = self.env['hr.config.parameter']
        if 'fideicomiso' in tipo_nomina.lower() :
            codes_str = config_obj._hr_get_parameter('hr.payroll.codigos.salario.integral.fideicomiso', True)
        elif 'vacaciones' in tipo_nomina.lower():
            codes_str = config_obj._hr_get_parameter('hr.payroll.codigos.salario.integral.vacaciones', True)
        elif 'utilidad' in tipo_nomina.lower():
            codes_str = config_obj._hr_get_parameter('hr.payroll.codigos.salario.integral.utilidades', True)
        elif 'liquidacion' in tipo_nomina.lower():
            codes_str = config_obj._hr_get_parameter('hr.payroll.codigos.salario.integral.liquidaciones', True)
        else:
            codes_str = config_obj._hr_get_parameter('hr.payroll.codigos.salario.integral', True)
        code = str(codes_str).strip().split(',')  # para obtener los conceptos a agregar al salario integrarel monto BRUTO a cobrar
        ultimo_sueldo = self.get_amount(code, employee_id.id, fecha_desde, meses, tipo_nomina, limite)  # para tomar la fecha en que se genera la nomina
        # ultimo_sueldo = self.get_amount(cr, uid, code, employee_id.id, fecha_desde, 0)     #para tomar la fecha maxima del rango en que se genera la nomina
        return ultimo_sueldo

    # @api.v7
    def get_amount(self, code=None, employee_id=None, fecha_desde=None, meses=0, tipo_nomina=None, limite=None):
        amount = 0.0
        promedio = 0.0
        domain_ps = []
        domain_psl = []
        p_ids = []
        payslip_line_obj = self.env['hr.payslip.line']
        payslip_run_obj = self.env['hr.payslip.run']
        if employee_id:
            domain_ps.append(('employee_id', '=', employee_id))
            domain_psl.append(('employee_id', '=', employee_id))

        domain_ps.append(('state', '=', 'done'))

        if not fecha_desde:
            fecha_desde = datetime.now().strftime('%Y-%m-%d')

        rango = self.rango_mes_anterior(fecha_desde, meses)
        if rango:
            if 'liquidacion' in tipo_nomina:
                domain_ps.append(('date_from', '<=', fecha_desde))
                payslip_ids = self.search( domain_ps, limit=limite)
            else:
                domain_ps.append(('date_from', '>=', rango[0]))
                domain_ps.append(('date_from', '<=', rango[1]))
                payslip_ids = self.search(domain_ps)
            if payslip_ids:
                for ps in payslip_ids:
                    payslip_run_ids = self.browse(ps.id)
                    for psr in payslip_run_ids:
                        if psr.payslip_run_id:
                            ids = payslip_run_obj.search([('id', '=',  psr.payslip_run_id.id),
                                        ('check_special_struct', '=', False)])
                            if ids:
                                p_ids.append(psr.id)
                        else:
                            for ps_id in payslip_ids:
                                p_ids.append(ps_id.id)
                domain_psl.append(('slip_id', 'in', p_ids))
            else:
                if tipo_nomina != 'normal':
                    raise exceptions.except_orm(('Advertencia!', u'No se han confirmado las nóminas correspondientes al mes anterior.\n \
                                                    Por favor verifique y proceda a realizar la confirmación requerida.'))
        if code:
            domain_psl.append(('code', 'in', code))

        payslip_line_ids = payslip_line_obj.search(domain_psl)


        if payslip_line_ids:
            for i in payslip_line_ids:
                amount = amount + i.amount

        return amount


    # @api.v7
    def calculo_alic_bono_vac(self, sueldo_normal, dias_b_v=0):
        config_obj = self.env['hr.config.parameter']
        alicuota = 0.0
        dias_str = config_obj._hr_get_parameter('hr.dias.x.mes')
        dias_x_anio = 	config_obj._hr_get_parameter('hr.payroll.max.dias.año')
        alicuota = (sueldo_normal / float(dias_str)) * (int(dias_b_v) / float(dias_x_anio))
        return alicuota

        # @api.v7
    def calculo_alic_util(self, sueldo_normal, alicuota_bv):
        config_obj = self.env['hr.config.parameter']
        alicuota = 0.0
        dias_str = config_obj._hr_get_parameter('hr.dias.x.mes')
        dias_x_anio = config_obj._hr_get_parameter('hr.payroll.max.dias.año')
        dias_max_str = config_obj._hr_get_parameter('hr.payroll.max.utili.days.year')
        fac_utilidades = float(dias_max_str) / float(dias_x_anio)
        alicuota = ((sueldo_normal / float(dias_str))) * fac_utilidades
        return alicuota


    def rango_mes_anterior(self, date_base, meses):
        date_range = []

        mes_anterior = datetime.strptime(date_base, DEFAULT_SERVER_DATE_FORMAT) - relativedelta.relativedelta(months=meses)
        local_date = datetime.strftime(mes_anterior, DEFAULT_SERVER_DATE_FORMAT).split('-')
        date_range.append(date(int(local_date[0]), int(local_date[1]), 1))  # primer dia del mes
        date_range.append(date(int(local_date[0]), int(local_date[1]),
                               calendar.monthrange(int(local_date[0]), int(local_date[1]))[1]))  # ultimo dia del mes

        return date_range


    def calcula_dias_x_periodo(self, date_from, date_to):
        res = {}
        sab = [5]
        dom = [6]
        lun = [0]
        laborales = [0, 1, 2, 3, 4]
        fecha_desde = date_from.split('-')
        fecha_hasta = date_to.split('-')
        date_from = datetime(int(fecha_desde[0]), int(fecha_desde[1]), int(fecha_desde[2]))
        date_to = datetime(int(fecha_hasta[0]), int(fecha_hasta[1]), int(fecha_hasta[2]))
        totalDiasLaborales = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=laborales).count()
        totalSabados = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=sab).count()
        totalDomingos = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=dom).count()
        totalLunes = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=lun).count()

        res = {
            'laborales': totalDiasLaborales,
            'sabados': totalSabados,
            'domingos': totalDomingos,
            'lunes': totalLunes,
        }
        return res

    def get_feriados_2(self, date_from, date_to):
        dias = totalHollydayWeekend = 0
        hollyday_on_w = [5, 6]
        test = self.env['hr.payroll.hollydays']

        hollyday_ids = test.search([('date_from','>=',date_from),
                                             ('date_from','<=',date_to),
                                             ('date_to','>=',date_from),
                                             ('date_to','<=',date_to)])
        if hollyday_ids:
           # hollydays = test.browse([id.id for id in hollyday_ids])
            for h in hollyday_ids:
                if h.date_from == h.date_to:
                    h_from = datetime.strptime(h.date_from, DEFAULT_SERVER_DATE_FORMAT)
                    h_to = datetime.strptime(h.date_to, DEFAULT_SERVER_DATE_FORMAT)
                    dias = dias + 1
                else:
                    h_from = datetime.strptime(h.date_from,DEFAULT_SERVER_DATE_FORMAT)
                    h_to = datetime.strptime(h.date_to,DEFAULT_SERVER_DATE_FORMAT)
                    diferencia = h_to - h_from
                    dias = dias + 1 + diferencia.days
                totalHollydayWeekend = totalHollydayWeekend + rrule.rrule(rrule.DAILY, dtstart=h_from, until=h_to,
                                                       byweekday=hollyday_on_w).count()
            dias = dias - totalHollydayWeekend
        return dias

    # Funcion que calcula la fraccion de dias de utilidades a pagar (artículo 131 de la lottt.)
    def get_fraccion_dias_util(self, cr, uid, ids, fecha_ingreso, fecha=None):
        rate = 1.0
        if not fecha_ingreso:
            raise exceptions.except_orm(('Advertencia!'),
                                 (u'La fecha de ingreso del empleado es inválida, por favor verifique.'))
        if not fecha:
            fecha = datetime.now().strftime('%Y-%m-%d')
        periodo = relativedelta.relativedelta(datetime.strptime(fecha, DEFAULT_SERVER_DATE_FORMAT),
                                              datetime.strptime(fecha_ingreso, DEFAULT_SERVER_DATE_FORMAT))
        if periodo.years == 0:
            restar_mes = self.get_first_workeday(cr, uid, ids, fecha_ingreso)
            meses = periodo.months
            if restar_mes:
                meses -= 1
            rate = meses / float(12)
        return rate


class hr_payroll_dias_vacaciones(models.Model):
    _name = 'hr.payroll.dias.vacaciones'
    _description = 'Factor de Calculo para las Vacaciones'


    service_years = fields.Integer('Años de Servicio', required=True)
    pay_days = fields.Integer('Dias a Pagar', required=True)

hr_payroll_dias_vacaciones()

class hr_payroll_utilidades(models.Model):
    _name = 'hr.payroll.utilidades'
    _description = u'Monto maximo de utilidades por año'



    utilidades_name = fields.Integer('Referencia', required=True)
    utilidades_pay_days = fields.Integer('Dias a Pagar', required=True)


    def get_last_util_max_days(self, year):
        days = 0
        if year:
            util_id = self.search([('utilidades_name','=', year)]) #, limit=1, order='utilidades_name, write_date desc')
        else:
            util_id = self.search([])#, limit=1, order='utilidades_name, write_date desc')
        for u in self.browse(util_id.id):
            days = u.utilidades_pay_days
        return days
