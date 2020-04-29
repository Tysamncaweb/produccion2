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

from odoo import fields, models, api, exceptions
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, time, timedelta
import time
#import pytz
import os
import re

#Toda clase en Odoo finalmente representa un tabla en la base de datos POSTGRESQ
class calling(models.Model):
    _name = 'calling'
#Con este name es se creara una tabla en base de datos en caso de un (.), se sustituye por un (_)
    RELATION_VALUES = [('father', 'Padre'),
                       ('mother', 'Madre'),
                       ('son', 'Hijo'),
                       ('spouse', 'Conyuge'),
                       ('own', 'Titular'),
                       ('nephews', 'Sobrino'),
                       ('inlaws','Suegro'),
                       ('grandchild','Nieto'),
                       ('grandparent','Abuelo'),
                       ('brother','Hermano')]

    GENDER = [('female','Femenino'),
              ('male','Masculino')]

    PATIENT_TYPE = [('owner','Owner'),
                    ('assignee','Assignee')]

    STATES = [('active','Activo'),
              ('progress', 'En Progreso'),
              ('complete', 'Completado'),
              ('cancel','Cancelado'),
              ('mobilization','Movilización')]

    COLOR_CODES = [('yellow','Amarillo'),
                   ('green', 'Verde'),
                   ('orange','Rojo'),
                   ('black','Negro')]

    def _get_user_id(self):
        user_id = self.env['hr.employee'].search([('user_id','=',self._uid)])
        if user_id:
            return user_id
        else:
            return None

    calling_headquarter = fields.Many2one('headquarter', 'Calling Headquarter')
    calling_user = fields.Many2one('hr.employee','Calling User')#, default=_get_user_id)#, required=True, default=lambda self: self.env.uid)
    calling_date = fields.Date('Calling Date', default=time.strftime('%Y-%m-%d'))
    calling_time = fields.Float('Calling Hour')
    #calling_wait_time =
    calling_end_time = fields.Float('Calling Hour End')
    calling_duration = fields.Float('Calling Duration')
    calling_collective = fields.Many2one('collective', 'Calling Collective')
    calling_client = fields.Many2one('res.partner', 'Calling Client',readonly=False)
    calling_reason = fields.Char('Calling Reason', size=250)
    patient_owner_id = fields.Many2one('patient', 'Patient Owner Id', domain=[('patient_relationship','like','own')])
    owner_patient = fields.Boolean(string='Es Paciente',default=False)
    independent_patient = fields.Boolean(string='Es Particular',default=False)
    patient_owner_name = fields.Char('Patient Owner Name', size=60, related='patient_owner_id.name')
    patient_name = fields.Many2one('patient', 'Patient')
    patient_id = fields.Char('Patient Identification', size=10, related='patient_name.patient_id')
    owner_id = fields.Char('Owner Identification', size=10, related='patient_owner_id.patient_id')
    patient_address = fields.Char('Patient Address', size=250)#Debe ser un select
    #patient_address_state = fields.Many2one('states', 'State')
    patient_address_state = fields.Many2one('res.country.state', 'State', domain="[('country_id','=',238)]")
    #patient_address_parish = fields.Many2one('parish', 'Parish')
    patient_address_parish = fields.Many2one('res.municipal.parish', 'Parish')
    patient_municipal_ids = fields.Char('Municipal Ids')
    calling_transport = fields.Boolean()
    #calling_transport_from = fields.Char('Calling Transport From',size=250)
    #calling_transport_to = fields.Char('Calling Transport To',size=250)
    patient_phone = fields.Char('patient Phone Number', size=100)#, related='patient_name.patient_phone')
    calling_code = fields.Selection(COLOR_CODES, 'Calling Code')
    calling_service = fields.Many2one('service', 'Calling Service')
    calling_service_type = fields.Many2one('service.type', 'Calling Service Type')
    #calling_additional_service_type = fields.Many2one('additional.service.type', 'Calling Additional Service Type')
    #calling_scheduled_transport_date = fields.Date('Schedule transport dat')
    calling_comments = fields.Text('Calling Comments', size=500)
    calling_time_wait = fields.Char('Wait Time', size=100)
    calling_user_auth = fields.Char('calling user', size=60)
    calling_form_number = fields.Char('Form Number', size=13)
    calling_diagnosis = fields.Many2one('diagnosis', 'Calling Diagnosis')
    calling_treatment = fields.Many2one('treatment', 'Calling Treatment')
    calling_number_key = fields.Char('Calling Number Key', size=9)
    #calling_commitment = fields.Char('Calling Commitment', size=10)
    patient_relation = fields.Selection(RELATION_VALUES, 'Patient Relation')
    patient_age = fields.Char('Patient Age', size=3)
    patient_gender = fields.Selection(GENDER, 'Patient Gender')
    patient_type = fields.Selection(PATIENT_TYPE, 'Patient Assignee')
    patient_precedent = fields.Char('Patient Precedent', size=250)
    service_type = fields.Many2one('service', 'Service Type')
    state = fields.Selection(STATES, default='active')
    #state = fields.Selection([('draft', 'Borrador'), ('active', 'Activo')], default='draft') Estaba asi desde la version 8
    calling_service_time = fields.Float('Service time')
    calling_medical_history = fields.Char("Medical history", size=250)
    calling_service_unit = fields.Many2one("fleet.vehicle", "Service unit")
    calling_medical_treatment = fields.Char("Medical treatment", size=250)
    calling_medical_rest = fields.Boolean()
    calling_medical_rest_days = fields.Integer("Medical rest days")
    calling_service_atendant = fields.Selection([('metromed','Metromed'),('others','Tercerizados')], 'Calling Service Atendant')
    calling_service_atendant_others = fields.Many2one('atendantothers','Calling Service Atendant Others')
    quotation_count = fields.Integer(string='Presupuesto')
    quotation_number = fields.Many2one('sale.order')
    service_direct = fields.Boolean(string='Servicio Directo',default=False)


    @api.onchange('calling_user')
    def _hora_inicio(self):
        os.environ['TZ'] = 'America/Caracas'
        time.tzset()
        horas = float(time.strftime('%H'))
        minutos = float(time.strftime('%M'))
        segundos = float(time.strftime('%S'))
        hora = (horas + (minutos / 60))
        self.calling_time = hora

    @api.onchange('calling_client')
    def _clear_hora_inicio(self):
        self.calling_collective = None

