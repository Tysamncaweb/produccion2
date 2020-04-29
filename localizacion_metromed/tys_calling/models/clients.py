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
##############################################################################

from odoo import fields, models, api, _ , exceptions
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import *
#from time import *
import re

class patient(models.Model):
    _name = 'patient'
    _rec_name = 'name'


    """
    @api.multi
   def name_get(self):
        #if self._context is None:
        #    context = {}
        res = []
        patients = self.browse(self.ids)
        for patient in patients:
            if self._context.get('show_patient',False):
                res.append((patient.id, patient.patient_id))
            else:
                res.append((patient.id, patient.name))
        return res
"""
    GENDER = [('female', 'Femenino'),
              ('male', 'Masculino')]

    RELATIONSHIP = [('father', 'Padre'),
                    ('mother', 'Madre'),
                    ('son', 'Hijo'),
                    ('spouse', 'Conyuge'),
                    ('own', 'Titular'),
                    ('nephews', 'Sobrino'),
                    ('inlaws','Suegro'),
                    ('grandchild','Nieto'),
                    ('grandparent','Abuelo'),
                    ('brother','Hermano')]

    #expresion regular digitos /^[0-9]$/

    name = fields.Char('Nombre del paciente', size=60)
    patient_id = fields.Char('Cedula del paciente', size=10)

    patient_owner_id = fields.Many2one('patient', 'Titular', domain=[('patient_relationship', 'like', 'own')])
    patient_collective = fields.Many2one('collective', 'Colectivo del paciente')
    patient_collective_certificate = fields.Char('Certifiacdo', size=50)
    patient_birth_date = fields.Date('Fecha de Nacimiento')
    patient_age = fields.Char(string='Edad', compute='_calcular_edad', readonly=0)
    patient_phone = fields.Char('Numero de telefono del paciente', size=100)
    patient_address = fields.Char('Direccion del paciente', size=250)
    patient_vip = fields.Boolean('¿Paciente VIP?')

    patient_active = fields.Boolean('¿Paciente Activo?', default=True)
    patient_gender = fields.Selection(GENDER, 'Genero del paciente')
    patient_relationship = fields.Selection(RELATIONSHIP, 'Parentesco', default='own')
    #patient_is_owner = fields.Boolean('¿Es titular?')

    #Prueba de nombre de cliente
    patient_client = fields.Char(string="Cliente", compute='_obtener_cliente', readonly=True)
    particular = fields.Boolean(string='Es Particular',default=False)
    patient_client = fields.Many2one('res.partner', 'Cliente', readonly=False)

    @api.one
    def _fecha_nacimiento_permitida(self, fecha_inicio, fecha_fin):
        if datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT):
            return True
        else:
            return False

    @api.onchange('patient_id')
    def _deafult_certificate(self):
        if self.patient_id:
            if len(self.patient_owner_id) == 0:
                self.patient_collective_certificate = self.patient_id

    #Funcion para el calculo de la edad del paciente de forma automaica
    #@api.one#Esta comentado porque genera un error
    @api.onchange('patient_birth_date')#Despues por aqui
    @api.depends('patient_birth_date')
    def _calcular_edad(self):
        for record in self:
            if record.patient_birth_date:
                fecha_fin = str(date.today())
                fecha_inicio = record.patient_birth_date
                fecha_permitida = self._fecha_nacimiento_permitida(fecha_inicio, fecha_fin)
                if fecha_permitida[0]:
                    antiguedad = relativedelta.relativedelta(datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT),
                                                             datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT))
                    years = antiguedad.years
                    record.patient_age = years
                else:
                    raise exceptions.except_orm('Advertencia', 'La fecha de nacimiento introducida "%s" no puede ser mayor a la actual!' % fecha_inicio)


    #Funcion para precargar los datos del paciente titular en caso de que existan
    #@api.one#Esta comentado porque genera un error
    @api.onchange('patient_owner_id')#primero por aqui
    def _buscar_datos_titular(self):
        for record in self:
            if self.patient_owner_id:
                id = int(self.patient_owner_id)
                self.env.cr.execute('SELECT patient_phone, patient_address, patient_active, patient_collective, patient_collective_certificate FROM patient WHERE id=%d' % (id))
                rows = self.env.cr.fetchall()
                if rows:
                    self.patient_phone = rows[0][0]
                    self.patient_address = rows[0][1]
                    self.patient_active = rows[0][2]
                    self.patient_collective = rows[0][3]
                    self.patient_collective_certificate = rows[0][4]

    @api.one
    def _obtener_cliente(self):
        """for record in self:
            if self.id:
                id = int(self.id)
                #self.env.cr.execute('SELECT client_name FROM patient JOIN collective ON patient.patient_collective=collective.id JOIN client ON collective.collective_client_id=client.id WHERE patient.id=%d' % (id))
                self.env.cr.execute('SELECT display_name FROM patient as p JOIN collective as c ON p.patient_collective=c.id JOIN res_partner as rp ON c.collective_client_id=rp.id WHERE p.id=%d' % (id))
                rows = self.env.cr.fetchall()
                if rows:
                    self.patient_client = rows[0][0]"""
        patient_client = self.patient_collective.collective_client_id.display_name
    """
    Se comentó esta sección debido a que la sentencia SQL, lo que hace es buscar entre las tablas los nombres registrados en el
    atributo display name.
"""

    def _validate_patient_id(self, valor):
        res = {}
        warn = {}
        ci_obj = re.compile(r"""^\d{7,15}$""", re.X)
        if ci_obj.search(valor):
            #validacion de la cedula Repetida
            res = {'patient_id':valor,'warning':warn}
            identification_id = self.search([('patient_id', '=', valor)])
            if identification_id:
                for patient in self.browse(identification_id):
                    warn = {'title':('Advertencia!'),'message':(u'El paciente ya se encuentra registrado. Cédula: %s') % (valor)}
                    return {'warning':warn}
                    #raise exceptions.except_orm(('Advertencia!'),(u'El paciente ya se encuentra registrado. Cédula: %s') % (valor))
        return res

    def _validate_patient_name(self, valor):
        res = {}
        name_obj = re.compile(u"""^[a-zA-ZñÑáÁéÉíÍóÓúÚ]+[a-zA-ZñÑáÁéÉíÍóÓúÚ\s,]+[a-zA-ZñÑáÁéÉíÍóÓúÚ]+$""", re.X)
        if name_obj.search(valor):
            res = {'name':valor}
        return res

    def _validate_patient_phone(self, valor):
        res = {}
        phone_obj = re.compile(r"""^0\d{3}-\d{7}$""", re.X)
                # ^: inicio de linea
                # 0\d{3}: codigo de area: cuantro (4) caracteres numericos comenzando con 0
                # -: seguido de -
                # \d{7}: numero de telefono: cualquier caracter numerico del 0 al 9. 7 numeros
                # re.X: bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if phone_obj.search(valor):
            res = {
                'patient_phone':valor
            }
        return res


    #Sobreescritura del metodo create
    @api.model
    def create(self, values):
        if values:
            if values.get('patient_id'):
                res = self.env['patient']._validate_patient_id(values['patient_id'])
                if res:
                    if res.get('warning'):
                        raise exceptions.except_orm(('Advertencia!'),(u'El paciente ya se encuentra registrado. Cédula: %s') % (values['patient_id']))
                #else:
                #    raise exceptions.except_orm(('Advertencia!'),(u'La cédula de identidad debe contener solo números.\nEj. 19763505'))
            if values.get('name'):
                res = self._validate_patient_name(values['name'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'),(u'El nombre no puede contener números ni caracteres especiales,\n',
                                                           u'tampoco puede iniciar ni terminar con espacioes en blanco'))
            """if values.get('patient_phone'):
                res = self._validate_patient_phone(values['patient_phone'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'),(u'El número telefónico tiene un formato incorrecto.\nEj: 0123-4567890.\nPor favor intente de nuevo'))"""
            if values.get('patient_relationship'):
                if not values.get('patient_owner_id'):
                    if values['patient_relationship'] != 'own':
                        raise exceptions.except_orm(('Advertencia!'),(u'Debe asignar la cédula del titular poder seleccionar este parentesco'))
                else:
                    if values['patient_relationship'] == 'own':
                        raise exceptions.except_orm(('Advertencia!'),('El paciente no puede ser el titular si ya es dependiente'))
            if values.get('patient_birth_date', False):
                fecha_fin = str(date.today())
                fecha_inicio = values['patient_birth_date']
                if datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT):
                    pass
                else:
                    raise exceptions.except_orm(('Advertencia!'), (
                    'La fecha de nacimiento introducida "%s" no puede ser mayor a la actual!' % fecha_inicio))
            record = super(patient, self).create(values)
            return record


    #sobreescritura del metodo write
    @api.multi
    def write(self, values):
        #if values and values.get('patient_birth_date', False):
        if values:
            if values.get('patient_id'):
                res = self.env['patient']._validate_patient_id(values['patient_id'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'),(u'La cédula de identidad debe contener solo números.\nEj. 19763505'))
            if values.get('name'):
                res = self._validate_patient_name(values['name'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'),(u'El nombre no puede contener números ni caracteres especiales'))
            """if values.get('patient_phone'):
                res = self._validate_patient_phone(values['patient_phone'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'),(u'El número telefónico tiene un formato incorrecto.\nEj: 0123-4567890.\nPor favor intente de nuevo'))"""
            if values.get('patient_relationship'):
                if not values.get('patient_owner_id'):
                    if values['patient_relationship'] != 'own':
                        raise exceptions.except_orm(('Advertencia!'),(u'Debe asignar la cédula del titular poder seleccionar este parentesco'))
                else:
                    if values['patient_relationship'] == 'own':
                        raise exceptions.except_orm(('Advertencia!'),('El paciente no puede ser el titular si ya es dependiente'))
            if values.get('patient_birth_date', False):
                fecha_fin = str(date.today())
                fecha_inicio = values['patient_birth_date']
                if datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT):
                    pass
                else:
                    raise exceptions.except_orm(('Advertencia!'), (
                    'La fecha de nacimiento introducida "%s" no puede ser mayor a la actual!' % fecha_inicio))
        record = super(patient, self).write(values)
        return record



class collecive(models.Model):
    _name = 'collective'
    _rec_name = 'collective_name'

    collective_name = fields.Char('Nombre del colectivo', size=250)
    collective_client_id = fields.Many2one('res.partner','Id del cliente', domain=[('customer','=',1)])

class client(models.Model):
    _name = 'client'
    _rec_name ='client_name'

    client_name = fields.Char('Nombre del cliente', size=60)
