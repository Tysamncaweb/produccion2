# coding: utf-8
from odoo import fields, models, api,_, exceptions

class hr_special_days(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):

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
                contract_ids = self.get_contract( payslip.employee_id, payslip.date_from, payslip.date_to
                                                )
            if not contract_ids or len(contract_ids) == 0:
                raise exceptions.except_orm(_('Advertencia!'), (u'La nómina que esta intentando generar, no posee contrato y/o estructura salarial.\n \
                    Por favor verifique el contrato del empleado %s y corrija para proceder a generar las nóminas\n correspondientes.')%(payslip.employee_id.name))
            lines = [(0, 0, line) for line in
                     self._get_payslip_lines( contract_ids, payslip.id)]
            self.write({'line_ids': lines, 'number': number})
            return super(hr_special_days, self).compute_sheet()

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):


        if not self.employee_id.contract_id:
            self.contract_id = False
            self.struct_id = False
        res = super(hr_special_days, self).onchange_employee()
        return res
