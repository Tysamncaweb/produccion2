# coding: utf-8
from odoo import fields, models, api, exceptions
from odoo import osv
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


class hr_payslip(models.Model):
    _inherit ='hr.payslip'

    ESTADOS = [
        ('draft', 'Borrador'),
        ('verify', 'Verificado'),
        ('confirm', 'Confirmado'),
        ('done', 'Realizado'),
        ('cancel', 'Cancelado'),
    ]
    department_id = fields.Many2one('hr.department', 'Departamento')
    job_id = fields.Many2one('hr.job', 'Cargo')
    contract_id = fields.Many2one('hr.contract', 'Contratos liquidacion')
    tiempo_servicio_dias = fields.Integer('Tiempo de servicio en Dias')
    tiempo_servicio_meses = fields.Integer('Tiempo de servicio en Meses')
    tiempo_servicio_year = fields.Integer('Tiempo de servicio en  Years')
    antiguedad_19061997_dias = fields.Integer('Antiuedad dede 1906199 Dias')
    antiguedad_19061997_meses = fields.Integer('Antiuedad dede 1906199 Meses')
    antiguedad_19061997_year = fields.Integer('Antiuedad dede 1906199 Years')
    month_worked_year_str = fields.Char('Meses trabajados en el año', size=20, help="Tiempo trabajado durante el año.")
    month_worked_year = fields.Integer('Meses trabajados en el año', help="Meses trabajados durante el año.")
    conceptos_salariales = fields.Many2many('hr.salary.rule', 'payslip_liquidacion_rel', 'payslip_id', 'rule_id','Conceptos salariales')
    notes = fields.Text('Observaciones', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(ESTADOS, string='state',
        help='* Cuando la liquidacion es creada el estado es \'Borrador\'.\
        \n* Si la liquidacion esta bajo verificacion, El estado es \'En Espera\'. \
        \n* Si la liquidacion es confirmada entonces el estado cambia a \'Hecho\'.\
        \n* Cuando el usuario cancela la liquidacion el estado es \'Cancelado\'.')
    vacation_amount = fields.Float('Bono de Vacaciones', digits=(10, 2))
    dias_habiles = fields.Integer('Nro dias habiles', help=u'este campo trae los días hábiles')
    days_to_pay = fields.Integer('Días a pagar')
    vacation_reserva = fields.Float('Dias/Porcion Reserva')
    salario_integral = fields.Float('Salario integral', digits=(10, 2))
    dias_adicionales = fields.Integer('Dias adicionales')
    tiempo_servicio = fields.Integer("Tiempo de servicio")
    ut = fields.Integer('Unidad Tributaria', help='este campo trae la Unidad Tributaria')
    general_state = fields.Char('Estado General', size=100)
    is_payoff = fields.Boolean('Es liquidacion')
    salario_basico = fields.Float('Salario Basico Mensual', digits=(10, 2))
    salario_basico_diario = fields.Float('Salario Basico diario', digits=(10, 2))
    salario_prom_mensual = fields.Float('Salario promedio mensual', digits=(10, 2))
    salario_prom_diairo = fields.Float('Salario promedio diario', digits=(10, 2))
    alic_bono_vac_liq = fields.Float('Alicuota bono vacacional liquidacion', digits=(10, 2))
    alic_util_liq = fields.Float('Alicuota utilidades liquidacion', digits=(10, 2))

    @api.onchange('employee_id')
    def onchange_employee_dos(self):
        if self._context.get('is_payoff'):
            res = {}
            job = False
            employee_obj = self.env['hr.employee']
            contract_obj = self.env['hr.contract']
            if self.employee_id:
                employee_data = employee_obj.browse([self.employee_id.id])
                department_id = employee_data.department_id.id
                job_id = employee_data.job_id.id
                contract_id = contract_obj.search([('employee_id', '=', self.employee_id.id)])
                # contract_id = employee_obj._get_latest_contract([self.employee_id.id])
                if contract_id:
                    contract_data = contract_obj.browse([contract_id.id])
                    date_start = contract_data.date_start
                    date_end = contract_data.date_end
                    wage = contract_data.wage
                    state = contract_data.state
                    if state != 'cancel':
                        raise exceptions.except_orm(('Advertencia!'),
                                                    ('El empleado no posee un contrato en estado "Cancelado"'))
                else:

                    raise exceptions.except_orm(('Advertencia!'),
                                                ('El empleado ', self.employee_id.name, ' no posee contrato!'))
            else:
                return {'value': res}
            self.department_id = department_id
            self.job_id = job_id
            self.date_from = date_start
            self.date_to = date_end

    @api.onchange('date_to')
    def onchange_date_end(self):
        if self._context.get('is_payoff'):
            config_obj = self.env['hr.config.parameter']
            tiempo_servicio = {
                'dias': 0,
                'meses': 0,
                'anios': 0,
            }
            antiguedad_19061977 = {
                'dias': 0,
                'meses': 0,
                'anios': 0,
            }
            months_worked_year = 0
            months_worked_year_int = 0
            ts = 0
            ult_liqu_colectiva = config_obj._hr_get_parameter('hr.payslip.ultima.liquidacion.colectiva',True)
            if self.date_from and self.date_to:
                # se le suma un dia a la fecha de finalizacion de la relacion laboral porque se considera que ese dia el empleado trabaja
                fecha_temp = datetime.strptime(self.date_to, DEFAULT_SERVER_DATE_FORMAT)
                fecha_temp = fecha_temp + relativedelta(days=1)
                date_end = datetime.strftime(fecha_temp, DEFAULT_SERVER_DATE_FORMAT)
                #TODO si se requiere se puede hacer persistir en el contrato la fecha de culminacion. Solo cuando se confirme la liquidacion
                tiempo_servicio = self.get_years_service(self.date_from, date_end)
                ts = tiempo_servicio['anios'] + 1 if tiempo_servicio['meses'] >= 6 else tiempo_servicio['anios']

                if self.employee_id:
                    #employee = self.env['hr.employee'].search(['id', '=', self.employee_id.id])

                    if datetime.strptime(self.date_from, DEFAULT_SERVER_DATE_FORMAT) < datetime.strptime(ult_liqu_colectiva,
                                                                                           DEFAULT_SERVER_DATE_FORMAT):
                        antiguedad_19061977 = self.get_years_service(self.employee_id.fecha_inicio, date_end)
                        ts = antiguedad_19061977['anios'] + 1 if antiguedad_19061977['meses'] >= 6 else antiguedad_19061977[
                            'anios']

                    months_worked_year, months_worked_year_int = self.get_year_worked_time(self.date_from, date_end)

                    return {'value': {
                        'tiempo_servicio_dias': tiempo_servicio['dias'],
                        'tiempo_servicio_meses': tiempo_servicio['meses'],
                        'tiempo_servicio_year': tiempo_servicio['anios'],
                        'antiguedad_19061997_dias': antiguedad_19061977['dias'],
                        'antiguedad_19061997_meses': antiguedad_19061977['meses'],
                        'antiguedad_19061997_year': antiguedad_19061977['anios'],
                        'month_worked_year_str': months_worked_year,
                        'month_worked_year': months_worked_year_int,
                        'tiempo_servicio': ts,
                    }
                    }

    @api.v7
    def get_years_service(self, fecha_inicio, fecha_fin=None):
        dias = 0
        meses = 0
        anios = 0
        res = {}
        if fecha_inicio and fecha_fin:
            antiguedad = relativedelta(datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT),
                                                     datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT))
            res = {
                'dias': antiguedad.days,
                'meses': antiguedad.months,
                'anios': antiguedad.years,
            }
        return res

    @api.v7
    def get_year_worked_time(self, date_start, date_end=None):
        year_worked_time = ''
        if not date_end:
            ahora = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            ahora = date_end
        date_start_year = "-01-01"
        date_start_year = ahora.split("-")[0] + date_start_year
        if date_start > date_start_year:
            months_worked_year = self.get_years_service(date_start, ahora)
        else:
            months_worked_year = self.get_years_service(date_start_year, ahora)
        months_worked_year_int = months_worked_year['meses']
        year_worked_time = str(months_worked_year['meses']) + (' meses' if months_worked_year['meses'] > 1 else ' mes ') \
                           + (' y ' + str(months_worked_year['dias']) + (
        ' días' if months_worked_year['dias'] > 1 else ' dia') if months_worked_year['dias'] > 0 else '')
        return year_worked_time, months_worked_year_int

    @api.onchange('struct_id')
    def onchange_tipo_liquidacion(self):
        struct_obj = self.env['hr.payroll.structure']
        conceptos_ids = []
        if self.struct_id:
            conceptos_ids = [cs.id for tilio in struct_obj.browse(self.struct_id.id) for cs in tilio.rule_ids]
        if conceptos_ids:
            self.conceptos_salariales = [(6,0,conceptos_ids)]

    @api.multi
    def hr_verify_sheet(self):
        #self.compute_sheet()
        ctx = self._context.copy() or {}
        is_payoff = self.env.context.get('come_from', False)
        payoff_values = {}
        if is_payoff:
            ctx.update({'slip_id': self.ids[0]})
            self.env.context = ctx
            payoff_values = self.get_payoff_values()
            payoff_values.update({'is_payoff': True})
            self.write(payoff_values)
            self.compute_sheet_2()

        return self.write({'state': 'verify'})

    @api.multi
    def compute_sheet_2(self):

        slip_line_pool = self.env['hr.payslip.line']
        sequence_obj = self.env['ir.sequence']
        for payslip in self.browse(self._ids):
            number = payslip.number or sequence_obj.next_by_code('salary.slip')
            # delete old payslip lines
            old_slipline_ids = slip_line_pool.search([('slip_id', '=', payslip.id)])
            #            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink()
            if payslip.contract_id:
                # set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to
                                                 )
            lines = [(0, 0, line) for line in
                     self._get_payslip_lines(contract_ids, payslip.id)]
            self.write({'line_ids': lines, 'number': number})
        return
    #  @api.multi
        #  def hr_verify_sheet(self):

        #   res = super(hr_payslip, self).hr_verify_sheet()
    #   return res

    @api.multi
    def hr_action_cancel(self):
        return self.write({'state': 'cancel','is_payoff': True})

    # colocar el estado en "borrador"
    @api.multi
    def hr_action_draft(self):
        return self.write({'state': 'draft'})

    # colocar el estado en "confirmado"
    @api.multi
    def hr_action_confirm(self):
        return self.write({'state': 'confirm'})

    # colocar el estado en "hecho"
    @api.multi
    def hr_action_done(self, context=None):
        sequence_obj = self.env['ir.sequence']
        #number = sequence_obj.next_by_code('salary.slip')
        #struct_new = self.env['hr.contract'].search([('employee_id', '=', self.employee_id)])
        for slip in self:
            # slip.write({'number': number}) #ya venia comentado!!!
            self = self.with_context({'struct_id': slip.struct_id.id, 'payoff': 'payoff',
                                      'payoff_date': datetime.now().strftime('%Y-%m-%d')})
            slip.action_payslip_done()

            if slip.move_id:
                slip.move_id.write(
                    {'name': '%s de %s' % (slip.struct_id.name, slip.employee_id.name)})
            self.employee_id.write({'active': False})
        return self.write({'state': 'done'})

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        ir_ui_obj = self.env['ir.ui.view']
        context = self._context
        is_payoff = context.get('is_payoff',False)
        if view_type == 'form':
            if is_payoff:
                view_id = ir_ui_obj.search([('name', '=', 'hr.payroll.payoff.form.view')], limit=1).id
            else:
                view_id = ir_ui_obj.search([('name', '=', 'hr.payslip.form')], limit=1).id

        return super(hr_payslip, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

    @api.model
    def create(self,values, context=None):
        if context is None: context = {}
        res = {}

        if context.get('is_payoff', False):
            values.update({'is_payoff': True})
        res = super(hr_payslip, self).create(values)
        return res

    @api.multi
    def write(self, values):
        # if context is None: context = {}
        # if not hasattr(ids, '__iter__'): ids = [ids]
        # values = {}
        if self.env.context.get('is_payoff', False):
            values.update({'is_payoff': True})
        res = super(hr_payslip, self).write(values)
        return res

    def get_payoff_values(self):
        values = {}
        limite = 2
        dias_b_v = 0
        config_obj = self.env['hr.config.parameter']
        vacaciones_obj = self.env["hr.payroll.dias.vacaciones"]
        dias_str = config_obj._hr_get_parameter( 'hr.dias.x.mes')

        # SALARIO BASE
        sal_mensual = self.employee_id.contract_id.wage

        #SALARIO PROMEDIO
        tipo_pago = self.employee_id.contract_id.schedule_pay
        if tipo_pago == 'monthly':
            limite=1
        elif tipo_pago == 'weekly':
            #TODO obtener el numero de lunes
            limite = self.get_mondays(self.date_to)
        promedio = self.calculo_sueldo_promedio(self.employee_id, self.date_to, 0, 'liquidacion', limite)
        #CALCULO DE ALICUOTAS
        vacation_id = vacaciones_obj.search([('service_years', '=', self.tiempo_servicio_year)])
        if vacation_id:
            dias_b_v = vacaciones_obj.browse(int(vacation_id.pay_days))

        alic_b_v = self.calculo_alic_bono_vac(sal_mensual+promedio, dias_b_v)
        alic_u =  self.calculo_alic_util(sal_mensual+promedio,alic_b_v)
        values.update({'salario_basico':sal_mensual,
                       'salario_basico_diario':sal_mensual/float(dias_str),
                       'salario_prom_mensual': sal_mensual + promedio,
                       'salario_prom_diairo': (sal_mensual + promedio) / float(dias_str),
                       'alic_bono_vac_liq': alic_b_v,
                       'alic_util_liq': alic_u,
                       'salario_integral':(sal_mensual+promedio)/float(dias_str) + alic_b_v + alic_u})
        return values

    def get_mondays(self,fecha):
        mondays = 0
        rango = self.rango_mes_anterior(fecha,0)
        recursive_days = date_from = datetime.strptime(rango[0], DEFAULT_SERVER_DATE_FORMAT)
        date_to = datetime.strptime(rango[1], DEFAULT_SERVER_DATE_FORMAT)
        date_end = date_to + relativedelta(days=+1)
        while recursive_days != date_end:
            if recursive_days.weekday() == 0:
                mondays += 1
            recursive_days += relativedelta(days=+1)
        return mondays







'''
class hr_payroll_structure(models.Model):
        _inherit = 'hr.payroll.structure'

        @api.multi
        def get_all_rules(self):
            all_rules = []
            is_payoff = self._context.get('come_from', False)
            if is_payoff and 'payoff' in is_payoff:
                payslip_id = self._context.get('slip_id', False)
                if payslip_id:
                    concept_ids = self.env['hr.payslip'].browse([payslip_id])
                    all_rules += self.env['hr.salary.rule']._recursive_search_of_rules()
                pass
            else:
                for struct in self.structure_ids:
                    all_rules += self.env['hr.salary.rule']._recursive_search_of_rules()
            return all_rules
'''

