from odoo import models, fields, api,exceptions, _
from datetime import datetime
from dateutil import relativedelta
_DATETIME_FORMAT = "%Y-%m-%d"

class salary_increase(models.Model):
    _name = "salary.increase"
    _description = "Salary Increase"


    state = fields.Selection([('draft', 'Borrador'),
        ('calculate', 'Calcular'),
        ('done', 'Calculado')], 'Estado', default ='draft')
    name = fields.Char("Motivo", size=64, required=True, states={'draft': [('readonly', False)]})
    wage = fields.Float('Porcentaje de Aumento',size=3, states={'draft': [('readonly', False)]})
    fecha_decrete = fields.Date('Fecha del Decreto', help='Fecha del Decreto Presidencial',  states={'draft': [('readonly', False)]})
    fecha_increase = fields.Date('Fecha del Aumento', required=True, help='Fecha del Decreto Presidencial', states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'Responsable',   states={'draft': [('readonly', False)]}, default=lambda s: s._uid)
    employee_ids = fields.One2many('salary.increase.line', 'salary_increase_id','Empleado', readonly=True, states={'draft': [('readonly', False)]})
    type_aumento = fields.Selection([('mov', 'Monto'), ('por', 'Porcentaje')], 'Tipo de Aumento')
    monto = fields.Float('Monto')



    @api.multi
    def upload_wage(self):
        return self._uid


    @api.onchange('type_aumento')
    def onchange_validar(self):

        if self.type_aumento == 'mov':
            self.wage = False

        if self.type_aumento == 'por':
            self.monto = False
        else:

            return {}

    @api.onchange('monto')
    def onchange_porcent(self):
        if self.employee_ids:

            for i in self.employee_ids:
                i.amount = monto = self.monto


    @api.multi
    def upload_wage(self):
        contract_obj = self.env['hr.contract']
        for si in self.browse(self.ids):
            if si.employee_ids:
                for line in si.employee_ids:
                    contract = line.employee_id.contract_id
                    line.write({'past_amount': contract.wage})
                    # contract.employee_id.contract_id.write({'wage': line.amount + contract.wage})
                    contract.write({'wage': line.amount + contract.wage})
        self.write({'state': 'done'})

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def upload_calcular(self):
        if self.type_aumento=='mov':
            if self.monto==False:
                raise exceptions.except_orm(_('Error !'), _('El monto debe ser mayor a cero'))
        if self.type_aumento == 'por':
            if self.wage==False:
                raise exceptions.except_orm(_('Error !'), _('El monto debe ser mayor a cero'))



        for i in self:
            employees = self.search([('employee_ids.employee_id', '=', [j.employee_id.id for j in i.employee_ids]),
                         ('fecha_increase', '=', i.fecha_increase)])
            if len(employees) > 1:
                raise exceptions.except_orm(_('Error !'), _('El Empleado que ha ingresado ya tiene aumento de la fecha'+' '+ i.fecha_increase))
            if not i.employee_ids:
                raise exceptions.except_orm(_('Error !'), _('Debe Agregar al Empleado'))
        self.write({'state': 'calculate'})


    @api.onchange('wage')
    def onchange_wage(self):
        if self.employee_ids:

            for line in self.employee_ids:
                line.porcent = self.wage
                contract = line.employee_id.contract_id
                line.amount = contract.wage * self.wage/100

                # validacion de fecha

    @api.onchange('fecha_increase')
    def onchange_date_fecha(self):
        fecha = self.fecha_increase
        if self.fecha_decrete:
            if self.fecha_increase < self.fecha_decrete:
                self.fecha_increase = False
                return {'warning': {'title': "Advertencia!",
                                    'message': "La Fecha del Aumento debe ser Mayor a la Fecha del Decreto"}}

    @api.onchange('fecha_decrete')
    def onchange_fecha_decrete(self):
        if self.fecha_increase:
            if self.fecha_decrete > self.fecha_increase:
                self.fecha_decrete = False
                self.wage = False
                return {'warning': {'title': "Advertencia!",
                                    'message': "La Fecha del Decreto debe ser Menor a la Fecha del Aumento"}}

    @api.onchange('wage')
    def onchange_date(self):
        por = self.wage
        if por <= 999:
            self.wage = por
        else:
            self.wage = False
            return {'warning': {'title': "Advertencia!",
                                'message': "El Porcentaje  Debe se Menor a 3 Digitos "}}

    @api.multi
    def _calculate_date(self, value):
        age = 0
        if value:
            ahora = datetime.now().strftime(_DATETIME_FORMAT)
            age = relativedelta.relativedelta(datetime.strptime(ahora, _DATETIME_FORMAT),
                                                  datetime.strptime(value, _DATETIME_FORMAT))
        return age


class salary_line(models.Model):

    _name = "salary.increase.line"
    _description = "History Salary Increase"
    _order = "fecha_increase desc"

    salary_increase_id = fields.Many2one(comodel_name="salary.increase", string="Incremento")
    employee_id = fields.Many2one('hr.employee','Empleado', readonly=True)
    vat = fields.Char(string="C.I", related='employee_id.identification_id_2', readonly=True)
    porcent = fields.Integer(string="Porcentaje", readonly=True)
    past_amount = fields.Float(string="Salario anterior")
    amount = fields.Float(string="Monto")
    fecha_increase = fields.Date(string="Fecha del Aumento", related='salary_increase_id.fecha_increase', store=True)
    increase_name = fields.Char(string="Motivo", related='salary_increase_id.name', readonly=True)


    @api.onchange('porcent')
    def onchange_porcent(self):
        if self.employee_id:
            #self.porcent = self.wage
            contract = self.employee_id.contract_id
            self.amount = self.monto
        else:
            return {}

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self._context
        if ctx.get('order_display', False):
            order = ctx['order_display']
        res = super(salary_line, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
        return res
