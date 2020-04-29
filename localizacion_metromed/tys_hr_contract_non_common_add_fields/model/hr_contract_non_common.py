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
#    Change: jeduardo **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#import num2cad
import re

class hr_contract(models.Model):

    _inherit = "hr.contract"
    #funciom monto en letra
   # @api.multi
   # @api.depends('wage')
   # def _conver_mont(self):
     #   for i in self:
    #        if i.wage:
  #              monto = str(i.wage)
   #             cadena = num2cad.EnLetras(monto)
    #            letra = cadena.escribir
     #           i.wage_Letter = letra
    #        else:
   #             i.wage_Letter = False
    #ASIGNACIONES - CHECK BOXES
    ajust_util_check = fields.Boolean('Activar ajust_util_check')
    ajust_tickets_check = fields.Boolean('Activar ajust_tickets_check')
    ajust_fide_check = fields.Boolean('Activar ajust_fide_check')
    bon_esp_check = fields.Boolean('Activar bon_esp_check')
    dias_pen_disfr_check = fields.Boolean('Activar dias_pen_disfr_check')
    trans_alim_pasantes_check = fields.Boolean('Activar trans_alim_pasantes_check')
    bon_proc_check = fields.Boolean('Activar bon_proc_check')
    ant_utils_check = fields.Boolean('Activar ant_utils_check')
    ant_prest_check = fields.Boolean('Activar ant_prest_check')
    reint_desc_ind_check = fields.Boolean('Activar reint_desc_ind_check')
    reint_gast_varios_embargo_check = fields.Boolean('Activar reint_gast_varios_embargo_check')
    ant_vacaciones_check = fields.Boolean('Activar ant_vacaciones_check')
    desc_horas_check = fields.Boolean('Activar desc_horas_check')
    reint_medicos_check = fields.Boolean('Activar reint_medicos_check')
    adicional_zona_check = fields.Boolean('Activar adicional_zona_check')
    examen_pre_post_vac_check = fields.Boolean('Activar examen_pre_post_vac_check')
    accdte_prof_check = fields.Boolean('Activar accdte_prof_check')
    n_accdte_prof_check = fields.Boolean('Activar n_accdte_prof_check')
    pre_post_vacacional_check = fields.Boolean('Activar pre_post_vacacional_check')
    reposo_100_check = fields.Boolean('Activar reposo_100_check')
    reposo_33_check = fields.Boolean('Activar reposo_33_check')
    perm_nac_examen_check = fields.Boolean('Activar perm_nac_examen_check')
    reposo_pre_post_check = fields.Boolean('Activar reposo_pre_post_check')

    anticipo_salario_check = fields.Boolean('Activar anticipo_salario_check')
    comisiones_check = fields.Boolean('Activar comisiones ')
    anticipo_comisiones_check = fields.Boolean('Activar anticipo de comisiones')
    retroactivo_salario_check = fields.Boolean('Activar retroactivo_salario  ')
    reintegro_inasis_desct_check = fields.Boolean('Activar reintegro_inasis_desct')
    reintegro_desc_indebido_check = fields.Boolean('Activar reintegro_desc_indebido')
    reintegro_desc_uniforme_check = fields.Boolean('Activar reintegro_desc_uniforme  ')
    anticipo_prest_soc_check = fields.Boolean('Activar anticipo_prest_soc  ')
    complemento_comision_mes_check = fields.Boolean('Activar complemento_comision_mes')
    asig_especiales_check = fields.Boolean('Activar asig_especiales')
    asig_otros_check = fields.Boolean('Activar asig_otros  ')
    bono_produccion_check = fields.Boolean('Activar bono_produccion')
    dias_faltantes_ticket_check = fields.Boolean('Activar dias_faltantes_ticket')
    ayuda_escolar_check = fields.Boolean('Activar ayuda_escolar')
    clausula_minima_check = fields.Boolean('Activar clausula_minima')

    bono_nocturno_mes_ant_check = fields.Boolean('Activar bono nocturno mes anterior')
    salario_bono_nocturno_mes_ant = fields.Many2one('salary.increase.line','Salario mes anterior')
    #salario_bono_nocturno_mes_ant_usado = fields.Float(invisible=True)
    domingos_laborados_check = fields.Boolean('Activar domingos laborados')
    domingos_laborados_mes_ant_check = fields.Boolean('Activar domingos laborados mes anterior')
    salario_domingos_laborados_mes_ant = fields.Many2one('salary.increase.line', 'Salario mes anterior')
    #salario_domingos_laborados_mes_ant_usado = fields.Float(invisible=True)
    feriado_laborado_mes_ant_check = fields.Boolean('Activar feriado laborado mes anterior')
    salario_feriado_laborado_mes_ant = fields.Many2one('salary.increase.line', 'Salario mes anterior')
    days_of_salary_pending_mes_anterior_check = fields.Boolean('Activar Reintegro de dias mes anterior')
    reintegro_dias_mes_ant = fields.Many2one('salary.increase.line', 'Salario mes anterior')


    #salario_feriado_laborado_mes_ant_usado = fields.Float(invisible=True)



    #ASIGNACIONES - CAMPOS
    reposo_33_value = fields.Integer('Reposo 33%', size=3)
    reposo_100_value = fields.Integer('Reposo 100%', size=3)
    reposo_pre_post_value = fields.Integer('Reposo pre/post', size=3)
    perm_nac_examen_value = fields.Integer('Permiso de nacimiento o examen', size=3)
    pre_post_vacacional_value = fields.Integer('Pre/post Vacacional', size=3)
    consultas_medicas_value = fields.Integer('Consultas medicas', size=3)
    accdete_prof_value = fields.Integer('Accidente profesional', size=3)
    n_accdete_prof_value = fields.Integer('accidente no profesional', size=3)
    per_nac_value = fields.Integer('Permiso de nacimiento', size=3)
    examen_pre_post_vac_value = fields.Integer('Examen Pre/Post vacacional', size=3)
    adicional_zona_value = fields.Float('Adicional por Zona', size=10)
    ajust_util_value = fields.Float('Ajustes de utilidades', size=10)
    ajust_tickets_value= fields.Float('Ajuste de cesta tickets', size=10)
    ajust_fide_value= fields.Float('Ajustes de fideicomiso', size=10)
    bon_esp_value= fields.Float('Bonificacions especiales', size=10)
    dias_pen_disfr_value= fields.Integer('Dias pendientes por disfrutar', size=3)
    trans_alim_pasantes_value= fields.Float('Tranporte/alimentacion de pasantes', size=10)
    bon_proc_value= fields.Float('Bono de produccion', size=10)
    ant_utils_value= fields.Float('Anticipo de utilidades', size=10)
    ant_prest_value= fields.Float('Anticipo de prestaciones', size=10)
    reint_desc_ind_value= fields.Float('Reintegro de descuesto indebido', size=10)
    reint_gast_varios_embargo_value= fields.Float('Reintegro de gastos varios por embargo', size=10)
    ant_vacaciones_value= fields.Float('Anticipo de vacaciones', size=10)
    desc_horas_value= fields.Float('Descuento de horas no trabajadas', size=10)
    reint_medicos_value= fields.Float('Reintegro de gastos medicos', size=10)
    inasistencia_injustificada_motivo = fields.Char('Motivo', size=100)

    anticipo_salario_value = fields.Float('Anticipo de Salario')
    comisiones_value = fields.Float('Comisiones')
    anticipo_comisiones_value = fields.Float('Anticipo de Comisiones')
    retroactivo_salario_value = fields.Float('Retroactivo de Salario')
    reintegro_inasis_desct_value = fields.Float('Reintegro por Inasistencia Descontada')
    reintegro_desc_indebido_value = fields.Float('Reintegro por Descuento Indebido')
    reintegro_desc_uniforme_value = fields.Float('Reintegro Descuento Uniformes')
    anticipo_prest_soc_value = fields.Float('Anticipo sobre Prestaciones Sociales')
    complemento_comision_mes_value = fields.Float('Complemento Comisiones Mes')
    asig_especiales_value = fields.Float('Asignaciones Especiales')
    asig_otros_value = fields.Float('Otras Asignaciones')
    bono_produccion_value = fields.Float('Bono Por Produccion')
    dias_faltantes_ticket_value = fields.Integer('Dias Faltantes Cestatickets')
    ayuda_escolar_value =fields.Float('Ayuda Escolar')
    clausula_minima_value = fields.Float('Clausula Minima')
    # TODO EVALUAR SI ESTOS CAMPOS REQUIEREN VALOR
    bono_nocturno_mes_ant_value = fields.Integer('Bono Nocturno Mes Anterior int_value')
    domingos_laborados_value = fields.Integer('Domingos Laborados int_value')
    domingos_laborados_mes_ant_value = fields.Integer('Domingos Laborados Mes Anterior int_valua')
    feriado_laborado_mes_ant_value = fields.Integer('Feriado Laborado Mes Anterior int_value')
    bono_nocturno_int_value = fields.Integer('Bono Nocturno int_value')
    days_of_salary_pending_mes_anterior_value = fields.Integer('Reintegro de dias mes anterior int_value')

    #DEDUCCIONES - CHECKBOXES
    prestamo_check = fields.Boolean('Activar prestamo_check')
    cuota_check = fields.Boolean('Activar cuota_check')
    desc_ind_salary_check = fields.Boolean('Activar desc_ind_salary_check')

    dcto_copias_check= fields.Boolean('Activar dcto_copias')
    dcto_llamadas_check= fields.Boolean('Activar dcto_llamadas')
    trimestre_vehiculo_check= fields.Boolean('Activar trimestre_vehiculo')
    dcto_pago_factura_check= fields.Boolean('Activar dcto_pago_factura')
    dcto_pago_comision_check= fields.Boolean('Activar dcto_pago_comision')
    dcto_poliza_hc_check= fields.Boolean('Activar dcto_poliza_hc')
    dcto_ant_gtos_moto_check= fields.Boolean('Activar dcto_ant_gtos_moto')
    dcto_poliza_vehiculo_check= fields.Boolean('Activar dcto_poliza_vehiculo')
    dcto_comision_dev_merc_check= fields.Boolean('Activar dcto_comision_dev_merc')
    dcto_vale_caja_chica_check= fields.Boolean('Activar dcto_vale_caja_chica')
    dcto_reposicion_carnet_check= fields.Boolean('Activar dcto_reposicion_carnet')
    dcto_pago_vehiculo_check= fields.Boolean('Activar dcto_pago_vehiculo')
    otras_deducciones_check= fields.Boolean('Activar otras_deducciones')

    dcto_sso_check = fields.Boolean('Activar dcto SSO')
    dcto_reg_prest_empleo_check = fields.Boolean('Activar dtco regimen prestacional de empleo')
    #dcto_fideicomiso_check = fields.Boolean('Activar dcto fideicomiso')
    dcto_cestaticket_check = fields.Boolean('Activar dcto cestaticket')
    ausencias_ded_mes_ant_check = fields.Boolean('activar ausencias injustificadas mes anterior')
    ausencias_ded_mes_ant = fields.Many2one('salary.increase.line', 'Salario mes anterior')

    #DEDUCCIONES - CAMPOS
    prestamo_value = fields.Float('Prestamo', size=10)
    cuota_value = fields.Float('Cuota', size=10)
    desc_ind_salary_value = fields.Float('Descuento indebido del salario', size=10)

    dcto_copias_value = fields.Float('Activar dcto_copias')
    dcto_llamadas_value = fields.Float('Activar dcto_llamadas')
    trimestre_vehiculo_value = fields.Float('Activar trimestre_vehiculo')
    dcto_pago_factura_value = fields.Float('Activar dcto_pago_factura')
    dcto_pago_comision_value = fields.Float('Activar dcto_pago_comision')
    dcto_poliza_hc_value = fields.Float('Activar dcto_poliza_hc')
    dcto_ant_gtos_moto_value = fields.Float('Activar dcto_ant_gtos_moto')
    dcto_poliza_vehiculo_value = fields.Float('Activar dcto_poliza_vehiculo')
    dcto_comision_dev_merc_value = fields.Float('Activar dcto_comision_dev_merc')
    dcto_vale_caja_chica_value = fields.Float('Activar dcto_vale_caja_chica')
    dcto_reposicion_carnet_value = fields.Float('Activar dcto_reposicion_carnet')
    dcto_pago_vehiculo_value = fields.Float('Activar dcto_pago_vehiculo')
    otras_deducciones_value = fields.Float('Activar otras_deducciones')
    # dcto_sso_value = fields.Boolean('Activar dcto SSO')
    # dcto_reg_prest_empleo_value = fields.Boolean('Activar dtco regimen prestacional de empleo')
    # dcto_fideicomiso_value = fields.Boolean('Activar dcto fideicomiso')
    dcto_cestaticket_value = fields.Integer('Activar dcto cestaticket value')


    #NUEVOS CAMPOS QUE CAMBIAN LOS CAMPOS TIPO CHAR POR FLOAT
    bono_nocturno_float_value = fields.Float('Bono Nocturno float_value')
    hrs_no_lab_float_value = fields.Float('Horas no Laboradas float_value')
    inasistencia_injustificada_float_value = fields.Float('Inasistencia Injustificada float_value')
    permiso_no_remunerado_dias_float_value = fields.Float('Permiso No Remunerado Dias float_value')
    permiso_no_remunerado_hrs_float_value = fields.Float('Permiso No Remunerado Hrs float_value')
   # wage_Letter = fields.Char(string='Salario en letra', compute='_conver_mont', store='True')
    ausencias_ded_mes_ant_value = fields.Integer('Ausencias Injustificadas mes anterior')


    # SALRIO MES ANTERIOR
    last_month_wage = fields.Float('Salrio Mes Anterior')
    salary_increase_line_ids = fields.Many2one('salary.increase.line','Linea de aumento salarial', readonly=True)

    @api.multi
    def _validate_value_digits(self, values):
        lista = ['domingos_laborados_mes_ant_value', 'feriado_laborado_mes_ant_value', 'days_of_salary_pending_mes_anterior_value',
                 'ausencias_ded_mes_ant_value']
        if values:
            for b in values:
                for c in lista:
                    if c == b:
                        # for a in values.get(c):
                        if values.get(c) > 30:
                            raise ValidationError(_(u'Solo admite hasta 30 Días. Por favor intente de nuevo'))
        return

    @api.multi
    def _validate_value_nigth_bonus_value(self, values):
        if self.bono_nocturno_mes_ant_check:
            valid_value = True
        else:
            valid_value = False
        bono_nocturno_mes_ant_value = values.get('bono_nocturno_mes_ant_value', False)
        if bono_nocturno_mes_ant_value or valid_value:
            if bono_nocturno_mes_ant_value > 7:
                raise ValidationError(_(u'Solo admite hasta 7 Días. Por favor intente de nuevo'))
            return

    @api.multi
    def write(self, values):
        self._validate_value_digits(values)
        self._validate_value_nigth_bonus_value(values)
        res = super(hr_contract, self).write(values)
        return res


    @api.model
    def create(self, values):
        self._validate_value_digits(values)
        self._validate_value_nigth_bonus_value(values)
        res = super(hr_contract, self).create(values)
        return res

    def validate_changed_fields(self, values, come_from):
        validar_value = False

        # PERMISO NO REMUNERADO
        permiso_no_remunerado_hrs_check = values.get('permiso_no_remunerado_hrs_check', False)
        if permiso_no_remunerado_hrs_check:
            validar_value = True
        else:
            validar_value = False
        permiso_no_remunerado_hrs_float_value = values.get('permiso_no_remunerado_hrs_float_value', False)
        if permiso_no_remunerado_hrs_float_value or validar_value:
            self._onchange_hours(None, permiso_no_remunerado_hrs_float_value, 'permiso_no_remunerado_hrs_float_value',
                                come_from)
        return True

    @api.multi
    def get_comisiones_value(self, employee_id):
        #print "amployee_id = " + employee_id
        contract = self.env['hr.contract'].browse(employee_id)
        return contract.comisiones_value

    @api.onchange('wage')
    def salario_a_utilizar_default(self):
        if self.wage:
            if not self.salario_bono_nocturno_mes_ant:
                self.last_month_wage = self.wage
            if not self.salario_domingos_laborados_mes_ant:
                self.last_month_wage = self.wage
            if not self.salario_feriado_laborado_mes_ant:
                self.last_month_wage = self.wage
            if not self.reintegro_dias_mes_ant:
                self.last_month_wage = self.wage


    @api.onchange('salario_bono_nocturno_mes_ant','salario_domingos_laborados_mes_ant','salario_feriado_laborado_mes_ant','reintegro_dias_mes_ant')
    def salario_a_utitlizar(self):
        if self.salario_bono_nocturno_mes_ant:
            self.last_month_wage = self.salario_bono_nocturno_mes_ant.past_amount
        else:
            self.last_month_wage = self.wage
        if self.salario_domingos_laborados_mes_ant:
            self.last_month_wage = self.salario_domingos_laborados_mes_ant.past_amount
        else:
            self.last_month_wage = self.wage
        if self.salario_feriado_laborado_mes_ant:
            self.last_month_wage = self.salario_feriado_laborado_mes_ant.past_amount
        else:
            self.last_month_wage = self.wage
        if self.reintegro_dias_mes_ant:
            self.last_month_wage = self.reintegro_dias_mes_ant.past_amount
        else:
            self.last_month_wage = self.wage


