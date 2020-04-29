# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta
import re

_logger = logging.getLogger(__name__)

_DATETIME_FORMAT = "%Y-%m-%d"

class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee familiar"

    #Datos Familiares
    son = fields.Boolean(string="Hijos")
    son_ids = fields.One2many('hr.son', 'employee_id', 'Hijos')
    mother_name = fields.Char("Nombre y Apellido de la madre", size=256)
    mother_date = fields.Date("Fecha de Nacimiento de la madre")
    mother_age = fields.Integer("Edad de la madre")
    mother_nationality = fields.Selection([('v.-','V.-'), ('E.-','E.-')], string="Nacionalidad de la madre")
    mother_ci = fields.Char("Cedula de Identidad de la madre", size=8)
    direccion_mom= fields.Char("Dirección", size=100)
    mother_live = fields.Boolean(string="Vive (madre)")
    telf_hab_mother = fields.Char(string="Telefono habitacion", size=12)
    telf_mov_mother = fields.Char(string="Telefono Móvil", size=12)
    father_name = fields.Char("Nombre y Apellido del padre", size=256)
    father_date = fields.Date("Fecha de Nacimiento del padre")
    father_age = fields.Integer("Edad del padre")
    father_nationality = fields.Selection([('v.-','V.-'), ('E.-','E.-')], string="Nacionalidad del padre")
    father_ci = fields.Char("Cedula de Identidad del padre", size=8)
    father_live = fields.Boolean(string="Vive (padre)")
    direccion_father = fields.Char("Dirección", size=100)
    telf_hab_father = fields.Char(string="Telefono habitacion", size=12)
    telf_mov_father = fields.Char(string="Telefono Móvil", size=12)
    spouse = fields.Boolean(string="Conyugue")
    spouse_name = fields.Char("Nombre y Apellido del conyugue", size=256)
    spouse_date = fields.Date("Fecha de Nacimiento del conyugue")
    spouse_age = fields.Integer("Edad del conyugue")
    spouse_nationality = fields.Selection([('V.-','V.-'), ('E.-','E.-')], string="Nacionalidad del conyugue")
    spouse_ci = fields.Char("Cedula de Identidad del conyugue", size=8)
    direccion_spouse= fields.Char("Dirección", size=100)
    telf_hab_spouse = fields.Char(string="Telefono habitacion", size=12)
    telf_mov_spouse = fields.Char(string="Telefono Móvil", size=12)
    total_son = fields.Integer('TOTAL HIJOS', compute='_total_hijos')
    #Calculo y validacion de la edad de la madre

    @api.one
    def _total_hijos(self):
        self.total_son = len(self.son_ids.ids)
        #if not son_ids :
        #    self.total_son= 0

        #else:
        #    if len(self.son_ids.ids):
        #        self.total_son = len(self.son_ids.ids)
        #    else:
        #        self.total_son = 0
        return




    @api.onchange('mother_date')
    def onchange_date_of_birth_mother(self):
        date = self.mother_date
        if date:
            age = self._calculate_date_of_birth(date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.mother_age = age.years
            else:
                self.mother_age = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    #Calculo y validacion de la edad del padre
    @api.onchange('father_date')
    def onchange_date_of_birth_father(self):
        date = self.father_date
        if date:
            age = self._calculate_date_of_birth(date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.father_age = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.father_age = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    #Calculo y validacion de la edad del esposo
    @api.onchange('spouse_date')
    def onchange_date_of_birth_spouse(self):
        date = self.spouse_date
        if date:
            age = self._calculate_date_of_birth(date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.spouse_age = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.spouse_age = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    @api.multi
    def _calculate_date_of_birth(self, value):
            age = 0
            if value:
                #ahora = datetime.now().strftime(_DATETIME_FORMAT)
                ahora = str(date.today())
                age = relativedelta.relativedelta(datetime.strptime(ahora, DEFAULT_SERVER_DATE_FORMAT),
                                                         datetime.strptime(value, DEFAULT_SERVER_DATE_FORMAT))
                #age = relativedelta.relativedelta(datetime.strptime(ahora,_DATETIME_FORMAT), datetime.strptime(value,_DATETIME_FORMAT))
            return age


    def validate_mother_ci(self,valor):
        res = None
        ci_obj = re.compile(r"""^\d{7,15}""", re.X)
        if ci_obj.search(valor):
            res = {'mother_ci': valor}
        return res

    def validate_father_ci(self,valor):
        res = None
        ci_obj = re.compile(r"""^\d{7,15}""", re.X)
        if ci_obj.search(valor):
            res = {'father_ci': valor}
        return res

    def validate_spouse_ci(self,valor):
        res = None
        ci_obj = re.compile(r"""^\d{7,15}""", re.X)
        if ci_obj.search(valor):
            res = {'spouse_ci': valor}
        return res

   # @api.onchange('telf_hab_mother','telf_mov_mother')
    def onchange_phone_number(self, phone, field):
           res = {}
           if phone:
               res = self.validate_phone_number(phone, field)
               if not res:
                   raise exceptions.except_orm(_('Advertencia!'), _(
                       u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
           return {'value': res}

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
                   field: phone
               }
           return res




    def create(self, vals):
        res = {}

        if vals.get('mother_ci'):
            res = self.validate_mother_ci(vals.get('mother_ci'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'La Cédula de la Madre debe contener solo números. Ej. 6231987'))
        if vals.get('father_ci'):
            res = self.validate_father_ci(vals.get('father_ci'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'La Cédula del Padre debe contener solo números. Ej. 7190364'))
        if vals.get('spouse_ci'):
            res = self.validate_spouse_ci(vals.get('spouse_ci'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'La Cédula del Conyuge debe contener solo números. Ej. 16654234'))
        if vals.get('telf_hab_mother'):
            res = self.validate_phone_number(vals.get('telf_hab_mother'),'telf_hab_mother')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                u'El número telefónico tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_mother'):
            res = self.validate_phone_number(vals.get('telf_mov_mother'), 'telf_mov_mother')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
        if vals.get('telf_hab_father'):
            res = self.validate_phone_number(vals.get('telf_hab_father'),'telf_hab_father')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                u'El número telefónico tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_father'):
            res = self.validate_phone_number(vals.get('telf_mov_father'), 'telf_mov_father')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
        if vals.get('telf_hab_spouse'):
            res = self.validate_phone_number(vals.get('telf_hab_spouse'), 'telf_hab_spouse')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_spouse'):
            res = self.validate_phone_number(vals.get('telf_mov_spouse'), 'telf_mov_spouse')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
        return super(Employee, self).create(vals)


    def write(self, vals):
        res = {}
        if vals.get('mother_ci'):
            res = self.validate_mother_ci(vals.get('mother_ci'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'La Cédula de la Madre debe contener solo números. Ej. 6231987'))
        if vals.get('father_ci'):
            res = self.validate_father_ci(vals.get('father_ci'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'La Cédula del Padre debe contener solo números. Ej. 11190364'))
        if vals.get('spouse_ci'):
            res = self.validate_spouse_ci(vals.get('spouse_ci'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'La Cédula del Conyuge debe contener solo números. Ej. 16654234'))
        if vals.get('telf_hab_mother'):
            res = self.validate_phone_number(vals.get('telf_hab_mother'),'telf_hab_mother')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                u'El número telefónico tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_mother'):
            res = self.validate_phone_number(vals.get('telf_mov_mother'), 'telf_mov_mother')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))

        if vals.get('telf_hab_father'):
            res = self.validate_phone_number(vals.get('telf_hab_father'), 'telf_hab_father')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_father'):
            res = self.validate_phone_number(vals.get('telf_mov_father'), 'telf_mov_father')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
        if vals.get('telf_hab_spouse'):
            res = self.validate_phone_number(vals.get('telf_hab_spouse'), 'telf_hab_spouse')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_spouse'):
            res = self.validate_phone_number(vals.get('telf_mov_spouse'), 'telf_mov_spouse')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
        return super(Employee, self).write(vals)



