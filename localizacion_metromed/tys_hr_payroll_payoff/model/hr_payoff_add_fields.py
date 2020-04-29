# coding: utf-8
##############################################################################
#
# Copyright (c) 2016 Tecnología y Servicios AMN C.A. (http://tysamnca.com/) All Rights Reserved.
# <contacto@tysamnca.com>
# <Teléfono: +58(212) 237.77.53>
# Caracas, Venezuela.
#
# Colaborador: <<nombre colaborador>> <e-mail del colaborador>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from odoo import fields, models, api
from odoo.osv import osv
from odoo.exceptions import Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_payroll(models.Model):
    _inherit = "hr.payroll"

    ajuste_salarial_check = fields.Boolean('Ajuste Salarial')
    ajuste_salarial_value = fields.Float('Ajuste Salarial')
    prima_peligrosidad_check = fields.Boolean('Prima de peligrosidad')
    prima_peligrosidad_value = fields.Float('Prima de peligrosidad', defaults=0.0)
    prima_vivienda_check = fields.Boolean('Prima de vivienda')
    prima_vivienda_value = fields.Float('Prima de vivienda')
    prima_sitio_inhosp_check = fields.Boolean('Sitio Inhospito check')
    prima_sitio_inhosp_value = fields.Float('Sitio Inhospito Value')
    subsidio_familiar_check = fields.Boolean('Subsidio Familiar')
    subsidio_familiar_value = fields.Float('Subsidio Familiar')
    prima_antiguedad_check = fields.Boolean('Prima de antiguedad')
    prima_antiguedad_value = fields.Float('Prima de antiguedad')
    horas_extra_check = fields.Boolean('Horas extraordinarias')
    horas_extra_value = fields.Float('Horas extraordinarias')
    asignacion_gerente_check = fields.Boolean('Asignacion gerente')
    asignacion_gerente_value = fields.Float('Asignacion gerente')
    bono_nocturno_check = fields.Boolean('Bono nocturno')
    bono_nocturno_value = fields.Float('Bono nocturno')
    prom_benef_turno_check = fields.Boolean('Promedio beneficio de turno')
    prom_benef_turno_value = fields.Float('Promedio beneficio de turno')
    sutitu_temp_check = fields.Boolean('Clausula sustitutiva temporal')
    sutitu_temp_value = fields.Float('Clausula sustitutiva temporal')
    remuneracion_basica_value = fields.Float('Remuneracion Basica', digits=(10, 2))
    alic_bono_vac = fields.Float('Alicuota de bono vacacional', digits=(10, 2))
    alic_utilidades = fields.Float('Alicuota de utilidades', digits=(10, 2))
    salario_normal = fields.Float('Salario Normal', digits=(10, 2))
    salario = fields.Float('Salario', digits=(10, 2))
    december_work_days = fields.Integer('Dias habiles de diciembre')
    december_work_days_check = fields.Boolean('Dias habiles diciembre check')
    asignacion_complementaria_check = fields.Boolean('Asignacion complementaria')
    asignacion_complementaria_value = fields.Float('Asignacion complementaria')
    contract_id = fields.Many2one('hr.contract','Contratos')
    has_payoff = fields.Boolean('Tiene Liquidacion', defaults=False)

    _defaults = {
        'has_payoff': False,
        'prima_peligrosidad_value': 0.0,
    }

    def calculate_payoff_values(self, cr, uid, ids, date_start, date_end, employee_id=None, contract_id=None,
                                tiempo_servicio=None, vals=None, context=None):
        empolyee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        payslip_obj = self.pool.get('hr.payslip')
        salario_integral = salario_normal = salario =  sueldo_promedio = asignacion_complementaria = 0.0
        dias_habiles = days_to_pay = dias_adicionales = ut =  0
        vacation_reserva = ajuste_salarial = prima_peligrosidad = prima_vivienda = subsidio_familiar = 0.0
        prima_antiguedad = horas_extra = asignacion_gerente = bono_nocturno = prom_benef_turno = prima_sitio_ihosp = 0.0
        sutitu_temp = remuneracion_basica = alic_bono_vac = alic_utilidades = 0.0
        contract_record = None
        vacaciones = {}
        days = {}
        salario_normal = 0

        # defaults
        res = {
            'dias_habiles': dias_habiles,
            'days_to_pay': days_to_pay,
            'vacation_reserva': vacation_reserva,
            'salario_integral': salario_integral,
            'dias_adicionales': dias_adicionales,
            'tiempo_servicio': tiempo_servicio,
            'ut': ut,
            'ajuste_salarial_value': ajuste_salarial,
            'prima_peligrosidad': prima_peligrosidad,
            'prima_vivienda': prima_vivienda,
            'subsidio_familiar': subsidio_familiar,
            'prima_antiguedad': prima_antiguedad,
            'horas_extra': horas_extra,
            'asignacion_gerente': asignacion_gerente,
            'bono_nocturno_value': bono_nocturno,
            'prom_benef_turno_value': prom_benef_turno,
            'sutitu_temp': sutitu_temp,
            'remuneracion_basica': remuneracion_basica,
            'alic_bono_vac': alic_bono_vac,
            'alic_utilidades': alic_utilidades,
            'asignacion_complementaria': asignacion_complementaria,
            'prima_sitio_inhosp_value': prima_sitio_ihosp,
        }

        if context is None:
            context = {}

        # valida que existan los datos principales para el calculo de la liquidacion: empleado y periodo de trabajo
        if (not employee_id) and (not date_start) and (not date_end) and not tiempo_servicio:
            return res

        # Obtiene la informacion del contrato del empleado. Si no hay contratos termina
        if contract_id:
            # set the list of contract for which the input have to be filled
            contract_ids = [contract_id]
        else:
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_id.id)], None, None, context=context)
            #date_end = contract_obj.read(cr, uid, contract_ids, ['date_end'], context=context)['date_end']
        if not contract_ids:
            return res

        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        if not contract_record:
            return res

        days = self.days_to_pay(cr, uid, ids, date_end)
        vacaciones = self.calculate_vacation_bonus(cr, uid, ids, tiempo_servicio)
        sueldo_promedio = contract_record.wage
        salario_normal += sueldo_promedio
        ut = payslip_obj.get_amount_ut(cr, uid, date_end)
        dias_str = payslip_obj.get_hr_parameter(cr, uid, 'hr_dias_x_mes')
        for p in self.browse(cr, uid, [ids], context=context):
            if vals:
                if p.ajuste_salarial_check:
                    ajuste_salarial = vals.get('ajuste_salarial_value', p.ajuste_salarial_value)
                    salario_normal += ajuste_salarial
                if p.asignacion_gerente_check:
                    asignacion_gerente = vals.get('asignacion_gerente_value', p.asignacion_gerente_value)
                    salario_normal += asignacion_gerente
                if p.prom_benef_turno_check:
                    prom_benef_turno = vals.get('prom_benef_turno_value', p.prom_benef_turno_value)
                    salario_normal += prom_benef_turno
                if p.bono_nocturno_check:
                    bono_nocturno = vals.get('bono_nocturno_value', p.bono_nocturno_value)
                    salario_normal += bono_nocturno
                if p.sutitu_temp_check:
                    sutitu_temp = vals.get('sutitu_temp_value', p.sutitu_temp_value)
                    salario_normal += sutitu_temp
                if p.asignacion_complementaria_check:
                    asignacion_complementaria = vals.get('asignacion_complementaria_value', p.asignacion_complementaria_value)
                    salario_normal += asignacion_complementaria
                if p.prima_sitio_inhosp_check:
                    prima_sitio_ihosp = 5*ut
                    salario_normal += prima_sitio_ihosp
                if p.prima_peligrosidad_check:
                    if p.prima_peligrosidad_value:
                        prima_peligrosidad = p.prima_peligrosidad_value
                    else:
                        prima_peligrosidad = (sueldo_promedio/30.0)*(float(contract_record.peligrosidad)/100.0)*float(days)
        salario_normal += prima_peligrosidad
        prima_vivienda = ut * 1.48
        salario_normal += prima_vivienda
        subsidio_familiar = ut * 0.74 * contract_record.prima_por_hijo_100
        salario_normal += subsidio_familiar
        prima_antiguedad = ut * 0.5 * tiempo_servicio
        salario_normal += prima_antiguedad
        if contract_record.hrs_extra:
            horas_extra = contract_record.hrs_extra
            salario_normal += horas_extra
        alic_bono_vac = payslip_obj.calculo_alic_bono_vac(cr, uid, salario_normal, vacaciones.get('asignacion'))
        alic_utilidades = payslip_obj.calculo_alic_util(cr, uid, salario_normal, vacaciones.get('asignacion'), alic_bono_vac)
        salario = salario_normal + alic_bono_vac*int(dias_str)
        salario_integral = salario + alic_utilidades*int(dias_str)
        res.update({
            'dias_habiles': dias_habiles,
            'days_to_pay': days,
            'vacation_reserva': vacaciones.get('asignacionR'),
            'salario_integral': salario_integral,
            'salario_normal': salario_normal,
            'salario': salario,
            'dias_adicionales': contract_record.dias_adic_fideicomiso,
            'tiempo_servicio': tiempo_servicio,
            'ut': ut,
            'ajuste_salarial': ajuste_salarial,
            'asignacion_gerente': asignacion_gerente,
            'prom_benef_turno': prom_benef_turno,
            'prima_peligrosidad': prima_peligrosidad,
            'prima_vivienda': prima_vivienda,
            'subsidio_familiar': subsidio_familiar,
            'prima_antiguedad': prima_antiguedad,
            'horas_extra': horas_extra,
            'alic_bono_vac': alic_bono_vac*int(dias_str),
            'alic_utilidades' : alic_utilidades*int(dias_str),
            'bono_nocturno': bono_nocturno,
            'sutitu_temp': sutitu_temp,
            'remuneracion_basica': sueldo_promedio,
            'asignacion_complementaria': asignacion_complementaria,
            'prima_sitio_inhosp_value': prima_sitio_ihosp,
        })
        return res

    def onchange_date_end(self, cr, uid, ids, date_start, date_end):
        res = super(hr_payroll_liquidacion_obj, self).onchange_date_end(cr, uid, ids, date_start, date_end)
        values = {}
        if date_end:
            fecha = date_end.split('-')
            if int(fecha[1]) == 12:
                res['value'].update({'december_work_days_check': True})
        return  res

    def onchange_december_work_days(self, cr, uid, ids, dias):
        if not 1 <= dias <= 31:
            raise osv.except_osv(('Advertencia!'),('La cantidad de días hábiles debe estar entre 1 y 31!'))
        return True

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        res = {}
        contract_data = None
        has_payoff = False
        contract_obj = self.env['hr.contract']
        if self.contract_id:
            contract_data = contract_obj.read(self.contract_id, ['date_end', 'date_start'])
            res = {'value': {
                'date_to': contract_data.get('date_end', False) if contract_data else None,
                'date_from': contract_data['date_start'],
                }
            }
        return res

    def calculate_prima_peligrosidad(self, cr, uid, ids, date_end, wage, peligrosidad, dias_str, context=None):
        result = 0.0
        dia_x_mes = 1
        fecha = date_end.split('-')
        if fecha[1] != 12:
            dia_x_mes = self.lengthmonth(int(fecha[0]), int(fecha[1]))
        else:
            for p in self.browse(cr, uid, ids, context=context):
                if p.december_work_days_check:
                    dia_x_mes = p.december_work_days
                else:
                    dia_x_mes = self.lengthmonth(int(fecha[0]), int(fecha[1]))

        result = ((wage / int(dias_str)) * (peligrosidad / 100.00)) * dia_x_mes
        return result

    def create(self, cr, uid, vals, context=None):
        values = {}
        payoff_values = {}
        employee_obj = self.pool.get('hr.employee')
        new_id = super(hr_payroll_liquidacion_obj, self).create(cr, uid, vals, context)
        tiempo_servicio = vals.get('tiempo_servicio_year', False)
        date_start = vals.get('date_start', False)
        date_end = vals.get('date_end', False)
        employee_id = employee_obj.browse(cr, uid, vals.get('employee_id', False), context=context)
        if tiempo_servicio:
            payoff_values = self.calculate_payoff_values(cr, uid, new_id, date_start, date_end, employee_id, None,
                                                         tiempo_servicio, vals, context=context)
        if payoff_values:
            values.update({
                # 'tiempo_servicio': payoff_values['tiempo_servicio'] if payoff_values else 0,
                'ut': payoff_values['ut'],
                'days_to_pay': payoff_values['days_to_pay'],
                'salario_integral': payoff_values['salario_integral'],
                'salario': payoff_values['salario'],
                'salario_normal': payoff_values['salario_normal'],
                'vacation_reserva': payoff_values['vacation_reserva'],
                'ajuste_salarial_value': payoff_values['ajuste_salarial'],
                'asignacion_gerente_value': payoff_values['asignacion_gerente'],
                'prom_benef_turno_value': payoff_values['prom_benef_turno'],
                'prima_peligrosidad_value': payoff_values['prima_peligrosidad'],
                'prima_vivienda_value': payoff_values['prima_vivienda'],
                'subsidio_familiar_value': payoff_values['subsidio_familiar'],
                'prima_antiguedad_value': payoff_values['prima_antiguedad'],
                'horas_extra_value': payoff_values['horas_extra'],
                'alic_bono_vac': payoff_values['alic_bono_vac'],
                'alic_utilidades': payoff_values['alic_utilidades'],
                'bono_nocturno_value': payoff_values['bono_nocturno'],
                'sutitu_temp_value': payoff_values['sutitu_temp'],
                'remuneracion_basica_value': payoff_values['remuneracion_basica'],
                'asignacion_complementaria_value': payoff_values['asignacion_complementaria'],
                'prima_sitio_inhosp_value': payoff_values['prima_sitio_inhosp_value'],
            })
        self.write(cr, uid, new_id, values, context=context)
        return new_id

    def write(self, cr, uid, ids, values, context=None):
        if context is None: context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]
        code = ''
        payoff_values = {}
        state = values.get('state', False)
        tiempo_servicio = values.get('tiempo_servicio_year', False)
        date_end = values.get('date_end', False)
        if state and state == 'verify':
            for liq in self.browse(cr, uid, ids, context=context):
                payoff_values = self.calculate_payoff_values(cr, uid, ids[0], liq.date_start,
                            date_end if date_end else liq.date_end, liq.employee_id,None,
                            tiempo_servicio if tiempo_servicio else liq.tiempo_servicio_year, values, context)
            if payoff_values:
                values.update({
                # 'tiempo_servicio': payoff_values['tiempo_servicio'] if payoff_values else 0,
                'ut': payoff_values['ut'],
                'days_to_pay': payoff_values['days_to_pay'],
                'salario_integral': payoff_values['salario_integral'],
                'salario': payoff_values['salario'],
                'salario_normal': payoff_values['salario_normal'],
                'vacation_reserva': payoff_values['vacation_reserva'],
                'ajuste_salarial_value': payoff_values['ajuste_salarial'],
                'asignacion_gerente_value': payoff_values['asignacion_gerente'],
                'prom_benef_turno_value': payoff_values['prom_benef_turno'],
                'prima_peligrosidad_value': payoff_values['prima_peligrosidad'],
                'prima_vivienda_value': payoff_values['prima_vivienda'],
                'subsidio_familiar_value': payoff_values['subsidio_familiar'],
                'prima_antiguedad_value': payoff_values['prima_antiguedad'],
                'horas_extra_value': payoff_values['horas_extra'],
                'alic_bono_vac': payoff_values['alic_bono_vac'],
                'alic_utilidades': payoff_values['alic_utilidades'],
                'bono_nocturno_value': payoff_values['bono_nocturno'],
                'sutitu_temp_value': payoff_values['sutitu_temp'],
                'remuneracion_basica_value': payoff_values['remuneracion_basica'],
                'asignacion_complementaria_value': payoff_values['asignacion_complementaria'],
                'prima_sitio_inhosp_value': payoff_values['prima_sitio_inhosp_value'],
                })
        res = super(hr_payroll_liquidacion_obj, self).write(cr, uid, ids, values, context)
        return res

    def hr_action_confirm(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get('hr.contract')
        for liq in self.browse(cr, uid, ids, context=context):
            contract_id = liq.contract_id
            if contract_id:
                contract_obj.write(cr, uid, ids, {'has_payoff': True}, context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

class hr_contract(models.Model):
    _inherit = "hr.contract"

    has_payoff = fields.Boolean('Tiene Liquidacion', defaults=False)
