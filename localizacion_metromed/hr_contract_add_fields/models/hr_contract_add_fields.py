# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import re
from odoo import api, fields, models, _ , exceptions
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _name = 'hr.contract'
    _inherit = ["hr.contract"]

    #ASIGNACIONES
    night_bonus_check = fields.Boolean(string='Night Bonus')
    night_bonus_value = fields.Integer(string='Night Bonus Value')
    #night_bonus = fields.Float(string='Night Bonus', digits=(10,2))
    days_of_salary_pending_check = fields.Boolean(string='Days of Salary Pending')
    days_of_salary_pending_value = fields.Integer('Days of Salary Pending Value', size=2)
    sundays_check = fields.Boolean(string='Sundays')
    sundays_value = fields.Integer(string='Sunday value')
    holidays_check = fields.Boolean(string='Holidays')
    holidays_value = fields.Integer('Holidays Value')
    holiday_not_worked_check = fields.Boolean(string='Holiday not Worked')
    holiday_not_worked_value = fields.Integer(string='Holiday not Worked Value', size=2)
    diurnal_extra_hours_check = fields.Boolean(string='Diurnal Extra Hours')
    diurnal_extra_hours_value = fields.Char(string='Diurnal Extra Hours Value', size=5, help="Accepts values between 00:00 and 23:59")
    diurnal_extra_hours = fields.Float(string='Diurnal Extra Hours',digits=(10,2), store=True)
    salary_retroactive_check = fields.Boolean(string='Salary Retroactive')
    salary_retroactive_value = fields.Float(string='Salary Retroactive Value', digits=(10,2))
    salary_assignment_check = fields.Boolean(string='Salary Assignment')
    salary_assignment_value = fields.Integer(string='Salary Assignment Value')
    non_salary_assignation_check = fields.Boolean(string='Non-Salary Assignation')
    non_salary_assignation_value = fields.Float(string='Non-Salary Assignation Value', digits=(10,2))
    # DEDUCCIONES
    hours_not_worked_check = fields.Boolean(string='Hours not Worked')
    hours_not_worked_value = fields.Char(string='Hours not Worked Value', size=5, help="Accepts values between 00:00 and 23:59")
    hours_not_worked = fields.Float('Hours not Worked', digits=(10, 2))
    hours_not_worked_mes_ant_check = fields.Boolean(string='Hours not Worked')
    hours_not_worked_mes_ant_value = fields.Char(string='Hours not Worked Value', size=5,
                                         help="Accepts values between 00:00 and 23:59")
    hours_not_worked_mes_ant = fields.Float('Hours not Worked', digits=(10, 2))
    salario_hours_not_worked_mes_ant = fields.Many2one('salary.increase.line', 'Salario mes anterior')
    unexcused_absences_check = fields.Boolean(string='Unexcused Absences')
    #unexcused_absences_value = fields.Char(string='Unexcused Absences Value', size=5, help="Accepts values between 00:00 and 23:59")
    unexcused_absences_value = fields.Integer(string='Unexcused Absences', size=2)
    unpaid_permit_days_check = fields.Boolean(string='Unpaid Permit Days')
    unpaid_permit_days_value = fields.Integer(string='Unpaid Permit Value Days', size=2)
    unpaid_permit_hours_check = fields.Boolean(string='Unpaid Permit Hours')
    unpaid_permit_hours_value = fields.Char(string='Unpaid Permit Hours Value', size=5, help="Accepts values between 00:00 and 23:59")
    unpaid_permit_hours = fields.Float(string='Unpaid Permit Hours', digits=(10, 2))
    faov_withholding_check = fields.Boolean(string='F.A.O.V. Withholding')
    saving_fund_withholding_check = fields.Boolean(string='Saving Fund Withholding')
    islr_withholding_check = fields.Boolean(string='I.S.L.R. Withholding')
    islr_withholding_value = fields.Float(string='I.S.L.R. Withholding Value', digits=(2,2))
    # 'retencion_pie_check = fields.Boolean('Retencion P.I.E.')non_salary_deduction_value
    # 'retencion_sso_check = fields.Boolean('Retencion S.S.O.')
    salary_deduction_check = fields.Boolean(string='Salary Deduction')
    salary_deduction_value = fields.Float(string='Salary Deduction Value', digits=(10, 2))
    non_salary_deduction_check = fields.Boolean(string='Non-Salary Deduction')
    non_salary_deduction_value = fields.Integer(string='Non-Salary Deduction Value')
    deduction_bono_vac_check = fields.Boolean(string='Deduction Bono Vacacional')
    deduction_bono_vac_value = fields.Integer(string='Deduction Bono Vacacional value')
    ausencias_ded_check= fields.Boolean(string='Cantidad de dias de Ausencias check')
    ausencias_ded_value = fields.Integer(string='Cantidad de dias de Ausencias value')
    dcto_sso_check = fields.Boolean('Activar dcto SSO')
    dcto_reg_prest_empleo_check = fields.Boolean('Activar dtco regimen prestacional de empleo')
    retencion_faov_check = fields.Boolean('Retencion FAOV')
    subsidio_patria_check = fields.Boolean('Subsidio Patria')
    subsidio_patria_value = fields.Float(string='Subsidio Patria Value')
    retroactivo_check = fields.Boolean('Retroactivo')
    retroactivo_value = fields.Float(string='Retroactivo')
    prestamo_check = fields.Boolean('Prestamo')
    prestamo_value = fields.Float(string='Prestamo')

    # @api.onchange('sundays_value','holidays_value','night_bonus_value','days_of_salary_pending_value','salary_assignment_value','non_salary_deduction_value','deduction_bono_vac_value')
    @api.multi
    def _validate_value_digits(self, values):
        lista = ['sundays_value', 'holidays_value', 'days_of_salary_pending_value',
                 'salary_assignment_value', 'non_salary_deduction_value', 'deduction_bono_vac_value','ausencias_ded_value']
        if values:
            for b in values:
                for c in lista:
                    if c == b:
                        #for a in values.get(c):
                        if values.get(c) > 30:
                            raise ValidationError(_(u'Solo admite hasta 30 Días. Por favor intente de nuevo'))
        return

    @api.multi
    def _validate_value_nigth_bonus_value(self, values):
        if self.night_bonus_check:
            valid_value = True
        else:
            valid_value = False
        night_bonus_value = values.get('night_bonus_value', False)
        if night_bonus_value or valid_value:
            if night_bonus_value > 7:
                raise ValidationError(_(u'Solo admite hasta 7 Días. Por favor intente de nuevo'))
            return


    @api.multi
    def write(self, values):
        self._validate_changed_fields(values, 'write')
        self._validate_value_digits(values)
        self._validate_value_nigth_bonus_value(values)
        res = super(Contract, self).write(values)
        return res

    #def write(self, cr, uid, ids, values, context=None):
    #    if context is None: context = {}
    #    if not hasattr(ids, '__iter__'): ids = [ids]
    #    self.validate_changed_fields(cr, uid, ids, values, 'write', context)
    #    res = super(hr_contract, self).write(cr, uid, ids, values, context)
    #    return res

    @api.model
    def create(self, values):
        self._validate_changed_fields(values, 'create')
        self._validate_value_digits(values)
        self._validate_value_nigth_bonus_value(values)
        res = super(Contract, self).create(values)
        return res

    #def create(self, cr, uid, values, context=None):
    #    if context is None: context = {}
    #    res = {}
    #    self.validate_changed_fields(cr, uid, None, values, 'create', context)
    #    res = super(hr_contract, self).create(cr, uid, values, context)
    #    return res


    def _validate_changed_fields(self, values, come_from):
        valid_value = False
        # BONO NOCTURNO
        '''night_bonus_check = values.get('night_bonus_check', False)
        if night_bonus_check:
            valid_value = True
        else:
            valid_value = False
        night_bonus_value = values.get('night_bonus_value', False)
        if night_bonus_value or valid_value:
            self._onchange_hours(night_bonus_value, 'nigth_bonus_value', come_from)
        '''
        # HORAS EXTRA DIURNO
        diurnal_extra_hours_check = values.get('diurnal_extra_hours_check', False)
        if diurnal_extra_hours_check:
            valid_value = True
        else:
            valid_value = False
        diurnal_extra_hours_value = values.get('diurnal_extra_hours_value', False)
        if diurnal_extra_hours_value or valid_value:
            self._onchange_hours(diurnal_extra_hours_value, 'diurnal_extra_hours_value', come_from)
        #else:
        #    if context.get('come_from', False) == 'write':
            #    self.onchange_horas(cr, uid, None, hrs_extra_diurno_value, 'hrs_extra_diurno_value', context=context)
        ####################### DESCUENTO DE HORAS###################################
        hours_not_worked_check = values.get('hours_not_worked_check', False)
        if hours_not_worked_check:
            valid_value = True
        else:
            valid_value = False
        hours_not_worked_value = values.get('hours_not_worked_value', False)
        if hours_not_worked_value or valid_value:
            self._onchange_hours(hours_not_worked_value, 'hours_not_worked_value', come_from)


        ############### DESCUENTO DE HORAS MES ANTERIOR ########################
        hours_not_worked_mes_ant_check = values.get('hours_not_worked_mes_ant_check', False)
        if hours_not_worked_mes_ant_check:
            valid_value = True
        else:
            valid_value = False
        hours_not_worked_mes_ant_value = values.get('hours_not_worked_mes_ant_value', False)
        if hours_not_worked_mes_ant_value or valid_value:
            self._onchange_hours(hours_not_worked_mes_ant_value, 'hours_not_worked_mes_ant_value',
                                 come_from)



        ######################### INASISTENCIA INJUSTIFICADA##############################
        unexcused_absences_check = values.get('unexcused_absences_check', False)
        if unexcused_absences_check:
            valid_value = True
        else:
            valid_value = False
        unexcused_absences_value = values.get('unexcused_absences_value', False)
        #if unexcused_absences_value or valid_value:
        #    self._onchange_hours(unexcused_absences_value, 'unexcused_absences_value', come_from)
        # PERMISO NO REMUNERADO
        unpaid_permit_hours_check = values.get('unpaid_permit_hours_check', False)
        if unpaid_permit_hours_check:
            valid_value = True
        else:
            valid_value = False
        unpaid_permit_hours_value = values.get('unpaid_permit_hours_value', False)
        if unpaid_permit_hours_value or valid_value:
            self._onchange_hours(unpaid_permit_hours_value, 'unpaid_permit_hours_value', come_from)
        return True

    @api.multi
    def _restore_all_fields(self, ids):
        contract_fields = {}
        if not hasattr(ids, '__iter__'):
            contract_id = [ids]
        else:
            contract_id = ids.get('contract_id',False)

        for contract in self.browse(contract_id[0]):
            #ASIGNACIONES
            c_id = contract.id
            if contract.night_bonus_check:
                contract_fields.update({'night_bonus_check':False,'night_bonus_value': 0.0})
            if contract.days_of_salary_pending_check:
               contract_fields.update({'days_of_salary_pending_check':False,'days_of_salary_pending_value':0})
            if contract.holidays_check:
                contract_fields.update({'holidays_check':False,'holidays_value':0})
           # if contract.holiday_not_worked_check:
            #    contract_fields.update({'holiday_not_worked_check':False,'holiday_not_worked_value':0})
            #if contract.diurnal_extra_hours_check:
             #   contract_fields.update({'diurnal_extra_hours_check':False,'diurnal_extra_hours_value':'0','diurnal_extra_hours':0.0})
            if contract.salary_retroactive_check:
                contract_fields.update({'salary_retroactive_check':False,'salary_retroactive_value':0.0})
            if contract.salary_assignment_check:
                contract_fields.update({'salary_assignment_check': False, 'salary_assignment_value': 0.0})
            if contract.non_salary_assignation_check:
                contract_fields.update({'non_salary_assignation_check': False, 'non_salary_assignation_value': 0.0})
            #DEDUCCIONES
            if contract.hours_not_worked_check:
                contract_fields.update({'hours_not_worked_check':False,'hours_not_worked_value':'0','hours_not_worked':0.0})
            #if contract.unexcused_absences_check:
             #   contract_fields.update({'unexcused_absences_check':False,'unexcused_absences_value':'0'})
          #  if contract.unpaid_permit_days_check:
           #     contract_fields.update({'unpaid_permit_days_check':False,'unpaid_permit_days_value':0})
            #if contract.unpaid_permit_hours_check:
             #   contract_fields.update({'unpaid_permit_hours_check':False,'unpaid_permit_hours_value':'0','unpaid_permit_hours':0.0})
            #if contract.salary_deduction_check:
             #   contract_fields.update({'deduccion_salarial_check': False, 'salary_deduction_value': '0'})
            if contract.salary_deduction_check:
                contract_fields.update({'salary_deduction_check': False, 'salary_deduction_value': '0'})
            if contract.non_salary_deduction_check:
                contract_fields.update({'non_salary_deduction_check': False, 'non_salary_deduction_value': '0'})
            if contract.deduction_bono_vac_check:
                contract_fields.update({'deduction_bono_vac_check': False, 'deduction_bono_vac_value': '0'})
            if contract.sundays_check:
                contract_fields.update({'sundays_check': False, 'sundays_value': '0'})
            if contract.ausencias_ded_check:
                contract_fields.update({'ausencias_ded_check': False, 'ausencias_ded_value': '0'})
            if contract.holidays_check:
                contract_fields.update({'holidays_check': False, 'holidays_value': '0'})
            if contract.retroactivo_check:
                contract_fields.update({'retroactivo_check': False, 'retroactivo_value': '0'})
            if contract.prestamo_check:
                contract_fields.update({'prestamo_check': False, 'prestamo_value': '0'})
            if contract.hours_not_worked_mes_ant_check:
                contract_fields.update({'hours_not_worked_mes_ant_check': False, 'hours_not_worked_mes_ant_value': '0','hours_not_worked_mes_ant': 0.0})

        if contract_fields:
            sql_update_clause = 'update hr_contract set '
            sql_where_clause = ' where id in %s'
            sql_middle_cluase = ''
            for key, value in contract_fields.items():
                sql_middle_cluase = sql_middle_cluase + key + '=' + str(value) + ', '
            sql_middle_cluase = sql_middle_cluase[:-2]
            sql_string = sql_update_clause + sql_middle_cluase + sql_where_clause
            self.env.cr.execute(sql_string, (tuple([c_id]),))
                # self.write(contract_id,contract_fields)

    def _validate_extra_hours(self, field, value):
        res = {}
        extra_hours_obj = re.compile(r"""^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$""", re.X)
        if extra_hours_obj.search(value):
            res = {
                field: value
            }
        return res

    def _onchange_hours(self, value, field, come_from=None):
        res = {}
        if 'float' not in field:
            if value:
                res = self._validate_extra_hours(field, value)
                if not res:
                    raise ValidationError(_('El formato de las horas es incorrecto, Solo acepta valores entre 00:00 y 23:59..\n'
                                            'Ej: 20:55. Por favor intente de nuevo'))
                value = self._convert_time_to_value(value)
                field_name = field[:-len('_value')]
                res.update({field_name:value})
            else:
                if come_from:
                    raise ValidationError(_('Ha seleccionado el campo %s, pero no ha introducido ningún valor.\n'
                                            'No puede guardar el campo vacío. Por favor intente de nuevo')%(self._get_name_field(field)))
        return {'value': res}
    '''
    @api.onchange('night_bonus_value')
    def _on_change_night_bonus_value(self):
        return self._onchange_hours(self.night_bonus_value,'night_bonus_value')
    '''

    @api.onchange('diurnal_extra_hours_value')
    def _on_change_diurnal_extra_hours_value(self):
        return self._onchange_hours(self.diurnal_extra_hours_value,'diurnal_extra_hours_value')

    @api.onchange('hours_not_worked_value')
    def _on_change_hours_not_worked_value(self):
        return self._onchange_hours(self.hours_not_worked_value,'hours_not_worked_value')

    @api.onchange('hours_not_worked_mes_ant_value')
    def _on_change_hours_not_worked_mes_ant_value(self):
        return self._onchange_hours(self.hours_not_worked_mes_ant_value, 'hours_not_worked_mes_ant_value')

    #@api.onchange('unexcused_absences_value')
    #def _on_change_unexcused_absences_value(self):
    #    return self._onchange_hours(self.unexcused_absences_value,'unexcused_absences_value')

    @api.onchange('unpaid_permit_hours_value')
    def _on_change_unpaid_permit_hours_value(self):
        return self._onchange_hours(self.unpaid_permit_hours_value,'unpaid_permit_hours_value')

    #@api.multi
    def _get_name_field(self, field):
        name = ''
        field_obj = self.env['ir.model.fields']
        #field_obj = self.pool.get('ir.model.fields')
        field_id = field_obj.search([('model','=','hr.contract'),('name','=',field)])
        #field_id = field_obj.search(cr, uid,[('model','=','hr.contract'),('name','=',field)] , context=context)
        if field_id:
            #nombre = field_obj.read(cr, uid,field_id, ['field_description'], context=context)
            name = field_obj.read(field_id, ['field_description'])
            #nombre = str(nombre[0]['field_description']).split('Valor')[0]
        #    name = str(name[0]['field_description']).split('Valor')[0]
        return name

    def _convert_time_to_value(self,time=None):
        result = horas = temp_value = 0.0
        if time:
            t = time.split(':')
            horas = float(t[0])
            temp_value = float(t[1])/60.0
            result = horas + temp_value
        return result

