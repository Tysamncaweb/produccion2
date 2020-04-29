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
#    Change: jeduardo **  05/07/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para la ficha del trabajador
#
# ##############################################################################################################################################################################

from odoo import fields, models, _ ,exceptions, api
# importando el modulo de regex de python
import re
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta

_DATETIME_FORMAT = "%Y-%m-%d"

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = "hr.employee"

    GRUPO_SANGUINEO = [
        ('O', 'O'),
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB')]

    FACTOR_RH = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo')]

    MARITAL_STATUS = [
        ('S', 'Single'),
        ('C', 'Married'),
        ('U', 'Union Estable de Hecho'),
        ('V', 'Widower'),
        ('D', 'Divorced'),
        ]

    NVEL_EDUCATIVO = [
        ('01', u'Básica'),
        ('02', 'Bachiller'),
        ('03', 'TSU'),
        ('04', 'Universitario'),]

    NACIONALIDAD = [
        ('V','Venezolano'),
        ('E','Extranjero')]


    identification_id_2 = fields.Char('Cedula de Identidad', size=8)
    nationality = fields.Selection(NACIONALIDAD, string="Tipo Documento", required=True)
    rif = fields.Char('Rif', size=15, required=True)
    personal_email = fields.Char('Correo Electronico Personal', size=240, required=True)
    education = fields.Selection(NVEL_EDUCATIVO,'Nivel Educativo')
    profesion_id = fields.Many2one('hr.profesion','Profesion')
    country_birth_id = fields.Many2one('res.country', 'Pais de nacimiento')                                            #PAIS DE NACIMIENTO
    state_id = fields.Many2one('res.country.state', 'Estado de nacimiento') #, domain="[('country_id','=',238)]")    #ESTADO DE NACIMIENTO
    city_id = fields.Many2one('res.country.city', 'Ciudad de nacimiento')                                             #CIUDAD DE NACIMIENTO
    employee_age = fields.Integer("Edad", compute='_calcular_edad')
    marriage_certificate = fields.Boolean('Entrego acta de matrimonio?')
    marital_2 = fields.Selection(MARITAL_STATUS, 'Marital Status')
   # Nro_de_Hijos = fields.Integer('Numero de hijos', size=2)
    grupo_sanguineo = fields.Selection(GRUPO_SANGUINEO, 'Grupo Sangineo')
    factor_rh = fields.Selection(FACTOR_RH, 'Factor RH')
    #INFORMACION DE CONTACTO
    street = fields.Char('Av./Calle', size=50)
    house = fields.Char('Edif. Quinta o Casa', size=50)
    piso = fields.Char('Piso', size=2)
    apto = fields.Char('No. de apartamento.', size=50)
    state_id_res = fields.Many2one('res.country.state', 'Estado', domain="[('country_id','=',238)]")
    city_id_res = fields.Many2one('res.country.city', 'Ciudad')
    telf_hab = fields.Char('Telefono Habitacion', size=12)
    telf_Contacto = fields.Char('Telefono Contacto', size=12)
    e_municipio = fields.Many2one('res.state.municipal','Municipio', size=100)
    e_parroquia = fields.Many2one('res.municipal.parish','Parroquia', size=100)
    code_postal = fields.Char('Código Postal', size=4)
  #  birthday = fields.Many2one('hr.employee','Fecha de Nacimiento')

    def onchange_email_addr(self, email, field):
        res = {}

        if email:
            res = self.validate_email_addrs(email, field)
            if not res:
                raise exceptions.except_orm(_('Advertencia!'), _('El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
        return {'value':res}

    def validate_email_addrs(self, email, field):
        res = {}

        mail_obj = re.compile(r"""
                \b             # comienzo de delimitador de palabra
                [\w.%+-]       # usuario: Cualquier caracter alfanumerico mas los signos (.%+-)
                +@             # seguido de @
                [\w.-]         # dominio: Cualquier caracter alfanumerico mas los signos (.-)
                +\.            # seguido de .
                [a-zA-Z]{2,3}  # dominio de alto nivel: 2 a 6 letras en minúsculas o mayúsculas.
                \b             # fin de delimitador de palabra
                """, re.X)     # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
                               # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if mail_obj.search(email):
            res = {
                field:email
            }
        return res

    def onchange_phone_number(self, phone, field):
        res = {}
        if phone:
            res = self.validate_phone_number(phone, field)
            if not res:
                raise exceptions.except_orm(_('Advertencia!'), _(u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        return {'value':res}

    def validate_phone_number(self, phone, field):
        res = {}

        phone_obj = re.compile(r"""^0\d{3}-\d{7}""", re.X)
                # ^: inicio de linea
                # 0\d{3}: codigo de area: cuantro (4) caracteres numericos comenzando con 0
                # -: seguido de -
                # \d{7}: numero de telefono: cualquier caracter numerico del 0 al 9. 7 numeros
                # re.X: bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if phone_obj.search(phone):
            res = {
                field:phone
            }
        return res

    def validacion_cedula(self,valor):
        if valor.isdigit() == False:
            raise exceptions.except_orm(('Advertencia!'), (u'La Cédula solo debe contener números'))
        if (len(valor) > 8) or (len(valor) < 7) :
            raise exceptions.except_orm(('Advertencia!'), (u'El número de Cédula no puede ser menor que 7 cifras ni mayor a 8.'))
        busqueda = self.env['hr.employee'].search([('identification_id_2','!=', 0)])
        for a in busqueda:
            if a.identification_id_2 == valor:
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'El número de Cédula ya se encuentra registrado'))
        return
    @api.one
    def _fecha_nacimiento_permitida(self, fecha_inicio, fecha_fin):
        if datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(fecha_inicio,
                                                                                         DEFAULT_SERVER_DATE_FORMAT):
            return True
        else:
            return False

    @api.onchange('birthday')
    @api.depends('birthday')
    def _calcular_edad(self):
        for record in self:
            if record.birthday:
                fecha_fin = str(date.today())
                fecha_inicio = record.birthday
                fecha_permitida = self._fecha_nacimiento_permitida(fecha_inicio, fecha_fin)
                if fecha_permitida[0]:
                    antiguedad = relativedelta.relativedelta(datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT),
                                                             datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT))
                    years = antiguedad.years
                    record.employee_age = years
                else:
                    raise exceptions.except_orm('Advertencia',
                                                'La fecha de nacimiento introducida "%s" no puede ser mayor a la actual!' % fecha_inicio)


    def onchange_rif_er(self, field_value):
        res = {}

        if field_value:
            res = self.validate_rif_er(field_value)
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678 o VEE012345678. Por favor intente de nuevo'))
        return {'value':res}

    def validate_rif_er(self, field_value):
        res = {}

        rif_obj = re.compile(r"^VE[V|E][\d]{9}", re.X)
        if rif_obj.search(field_value):
            res = {
                'rif':field_value
            }
        return res

    @api.multi
    def write(self, vals):
        res = {}

        if vals.get('identification_id_2'):
            valor = vals.get('identification_id_2')
            self.validacion_cedula(valor)
        if vals.get('rif'):
            res =self.validate_rif_er(vals.get('rif'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678 o VEE012345678. Por favor intente de nuevo'))
        if vals.get('personal_email'):
            res =self.validate_email_addrs(vals.get('personal_email'),'personal_email')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
        if vals.get('telf_hab'):
            res =self.validate_phone_number(vals.get('telf_hab'),'telf_hab')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        if vals.get('telf_Contacto'):
            res =self.validate_phone_number(vals.get('telf_Contacto'),'telf_Contacto')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        if vals.get('code_postal'):
            res =self.validate_code_postal(vals.get('code_postal'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'El código postal debe contener solo números. Ej. 1000'))

        return super(HrEmployee, self).write(vals)

    @api.model
    def create(self, vals):

        if self._context is None:
            context = {}
            res = {}

        if vals.get('identification_id_2'):
            valor = vals.get('identification_id_2')
            self.validacion_cedula(valor)

        if vals.get('rif'):
            res =self.validate_rif_er(vals.get('rif'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678 o VEE012345678. Por favor intente de nuevo'))
        if vals.get('personal_email'):
            res =self.validate_email_addrs(vals.get('personal_email'),'personal_email')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
        if vals.get('telf_hab'):
            res =self.validate_phone_number(vals.get('telf_hab'),'telf_hab')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        if vals.get('telf_Contacto'):
            res =self.validate_phone_number(vals.get('telf_Contacto'),'telf_Contacto')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))

        if vals.get('code_postal'):
            res =self.validate_code_postal(vals.get('code_postal'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'El código postal debe contener solo números. Ej. 1000'))
        res = super(HrEmployee, self).create(vals)
        return res

    def validate_code_postal(self,valor):
        res = {}
        code_obj = re.compile(r"""^\d{4}""", re.X)
        if code_obj.search(valor):
            res = {
                'code_postal':valor
            }
        return res

HrEmployee()

class hr_profesion(models.Model):

    def _get_profesion_position(self):
        res = []
        for employee in self.env('hr.employee').browse(self):
            if employee.profesion_id:
                res.append(employee.profesion_id.id)
        return res

    _name = "hr.profesion"
    _description = "Profesion Description"

    name = fields.Char('Profesion Name', size=128, required=True, select=True)
        #'employee_ids': fields.one2many('hr.employee', 'profesion_id', 'Employees'),


hr_profesion()


class Employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", size=20)

'''
class hr_ciudad(models.Model):

    def _get_ciudad_position(self):
        res = []
        for employee in self.env('hr.employee').browse(self):
            if employee.city_id:
                res.append(employee.city_id.id)
        return res

    _name = "hr.ciudad"
    _description = "Ciudad Description"

    name= fields.Char('Ciudad Name', size=50, required=True, select=True)
    #employee_ids= fields.One2many('hr.employee', 'city_id', 'Employees')
    estate_id = fields.Many2one('res.country.city', 'Estado')


hr_ciudad()



class hr_municipio(models.Model):

    def _get_municipio_position(self):
        res = []
        for employee in self.env['hr.employee'].browse():
            if employee.municipio_id:
                res.append(employee.municipio_id.id)
        return res

    _name = "hr.municipio"
    _description = "Municipio Description"

    name = fields.Char('Municipio', size=128, required=True, select=True)
   # employee_ids = fields.One2many('hr.employee', 'municipio_id', 'Employees')
    ciudad_id = fields.Many2one('res.country.city', 'Ciudad')
    estate_id = fields.Many2one('res.country.state', 'Estado')


hr_municipio()

class hr_parroquia(models.Model):

    def _get_parroquia_position(self):
        res = []
        for employee in self.env['hr.employee'].browse():
            if employee.parroquia_id:
                res.append(employee.parroquia_id.id)
        return res

    _name = "hr.parroquia"
    _description = "Parroquia Description"

    name = fields.Char('Parroquia', size=128, required=True, select=True)
   # employee_ids = fields.One2many('hr.employee', 'parroquia_id', 'Employees')
    municipio_id = fields.Many2one('hr.municipio', 'Municipio')


hr_parroquia()
'''