#    @api.onchange('calling_collective')#sirve
#    def _get_client_name(self):
#        if self.calling_collective:
#            partner_obj = self.calling_collective.collective_client_id
#            name_client = partner_obj.display_name
#            self.calling_client = name_client
#            collective_id = self.calling_collective.id
#            #self.patient_owner_id = 0
#            domain = [('patient_collective','=', int(collective_id))]
#            active_partner = partner_obj.active_client
#            if not active_partner:
#                return {'domain': {'patient_owner_id': domain},
#                         'warning': {'title': "Advertencia!",
#                                    'message': "Cliente inactivo. No se le puede prestar el servicio.El Operador del Call Center"
#                                                                                  "debe indicarle al solicitante del servicio que se comunique con el Departamento de"
#                                                                                  "Comercialización de la empresa Metromed, C.A., el cual le suministrará mayor"
#                                                                                  "información al respecto, a través de los números telefónicos: 0212-7519886 y 7511033"}}
#
#            return {'domain': {'patient_owner_id': domain}}
#        else:
#            return None


    @api.onchange('patient_owner_id')
    def _get_patients(self):
        if self.patient_owner_id:
            patient_id = self.patient_owner_id.id
            domain = [('patient_owner_id','=',patient_id)]
            #self.patient_name = 0
            self.patient_phone = self.patient_owner_id.patient_phone
            return {'domain': {'patient_name': domain}}
        else:
            return False

    @api.onchange('patient_name')
    def _get_patient_data(self):
        if self.patient_name:
            patient_relationship = self.patient_name.patient_relationship
            patient_gender = self.patient_name.patient_gender
            self.patient_relation = patient_relationship
            self.patient_gender = patient_gender
        else:
            return False

    @api.onchange('owner_patient')
    def _get_fiel_boool(self):
        if self.owner_patient and self.patient_owner_id:
            self.patient_name = self.patient_owner_id
        else:
            return False

    @api.onchange('patient_address_state')
    def _get_parish(self):
        local_ids = ''
        self.patient_address_parish = None
        if self.patient_address_state:
            state_id = self.patient_address_state
            # self.patient_address_parish = 0
            municipal_id = self.env['res.state.municipal'].search([('res_country_state_id','=',state_id.id)])
            if municipal_id:
                #proceso que obtien los ids de los municipios y los coloca en una cadena separada por comas
                muni_ids = [muni.id for muni in municipal_id]
                parish_ids = self.env['res.municipal.parish'].search([('res_state_municipal_id', 'in', muni_ids)])
                local_ids = [parish.id for parish in parish_ids]
            else:
                local_ids = []

            self.patient_municipal_ids = local_ids
            domain = [('id', 'in', local_ids)]
            return {'domain': {'patient_address_parish': domain}}
        else:
            return False


    """@api.onchange('calling_service')
    def _get_service_type(self):
        if self.calling_service:
            service_id = self.calling_service
            self.calling_service_type = 0
            if self.calling_service.id != 2:
                self.calling_transport = False
                self.calling_transport_from = ""
                self.calling_transport_to = ""
            domain = [('service_id', '=', int(service_id))]
            return {'domain': {'calling_service_type': domain}}
        else:
            return False"""


    """@api.onchange('calling_service_type')
    def _get_additional_service_type(self):
        if self.calling_service_type:
            service_type_id = self.calling_service_type
            self.calling_additional_service_type = 0
            domain = [('service_type_id', '=', int(service_type_id))]
            return {'domain': {'calling_additional_service_type': domain}}
        else:
            return False"""

    # Funcion para el calculo de la edad del paciente de forma automaica

    #@api.one#Esta comentado porque genera un error
    @api.onchange('patient_name')
    @api.depends('patient_name')
    def _calcular_edad(self):
        for record in self:
            if self.patient_name and self.patient_name.patient_birth_date:
                patient_birth_date = self.patient_name.patient_birth_date
                fecha_fin = str(date.today())
                fecha_inicio = patient_birth_date
                antiguedad = relativedelta(datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT),
                                                         datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT))
                years = antiguedad.years
                self.patient_age = years

    @api.one
    def confirm_calling(self):
        if not self.calling_end_time:
            os.environ['TZ'] = 'America/Caracas'
            time.tzset()
            horas = float(time.strftime('%H'))
            minutos = float(time.strftime('%M'))
            segundos = float(time.strftime('%S'))
            hora = (horas + (minutos / 60))
            dif = (hora - self.calling_time)
            self.calling_end_time = hora
            self.calling_duration = dif
            self.write({'state':'progress'})
        return True

    #############
    @api.one
    def complete_calling(self):
        if self.service_direct and not self.quotation_number and ( self.calling_service_type.id ==1 or self.calling_service_type.id==3 or self.calling_service_type.id==4 or self.calling_service_type.id==5):
                raise exceptions.except_orm(('Advertencia!'), (
                    u"El tipo de servicio seleccionado requiere que se cree un presupuesto. "
                    u"Presione el botón Presupuesto para continuar con el registro."))
        if self.service_direct and ( self.calling_service_type.id ==2 or self.calling_service_type.id==6 or self.calling_service_type.id==7 or self.calling_service_type.id==8):
            raise exceptions.except_orm(('Advertencia!'), (
                u"El tipo de servicio seleccionado no es un servicio directo. "))
        return self.write({'state':'complete'})

    @api.one
    def mobilization_calling(self):
        self.write({'state': "mobilization"})
        return True

    @api.one
    def cancel_calling(self):
        self.write({'state': "cancel"})
        return True

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

    def _validate_form_number(self, valor):
        res = {}
        warn = {}
        form_obj = re.compile(r"""^\d+$""", re.X)
        if form_obj.search(valor):
            #validacion de la cedula Repetida
            res = {'calling_form_number':valor,'warning': warn}
            form_id = self.search([('calling_form_number', '=', valor)])
            if form_id:
                for form_number in self.browse(form_id):
                    warn = {'title':('Advertencia!'),'message':(u'El número de planilla "%s" ya se encuntra registrado') % (valor)}
                    return {'warning':warn}
        return res

    # Sobreescritura del metodo create
    @api.model
    def create(self, values):
        if values:
             """if values.get('patient_phone'):
                res = self._validate_patient_phone(values['patient_phone'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'), (u'El número telefónico tiene un formato incorrecto.\nEj: 0123-4567890.\nPor favor intente de nuevo'))"""
             if values.get('calling_form_number'):
                res = self.env['calling']._validate_form_number(values['calling_form_number'])
                if res:
                    if res.get('warning'):
                        raise exceptions.except_orm(('Advertencia!'),(u'El número de planilla "%s" ya se encuentra registrado') % (values['patient_id']))
                else:
                    raise exceptions.except_orm(('Advertencia!'),(u'El número de planilla debe contener solo números.'))

             #DESCOMENTAR SI EL CLIENTE QUE TIENE COLECTIVOS ASOCIADOS DEBA SER SELECCIONADO DE FORMA OBLIGATORIA
             #if values.get('calling_client'):
             #    calling_collective_obj = self.env['collective']
             #    calling_collective_ids = calling_collective_obj.search([('collective_client_id','=',values.get('calling_client'))])
             #    if calling_collective_ids:
             #        if not values.get('calling_collective', False):
             #           raise exceptions.except_orm(('Advertencia!'), (u"Cliente seleccionado, posee colectivos asociados y Ud. no ha seleccionado ninguno. "
             #                                                                     "Por favor seleccione un colectivo para éste cliente."))

             """if not values.get('calling_user'):
                 raise exceptions.except_orm(('Advertencia!'), (
                     u"Debe seleccionar el teleoperador que está registrando la llamada. "))"""
             #else:
                 #user_id = self.env['hr.employee'].search([('user_id', '=', self._uid)])
                 #if user_id:
                 #   if values.get('calling_user') != user_id.id:
                 #       raise exceptions.except_orm(('Advertencia!'), (u"El teleoperador seleccionado no corresponde con el usuario que está registrando la llamada. "
                 #        u"Por favor verifique que el teleoperador y el usuario sean el mismo."))
                 #else:
                 #    raise exceptions.except_orm(('Advertencia!'), (u"El teleoperador no ha sido asociado con el usuario de la aplicación. "
                 #        u"Por favor verifique que el operador esté asociado al usuario del ERP."))

        record = super(calling, self).create(values)
        return record

    # Sobreescritura del metodo create
    @api.multi
    def write(self, values):
        if values:
            """if values.get('patient_phone'):
                res = self._validate_patient_phone(values['patient_phone'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'), (u'El número telefónico tiene un formato incorrecto.\nEj: 0123-4567890.\nPor favor intente de nuevo'))"""
            """if values.get('calling_form_number'):
                res = self.env['calling']._validate_form_number(values['calling_form_number'])
                if not res:
                    raise exceptions.except_orm(('Advertencia!'), (u'El número de planilla debe contener solo números.'))"""
            """if values.get('calling_user') and values.get('calling_user')== None :
                raise exceptions.except_orm(('Advertencia!'), (
                    u"Debe seleccionar el teleoperador que está registrando la llamada. "))"""
            #if values.get('calling_client'):
            #    calling_collective_id_int = values.get('calling_collective')
            #    collective_obj = self.env['collective'].browse(calling_collective_id_int)
            #    collective_id = collective_obj.collective_client_id
            #    partner_name = collective_id.active_client
            #    if not partner_name:
            #        raise exceptions.except_orm(('Advertencia!'), (u"Cliente inactivo. No se le puede prestar el servicio.El Operador del Call Center "
            #                                                                     "debe indicarle al solicitante del servicio que se comunique con el Departamento de "
            #                                                                     "Comercialización de la empresa Metromed, C.A., el cual le suministrará mayor "
            #                                                                     "información al respecto, a través de los números telefónicos: 0212-7519886 y 7511033"))

            # DESCOMENTAR SI EL CLIENTE QUE TIENE COLECTIVOS ASOCIADOS DEBA SER SELECCIONADO DE FORMA OBLIGATORIA
            # if values.get('calling_client'):
            #    calling_collective_obj = self.env['collective']
            #    calling_collective_ids = calling_collective_obj.search([('collective_client_id','=',values.get('calling_client'))])
            #    if calling_collective_ids:
            #        if not values.get('calling_collective', False):
            #           raise exceptions.except_orm(('Advertencia!'), (u"Cliente seleccionado, posee colectivos asociados y Ud. no ha seleccionado ninguno. "
            #                                                                     "Por favor seleccione un colectivo para éste cliente."))

            #if values.get('calling_user', False):
                #user_id = self.env['hr.employee'].search([('user_id', '=', self._uid)])
                #if user_id:
                #    if values.get('calling_user') != user_id.id:
                #        raise exceptions.except_orm(('Advertencia!'), (
                #        u"El teleoperador seleccionado no corresponde con el usuario que está registrando la llamada. "
                #        u"Por favor verifique que el teleoperador y el usuario sean el mismo."))
                #else:
                #    raise exceptions.except_orm(('Advertencia!'), (
                #    u"El teleoperador no ha sido asociado con el usuario de la aplicación. "
                #    u"Por favor verifique que el operador esté asociado al usuario del ERP."))

        record = super(calling, self).write(values)
        return record

    @api.multi
    def foo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_view_reload',
        }


