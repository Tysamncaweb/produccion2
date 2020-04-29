# coding: utf-8
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
import calendar

class hr_special_days(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    @api.depends('date_from', 'date_to')
    def _compute_days(self):
         for slip in self:
            holydays = mondays = saturdays = sundays = workdays = 0
            hollydays_str = ''
            hr_payroll_hollydays = slip.env['hr.payroll.hollydays']
            fecha_desde = None
            fecha_hasta = None
            if slip.date_from and slip.date_to:
                fecha_desde = slip.date_from
                fecha_hasta = slip.date_to
            else:
                ctx = slip._context.copy()
                psr = slip.env['hr.payslip.run'].browse([ctx.get('active_id')])
                for p in psr:
                    fecha_desde = p.date_start
                    fecha_hasta = p.date_end

            recursive_days = date_from = datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT)
            date_to = datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT)
            date_end = date_to + relativedelta(days=+1)

            while recursive_days != date_end:
                hollyday_id = hr_payroll_hollydays.search(
                    [('date_from', '<=', str(recursive_days)[:10]), ('date_to', '>=', str(recursive_days)[:10])])
                if hollyday_id:
                    holydays += 1
                    holyday_obj = hr_payroll_hollydays.browse(hollyday_id.id)
                    hollydays_str += str(recursive_days)[:10] + ': ' + holyday_obj[0].nombre + '\n'

                elif recursive_days.weekday() == 5:
                    saturdays += 1
                elif recursive_days.weekday() == 6:
                    sundays += 1
                if recursive_days.weekday() == 0:
                    mondays += 1
                if  0 <=    recursive_days.weekday() <= 4:
                    workdays += 1

                recursive_days += relativedelta(days=+1)

            # workdays = self.validate_workdays(workdays,saturdays,sundays,holydays,slip.date_from,slip.date_to)
            workdays = 15 - saturdays - sundays - holydays
            slip.saturdays = saturdays
            slip.sundays = sundays
            slip.holydays = holydays
            slip.mondays = mondays
            slip.workdays = workdays


    saturdays = fields.Integer('Sabados', compute='_compute_days', store=True, readonly=True)
    sundays = fields.Integer('Domingos', compute='_compute_days', store=True, readonly=True)
    holydays = fields.Integer('Dias Festivos', compute='_compute_days', store=True, readonly=True)
    mondays = fields.Integer('Nro lunes', help='este campo trae el numero de lunes', compute='_compute_days', store=True, readonly=True)
    workdays = fields.Integer('Dias habiles', help='este campo los dias habiles del periodo', compute='_compute_days',
                             store=True, readonly=True)
    hollydays_str = fields.Char('Feriados', size=768)



class hr_payroll_hollydays(models.Model):
    _name = 'hr.payroll.hollydays'
    _description = 'Dias Feriados'

    hollydays = fields.Boolean('Dias')
    nombre = fields.Char('Motivo del dia Festivo', size=256, required=True)
    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta')


    @api.onchange('date_from')
    def onchange_date_from(self):
        if not self.hollydays:
            self.date_to = self.date_from

    @api.onchange('hollydays')
    def onchange_date_hollydays(self):
        if not self.hollydays:
            self.date_to = self.date_from