Contract()

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    @api.multi
    def hr_verify_sheet(self):
        # if context is None: context = {}
        # if not hasattr(ids, '__iter__'): ids = [ids]
        res = super(HrPayslip, self).hr_verify_sheet()
        is_payoff = self.env.context.get('come_from', False)
        if not  is_payoff:
            contract_id = self.read(['contract_id'])
            contract_obj = self.env['hr.contract']
            contract_obj.restore_all_fields(contract_id[0])
        return res
HrPayslip()

class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'

    # def close_payslip_run(self, cr, uid, ids, context=None):
    #     if context is None: context = {}
    #     if not hasattr(ids, '__iter__'): ids = [ids]
    #     res = super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context)
    #     slip_ids_obj = self.browse(cr, uid, ids)
    #     contract_obj = self.pool.get('hr.contract')
    #     hr_payslip_obj = self.pool.get('hr.payslip')
    #     for slip_id in hr_payslip_obj.browse(cr, uid, slip_ids_obj[0].slip_ids.id):
    #         contract_id = slip_id.contract_id.id
    #         contract_obj.restore_all_fields(cr, uid, contract_id, context)
    #     return res
    @api.multi
    def close_payslip_run(self):
        # if context is None: context = {}
        # if not hasattr(ids, '__iter__'): ids = [ids]
        res = super(HrPayslipRun, self).close_payslip_run()
        for slip_run in self.browse(self.ids):
            for slip in slip_run.slip_ids:
                slip.contract_id._restore_all_fields(slip.contract_id.id)
        return res
HrPayslipRun()