class additionalServiceType(models.Model):
    _name = 'additional.service.type'
    _rec_name = 'additional_service_type_name'

    service_type_id = fields.Many2one('service.type', 'Service_type_id')
    additional_service_type_name = fields.Char('Additional Service Type Name', size=250)
    short_additional_service_type_name = fields.Char('Short Service Name', size=3)

class serviceType(models.Model):
    _name = 'service.type'
    _rec_name = 'service_type_name'

    #service_id = fields.Many2one('service', 'Service Id')
    service_type_name = fields.Char('Service Type Name', size=250)
    short_service_type_name = fields.Char('Short Service Name', size=3)

class service(models.Model):
    _name = 'service'
    _rec_name = 'service_name'

    service_name = fields.Char('Service Name', size=250)

class atendantothers(models.Model):
    _name = 'atendantothers'

    name = fields.Char('Nombre',size=250)

class headquarter(models.Model):
    _name = 'headquarter'

    name = fields.Char('Headquarter',size=20)
    description = fields.Text('Headquarter Description', size=250)
    city = fields.Char('Headquarter City',size=20)

class parish(models.Model):
    _name = 'parish'

    name = fields.Char('Parish', size=50)
    state_id = fields.Many2one('states', 'State Id')

class states(models.Model):
    _name = 'states'

    name = fields.Char('State', size=50)

class vehicle_unit(models.Model):
    _name = 'vehicle.unit'

    unit_number = fields.Char('Vehicle Unit', size=7)
    unit_state = fields.Boolean('Unit Sate')
    unit_driver = fields.Many2one('client', 'Client')

class diagnosis(models.Model):
    _name = 'diagnosis'
    _rec_name = 'diagnosis_name'

    diagnosis_name = fields.Char('Diagnosis Name', size=100)
    diagnosis_description = fields.Text('Diagnosis Description')

class treatment(models.Model):
    _name = 'treatment'

    treatment_number = fields.Char('treatment Number', size=10)
    treatment_description = fields.Text('treatment Description', size=500)