class HrSon(models.Model):
    _name = "hr.son"

    #Datos de los ninos
    name_sons = fields.Char(string="Nombre y Apellido del hijo", size=256)
    sex_sons = fields.Selection([('f','Femenino'), ('m','Masculino')], string="Sexo del hijo")
    date_sons = fields.Date(string="Fecha de Nacimiento del hijo")
    age_sons = fields.Char(string="Edad del hijo", size=10)
    nationality_sons = fields.Selection([('v.-','V.-'), ('E.-','E.-')], string="Nacionalidad del hijo")
    ci_sons = fields.Char("Cedula de identidad del hijo", size=8)
    disability_sons = fields.Boolean(string="Discapacidad (hijo)")
    constancia_inscripcion = fields.Boolean(string="Constancia de Inscripción del hijo")
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")
    telf_hab_son = fields.Char('Telefono Habitacion', size=12)
    telf_mov_son = fields.Char('Telefono Móvil', size=12)
    direccion_son= fields.Char('Dirección', size=100)
    ##  Validacion de numero telefonico

    def onchange_phone_number(self, phone, field):
        res = {}
        if phone:
            res = self.validate_phone_number(phone, field)
            if not res:
                raise exceptions.except_orm(_('Advertencia!'), _(
                    u'El número telefónico tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))
        return {'value': res}

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
                field: phone
            }
        return res

    #Calculo y validacion de la edad de los ninos
    @api.onchange('date_sons')
    def onchange_date_of_birth(self):
        date = self.date_sons
        if date:
            age = self._calculate_date_of_birth(date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.age_sons = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.age_sons = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    @api.multi
    def _calculate_date_of_birth(self, value):
            age = 0
            if value:
                ahora = str(date.today())
                age = relativedelta.relativedelta(datetime.strptime(ahora, DEFAULT_SERVER_DATE_FORMAT),
                                                  datetime.strptime(value, DEFAULT_SERVER_DATE_FORMAT))
            return age

    def validate_ci_sons(self, valor):
        res = None
        ci_obj = re.compile(r"""^\d{7,15}""", re.X)
        if ci_obj.search(valor):
            res = {'ci_sons': valor}
        return res

    def create(self, vals):
        res = {}

        if vals.get('ci_sons'):
            res = self.validate_ci_sons(vals.get('ci_sons'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'La Cédula del hijo debe contener solo números. Ej. 26231987'))

        if vals.get('telf_hab_son'):
            res = self.validate_phone_number(vals.get('telf_hab_son'), 'telf_hab_son')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El Telefono de Habitación del Hijo tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_son'):
            res = self.validate_phone_number(vals.get('telf_mov_son'), 'telf_mov_son')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El Telefono Móvil del Hijo tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))


        return super(HrSon, self).create(vals)



    def write(self, vals):
        res = {}

        if vals.get('ci_sons'):
            res = self.validate_ci_sons(vals.get('ci_sons'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'La Cédula del hijo debe contener solo números. Ej. 26231987'))
        if vals.get('ci_sons'):
            res = self.validate_ci_sons(vals.get('ci_sons'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (u'La Cédula del hijo debe contener solo números. Ej. 26231987'))

        if vals.get('telf_hab_son'):
            res = self.validate_phone_number(vals.get('telf_hab_son'), 'telf_hab_son')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El Telefono de Habitación del Hijo tiene el formato incorrecto. Ej: 0212-4567890. Por favor intente de nuevo'))
        if vals.get('telf_mov_son'):
            res = self.validate_phone_number(vals.get('telf_mov_son'), 'telf_mov_son')
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El Telefono Móvil del Hijo tiene el formato incorrecto. Ej: 0416-4567890. Por favor intente de nuevo'))


        return super(HrSon, self).write(vals)