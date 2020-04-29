from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.tys_hr_resumen_nomina.template_hr_payroll_summary_report'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip.run'].browse(docids)}
        res = dict()
        docs = []
        contract = self.env['hr.contract']
        payslip = self.env['hr.payslip']
        docs2 = []
        var2 = 0
        cont = 0
        department = []
        department_work = []
        total_final = 0
        total_monto = 0
        payslip_run= payslip.search([('payslip_run_id', '=', docids)])
        for slip in payslip_run:
            if slip.employee_id.department_id.name:
                if department:
                    cont = 0
                    for a in department:
                        if a == slip.employee_id.department_id.name:
                            cont += 1
                    if cont == 0:
                        department.append(slip.employee_id.department_id.name)
                else:
                    department.append(slip.employee_id.department_id.name)
            total_final += 1
        for b in department:
            cont3 = 0
            for slip in payslip_run:
                if b == slip.employee_id.department_id.name:
                    cont3 +=1
                    cont2 = 0
                    fecha_actual0 = str(date.today())
                    fecha_actual = fecha_actual0[8:10] + "/" + fecha_actual0[5:7] + "/" + fecha_actual0[0:4]
                    date_start = str(slip.date_from)
                    fecha_start = date_start[8:10] + "/" + date_start[5:7] + "/" + date_start[0:4]
                    date_end = str(slip.date_to)
                    fecha_end = date_end[8:10] + "/" + date_end[5:7] + "/" + date_end[0:4]
                    for a in slip.line_ids:
                        cant_sueldo = ' '
                        unidad = ' '
                        if a.category_id.name == 'Basic':
                            totalD_asig = a.total
                        if a.category_id.name == 'Gross':
                            totalD_ded = a.total
                        if a.category_id.name == 'Net':
                            totalD_net = a.total

                        if a.category_id.code == 'ALW':
                            cont += 1
                            cont2 += 1

                            if a.amount_python_compute:
                                if (a.amount_python_compute.find("worked_days.WORK100.number_of_days") != -1):
                                    cant_sueldo= 15
                                    varsal = a.total
                                    unidad = "{0:.2f}".format(varsal/15)
                                if a.amount_python_compute.find("night_bonus_value") != -1:
                                   cant_sueldo = int(round(a.total/(((varsal*2)/30)*1.3)))
                                   unidad = "{0:.2f}".format(a.total/cant_sueldo)
                                if a.amount_python_compute.find("days_of_salary_pending_value") != -1:
                                    cant_sueldo = slip.contract_id.days_of_salary_pending_value
                                    unidad = "{0:.2f}".format(a.total/cant_sueldo)
                                if  a.amount_python_compute.find("sundays_value") != -1:
                                    cant_sueldo = int(round((a.total)/((varsal/15)*1.5)))
                                    unidad = "{0:.2f}".format(a.total/cant_sueldo)


                            uni = str(unidad).split('.')
                            unidad_conv = ",".join(uni)
                            tot = str(a.total).split('.')
                            total_asg_conv =  ",".join(tot)
                            docs2.append({
                                'descripcion': a.name,
                                'total_alw': total_asg_conv,
                                'total_ded' : ' ',
                                'code': a.code,
                                'cant_sueldo': cant_sueldo,
                                'unidad': unidad_conv,
                            })

                        elif a.category_id.code == 'DED':
                            cont += 1
                            cont2 += 1
                            uni2 = str(unidad).split('.')
                            unidad_conv1 = ",".join(uni2)
                            tot1 = str(a.total).split('.')
                            total_ded_conv = ",".join(tot1)
                            docs2.append({
                                'descripcion': a.name,
                                'total_alw': ' ',
                                'total_ded': total_ded_conv,
                                'code': a.code,
                                'cant_sueldo': cant_sueldo,
                                'unidad': unidad_conv1,
                            })
                    total_monto += totalD_net

                    asig = str(totalD_asig).split('.')
                    asig_conv = ",".join(asig)
                    ded = str(totalD_ded).split('.')
                    ded_conv = ",".join(ded)
                    net = str(totalD_net).split('.')
                    net_conv = ",".join(net)
                    wage1 = slip.contract_id.wage
                    sueld = str(wage1).split('.')
                    sueldo_lis = ",".join(sueld)
                    docs.append({
                        'ci': slip.employee_id.identification_id_2,
                        'employee': slip.employee_id.name,
                        'f_ing': slip.employee_id.fecha_inicio,
                        'wage': sueldo_lis,
                        'cargo': slip.contract_id.job_id.name,
                        'concepto': slip.contract_id.struct_id.name,
                        'var1': cont -1,
                        'var2': var2,
                        'asig_total' : asig_conv,
                        'ded_total' :  ded_conv,
                        'net_total' : net_conv,
                        'department': slip.employee_id.department_id.name,
                        'total_depart' : totalD_net,
                    })
                    var2 = var2 + cont2
            department_work.append(cont3)
            #docs.append({'cont3': cont3,})
        var_departamento = department[0]

        final = str("{0:.2f}".format(total_monto)).split('.')
        final_total = ",".join(final)
        return {
            'data': data['form'],
            'model': self.env['report.tys_hr_resumen_nomina.template_hr_payroll_summary_report'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'docs2': docs2,
            'date_start': fecha_start,
            'date_end': fecha_end,
            'date_actual' : fecha_actual,
            'department_work': department_work,
            'var_departamento': var_departamento,
            'total_final': total_final,
            'monto_final': final_total,
        }

