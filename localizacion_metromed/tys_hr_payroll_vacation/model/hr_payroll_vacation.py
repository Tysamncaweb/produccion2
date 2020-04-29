# coding: utf-8
# from openerp import fields, models, api
from odoo import fields, models, api
from dateutil import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(models.Model):
    _inherit ='hr.payslip'


    dias_a_pagar_va = fields.Integer('Dias a pagar vacaciones')
    tiempo_servicio_va = fields.Integer('Tiempo de servicio vacaciones')
    salario_mensual_va = fields.Float('Salario mensual vacaciones',digits=(10,2))
    domingos = fields.Integer('Domingos vacacioneas')
    dias_porcion =fields.Float('Dias Porcion',digits=(10,2))
    # 'dias_adicional':fields.integer('Dias adicionales'),
    dias_festivos = fields.Integer('Dias festivos')


    @api.multi
    def compute_sheet(self):
        # res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        special_struct_obj = self.env['hr.payroll.structure']
        run_obj = self.env['hr.payslip.run']
        config_obj = self.env['hr.config.parameter']
        feriados = 0
        sueldo_promedio = 0.0
        active_id = self._context.get('active_id', False)
        tiempo_servicio = {}
        vacaciones = {}
        payslip_values = {}
        dias_x_periodo = {}
        tipo_nomina = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.vacaciones', True)

        special_fields = run_obj.search([('id', '=', active_id)])
        is_special = special_fields.check_special_struct
        structure_ids = [special_fields.struct_id.id]
        #is_special = self._context.get('is_special', False)
        #special_id = self._context.get('special_id', False)
        psr = None
        if active_id:
            psr = run_obj.browse(active_id)
        if is_special and structure_ids:
            for payslip_id in self.ids:
                payslip = self.search([('id', '=', payslip_id)])
                special_obj = special_struct_obj.browse(structure_ids)
                if 'code' in special_obj:
#                if  special_obj.code in tipo_nomina:
                    dias_x_periodo = self.calcula_dias_x_periodo(payslip.date_from, payslip.date_to)
                    feriados = self.get_feriados_2(payslip.date_from, payslip.date_to)
                    tiempo_servicio = self.get_years_service(payslip.contract_id.date_start, payslip.date_to)
                    vacaciones = self.get_dias_bono_vacacional(tiempo_servicio)
                    sueldo_promedio = self.calculo_sueldo_promedio(payslip.employee_id, payslip.date_from, 1, 'vacaciones')
                payslip_values.update({
                    'salario_mensual_va':  sueldo_promedio,
                    'domingos': dias_x_periodo.get('domingos',False),
                    'dias_festivos': feriados,
                    'dias_porcion': vacaciones.get('asignacion',False),
                    'dias_a_pagar_va':vacaciones.get('asignacion',False),
                    'tiempo_servicio_va':tiempo_servicio.get('anios',False),
                })
                self.write(payslip_values)
        res = super(hr_payslip, self).compute_sheet()
        return res


#
# class hr_contract(osv.osv):
#     _inherit = 'hr.contract'
#     _columns = {
#         'fecha_modificado': fields.date('Bono Nocturno Valor'),
#         'fideicomiso': fields.float('Bono Nocturno', digits=(10, 2)),
#     }