class salary_line(models.Model):
    _inherit = 'salary.increase.line'

    def name_get(self):
      #  if self._context is None:
       #     context = {}
        res = []
        sil_obj = self.env['salary.increase.line']
        emp_id = self.employee_id.id
        salaries = sil_obj.search([('employee_id','=',emp_id)])
        for salary in salaries:
            res.append((salary.id, str(salary.past_amount) + ' < ' + salary.fecha_increase))
        return res

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def hr_verify_sheet(self):
        res = super(hr_payslip, self).hr_verify_sheet()
        if self.env.context.get('come_from') and 'payoff' in self.env.context.get('come_from'):
            return res
        new_values ={
            'reposo_33_value' : 0,
            'reposo_100_value': 0,
            'reposo_pre_post_value ': 0,
            'perm_nac_examen_value' :0,
            'pre_post_vacacional_value' : 0,
            'consultas_medicas_value' :0,
            'accdete_prof_value' :0,
            'n_accdete_prof_value' :0,
            'per_nac_value' : 0,
            'examen_pre_post_vac_value': 0,
            'adicional_zona_value' : 0,
            'prestamo_value' :0,
            'cuota_value' : 0,
            'desc_ind_salary_value':0,
            'ajust_util_value': 0,
            'ajust_tickets_value' :0,
            'ajust_fide_value' :0,
            'bon_esp_value':0,
            'dias_pen_disfr_value': 0,
            'trans_alim_pasantes_value':0,
            'bon_proc_value': 0,
            'ant_utils_value': 0,
            'ant_prest_value': 0,
            'reint_desc_ind_value': 0,
            'reint_gast_varios_embargo_value':0,
            'ant_vacaciones_value' :0,
            'desc_horas_value' : 0,
            'reint_medicos_value': 0,
            'ausencias_ded_mes_ant_value': 0,
            'bono_nocturno_mes_ant_value': 0,
            'days_of_salary_pending_mes_anterior_value':0,
            'domingos_laborados_mes_ant_value': 0,
            'feriado_laborado_mes_ant_value':0,
            'inasistencia_injustificada_motivo' : '\'\'',}

        new_values.update({i: False for i in ['prestamo_check', 'cuota_check', 'desc_ind_salary_check', 'ajust_util_check', \
                             'ajust_tickets_check', 'ajust_fide_check', 'bon_esp_check', 'dias_pen_disfr_check',\
                             'trans_alim_pasantes_check', 'bon_proc_check', 'ant_utils_check', 'ant_prest_check',\
                             'reint_desc_ind_check', 'reint_gast_varios_embargo_check', 'ant_vacaciones_check',\
                             'desc_horas_check', 'reint_medicos_check', 'adicional_zona_check',\
                             'examen_pre_post_vac_check', 'accdte_prof_check', 'n_accdte_prof_check',\
                             'pre_post_vacacional_check', 'reposo_100_check', 'reposo_33_check', 'perm_nac_examen_check',\
                             'reposo_pre_post_check', 'ausencias_ded_mes_ant_check','bono_nocturno_mes_ant_check', 'days_of_salary_pending_mes_anterior_check', 'feriado_laborado_mes_ant_check']})
        # AGREGANDO ASIGNACIONES
        new_values.update({i: False for i in
                           ['anticipo_salario_check', 'comisiones_check','anticipo_comisiones_check','retroactivo_salario_check',
                           'reintegro_inasis_desct_check', 'reintegro_desc_indebido_check', 'reintegro_desc_uniforme_check',
                           'anticipo_prest_soc_check', 'complemento_comision_mes_check',
                           'asig_especiales_check', 'asig_otros_check', 'bono_produccion_check','dias_faltantes_ticket_check','ayuda_escolar_check','clausula_minima_check']})
        new_values.update({i: 0.0 for i in
                         ['anticipo_salario_value', 'comisiones_value', 'anticipo_comisiones_value', 'retroactivo_salario_value',
                          'reintegro_inasis_desct_value', 'reintegro_desc_indebido_value', 'reintegro_desc_uniforme_value',
                          'anticipo_prest_soc_value', 'complemento_comision_mes_value',
                          'asig_especiales_value', 'asig_otros_value', 'bono_produccion_value','ayuda_escolar_value','clausula_minima_value']})
        new_values.update({'dias_faltantes_ticket_value':0})
        # AGREGANDO DEDUCCIONES
        new_values.update({i: False for i in
                           ['dcto_copias_check','dcto_llamadas_check','trimestre_vehiculo_check','dcto_pago_factura_check',
                            'dcto_pago_comision_check','dcto_poliza_hc_check','dcto_ant_gtos_moto_check','dcto_poliza_vehiculo_check',
                            'dcto_comision_dev_merc_check','dcto_vale_caja_chica_check','dcto_reposicion_carnet_check',
                            'dcto_pago_vehiculo_check','otras_deducciones_check']})
        new_values.update({i: 0.0 for i in
                           ['dcto_copias_value', 'dcto_llamadas_value', 'trimestre_vehiculo_value',
                            'dcto_pago_factura_value','dcto_pago_comision_value', 'dcto_poliza_hc_value', 'dcto_ant_gtos_moto_value',
                            'dcto_poliza_vehiculo_value','dcto_comision_dev_merc_value', 'dcto_vale_caja_chica_value',
                            'dcto_reposicion_carnet_value','dcto_pago_vehiculo_value', 'otras_deducciones_value']})

        new_values.update({i: 0.0 for i in
                           ['bono_nocturno_float_value','hrs_no_lab_float_value','inasistencia_injustificada_float_value',
                            'permiso_no_remunerado_dias_float_value','permiso_no_remunerado_hrs_float_value', 'hours_not_worked_mes_ant_value']})

        # self.contract_id.write(new_values)
        sql_update_clause = 'update hr_contract set'
        sql_where_clause = ' where id in %s'
        sql_middle_cluase = ''
        sql_string = ''
        for clave, valor in new_values.items():
            sql_middle_cluase = sql_middle_cluase + clave + '=' + str(valor) + ', '
        payslip_id = self.ids
        payslip = self.browse(payslip_id)
        contract_id = payslip.contract_id.id
        sql_middle_cluase= sql_middle_cluase[:-2]
        sql_string = sql_update_clause + sql_middle_cluase + sql_where_clause
        self.env.cr.execute(sql_string, (tuple([contract_id]),))
        return res

    @api.multi
    def compute_sheet(self):


        slip_line_env = self.env['hr.payslip.line']
        sequence_obj = self.env['ir.sequence']

        for payslip in self.browse(self._ids):
            number = payslip.number or sequence_obj.get('salary.slip')
            # delete old payslip lines
            old_slipline_ids = slip_line_env.search([('slip_id', '=', payslip.id)])
            #            old_slipline_ids
            if old_slipline_ids:
                for i in old_slipline_ids:
                    slip_line_env.search([('id','=',i.id)]).unlink()
                #slip_line_env.unlink(self._cr, self._uid, old_slipline_ids, context=self._context)
            if payslip.contract_id:
                # set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to,
                                                 )
            lines = []
            for line in self.env['hr.payslip']._get_payslip_lines(contract_ids, payslip.id):
                if 'code' in line:
                    apply_code = self.env['hr.config.parameter'].search([('value','=',line.get('code'))])
                    if apply_code.key == 'tys.hr.payroll.apply.nocturnal':
                        if payslip.contract_id.bono_nocturno_check == True:
                            line['quantity'] = payslip.contract_id.bono_nocturno_int_value
                            lines.append((1, 1, line))
                    elif apply_code.key == 'tys.hr.payroll.apply.nocturnal.before':
                        if payslip.contract_id.bono_nocturno_mes_ant_check == True:
                            line['quantity'] = payslip.contract_id.bono_nocturno_mes_ant_value
                            lines.append((1, 1, line))
                    elif apply_code.key == 'tys.hr.payroll.apply.holiday':
                        if payslip.contract_id.feriados_check == True:
                            line['quantity'] = payslip.contract_id.feriados_value
                            lines.append((1, 1, line))
                    elif apply_code.key == 'tys.hr.payroll.apply.holiday.before':
                        if payslip.contract_id.feriado_laborado_mes_ant_check == True:
                            line['quantity'] = payslip.contract_id.feriado_laborado_mes_ant_value
                            lines.append((1, 1, line))
                    elif apply_code.key == 'tys.hr.payroll.apply.sunday':
                        if payslip.contract_id.domingos_laborados_check == True:
                            line['quantity'] = payslip.contract_id.domingos_laborados_value
                            lines.append((1, 1, line))
                    elif apply_code.key == 'tys.hr.payroll.apply.sunday.before':
                        if payslip.contract_id.domingos_laborados_mes_ant_check == True:
                            line['quantity'] = payslip.contract_id.domingos_laborados_mes_ant_value
                            lines.append((1, 1, line))
                lines.append((0, 0, line))
            payslip.write({'line_ids': lines, 'number': number, })
        return super(hr_payslip, self).compute_sheet()

