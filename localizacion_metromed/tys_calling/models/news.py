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
#    GNU Affero General Public License for more detailsh.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.p
#

##############################################################################

from odoo import fields, models, api
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import re
from odoo.osv import osv
from datetime import *

class news(models.Model):
    _name = 'news'

    news_date = fields.Date('Register date')
    group_leader_id = fields.Many2one('hr.employee', 'Group leader')
    supervisor_id = fields.Many2one('hr.employee', 'Supervisor')
    headquarter_id = fields.Many2one('headquarter', 'Headquarter')
    news = fields.Text('News')
    #guard_group_out = fields.Selection([('a','A')], string='Guard group out')
    guard_group_out = fields.Many2one('guard.groups', 'Guard group out')
    guard_members_out_attendant = fields.Many2many('hr.employee', 'users_members_guard_out_attendant', 'user_out_id', 'group_out_id', string='Guard members out attendant')
    guard_members_out_no_attendant = fields.Many2many('hr.employee', 'users_members_guard_out_no_attendant', 'user_out_id','group_out_id', string='Guard members out no attendant')
    guard_group_in = fields.Many2one('guard.groups', 'Guard group in')
    guard_members_in_attendant = fields.Many2many('hr.employee', 'users_members_guard_in_attendant', 'user_in_id', 'group_in_id', string='Guard members in attendant')
    guard_members_in_no_attendant = fields.Many2many('hr.employee', 'users_members_guard_in_no_attendant','user_in_id', 'group_in_id',string='Guard members in no attendant')
    crew_medic = fields.Char('Crew medic', size=250)#'Crew medic')
    crew_medic2 = fields.Char('Crew medic', size=250)
    crew_medic3 = fields.Char('Crew medic', size=250)
    """crew_paramedic = fields.Many2one('hr.employee', 'Crew paramedic')
    crew_paramedic2 = fields.Many2one('hr.employee', 'Crew paramedic')
    crew_paramedic3 = fields.Many2one('hr.employee', 'Crew paramedic')
    crew_driver = fields.Many2one('hr.employee', 'Crew driver')
    crew_driver2 = fields.Many2one('hr.employee', 'Crew driver')
    crew_driver3 = fields.Many2one('hr.employee', 'Crew driver')"""
    crew_medic_substitute = fields.Char('Crew medic substitute', size=250)#'Crew medic substitute')
    crew_medic_substitute2 = fields.Char('Crew medic substitute', size=250)
    crew_medic_substitute3 = fields.Char('Crew medic substitute', size=250)
    """crew_paramedic_substitute = fields.Many2one('hr.employee', 'Crew paramedic substitute')
    crew_paramedic_substitute2 = fields.Many2one('hr.employee', 'Crew paramedic substitute')
    crew_paramedic_substitute3 = fields.Many2one('hr.employee', 'Crew paramedic substitute')
    crew_driver_substitute = fields.Many2one('hr.employee', 'Crew driver substitute')
    crew_driver_substitute2 = fields.Many2one('hr.employee', 'Crew driver substitute')
    crew_driver_substitute3 = fields.Many2one('hr.employee', 'Crew driver substitute')"""
    news_comments = fields.Text('Calling Comments', size=500)
    unit_id = fields.Many2one('fleet.vehicle', 'Unit')
    unit_id2 = fields.Many2one('fleet.vehicle', 'Unit')
    unit_id3 = fields.Many2one('fleet.vehicle', 'Unit')
    mileage = fields.Integer('Kilometer')
    mileage2 = fields.Integer('Kilometer')
    mileage3 = fields.Integer('Kilometer')
    news_members_out_line = fields.One2many('news.members.out.line', 'news_id', string='News lines')
    news_members_in_line = fields.One2many('news.members.in.line', 'news_id', string='News lines')

    @api.onchange('guard_group_out')
    def _out_groups_filter(self):
        if self.guard_group_out:
            group_id = self.guard_group_out
            #self.guard_group_in = 0
            domain = [('id','!=',int(group_id))]
            return {'domain':{'guard_group_in': domain}}
        else:
            return False

    @api.onchange('guard_group_out')
    def _out_groups_members_filter(self):
        if self.guard_group_out:
            news_members_out_line = self.env['news.members.out.line']
            group_id = self.guard_group_out.id
            search_var = self.env['guard.group.members.line'].search([('guard_group_id','=',group_id)])
            if search_var:
                res = []
                for i in search_var:
                    res.append((0,0,{'member_id':i.member_id}))
                self.news_members_out_line = res
            else:
                self.news_members_out_line = [(2, 2)]

            #self.news_members_out_line = [(0,0,{'member_id':1}),(0,0,{'member_id':25})]
            #for i in self.news_members_out_line:
            #    i.member_id = 1
            group_id = self.guard_group_out
            self.env.cr.execute('SELECT ru.id, gg.name FROM guard_groups as gg JOIN guard_group_members as ggm ' \
                                'ON gg.id = ggm.guard_group_id JOIN guard_group_members_line as ggml ' \
                                'ON ggm.id = ggml.guard_group_id JOIN res_users as ru ON ru.id = ggml.member_id ' \
                                'where gg.id = %d' % (group_id))
            rows = self.env.cr.fetchall()
            if rows:
                domain_group = ['|']
                for file in rows:
                    domain_group.append(('id', '=', int(file[0])))
                #print domain_group
                return {'domain':{'news_members_out_line':domain_group}}

    @api.onchange('guard_group_in')
    def _in_groups_filter(self):
        if self.guard_group_in:
            group_id = self.guard_group_in
            #self.guard_group_out = 0
            domain = [('id','!=',int(group_id))]
            return {'domain':{'guard_group_out': domain}}
        else:
            return False

    @api.onchange('guard_group_in')
    def _in_groups_members_filter(self):
        if self.guard_group_in:
            news_members_in_line = self.env['news.members.in.line']
            group_id = self.guard_group_in.id
            search_var = self.env['guard.group.members.line'].search([('guard_group_id', '=', group_id)])
            if search_var:
                res = []
                for i in search_var:
                    res.append((0, 0, {'member_id': i.member_id}))
                self.news_members_in_line = res
            else:
                self.news_members_in_line = [(2, 2)]

            # self.news_members_in_line = [(0,0,{'member_id':1}),(0,0,{'member_id':25})]
            # for i in self.news_members_in_line:
            #    i.member_id = 1
            group_id = self.guard_group_in
            self.env.cr.execute('SELECT ru.id, gg.name FROM guard_groups as gg JOIN guard_group_members as ggm ' \
                                'ON gg.id = ggm.guard_group_id JOIN guard_group_members_line as ggml ' \
                                'ON ggm.id = ggml.guard_group_id JOIN res_users as ru ON ru.id = ggml.member_id ' \
                                'where gg.id = %d' % (group_id))
            rows = self.env.cr.fetchall()
            if rows:
                domain_group = ['|']
                for file in rows:
                    domain_group.append(('id', '=', int(file[0])))
                # print domain_group
                return {'domain': {'news_members_in_line': domain_group}}

    def _validate_news_date(self, news_date):
        res = {}
        today = str(date.today())
        if datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(news_date, DEFAULT_SERVER_DATE_FORMAT):
            res = {'news_date': news_date}
        return res

    @api.model
    def create(self, values):
        if values:
            if values.get('news_date'):
                res = self.env['news']._validate_news_date(values['news_date'])
                if not res:
                    raise osv.except_osv(('Advertencia!'),('La fecha seleccionada no puede ser mayor a la actual'))
            if not values.get('news_members_out_line'):
                raise osv.except_osv(('Advertencia!'),('Debe seleccionar al menos un miembro para el grupo que entrega la guardia'))
            if not values.get('news_members_in_line'):
                raise osv.except_osv(('Advertencia!'),('Debe seleccionar al menos un miembro para el grupo que recibe la guardia'))
            record = super(news, self).create(values)
            return record

    @api.multi
    def write(self, values):
        if values:
            if values.get('news_date'):
                res = self.env['news']._validate_news_date(values['news_date'])
                if not res:
                    raise osv.except_osv(('Advertencia!'),('La fecha seleccionada no puede ser mayor a la actual'))
            if not values.get('news_members_out_line'):
                raise osv.except_osv(('Advertencia!'),('Debe seleccionar al menos un miembro para el grupo que entrega la guardia'))
            if not values.get('news_members_in_line'):
                raise osv.except_osv(('Advertencia!'),('Debe seleccionar al menos un miembro para el grupo que recibe la guardia'))
            record = super(news,self).write(values)
            return record

class news_members_out_line(models.Model):
    _name = 'news.members.out.line'

    NO_ATTENDEE_REASON = [('rest','Rest'),
                          ('permision','Permision'),
                          ('vacations','Vacations'),
                          ('unknown', 'Unknown'),
                          ('change','Guard change'),
                          ('suppliear','There is no supplier')]

    @api.onchange('guard_group_out')
    def _out_groups_members_filter(self):
        if self.guard_group_out:
            group_id = self.guard_group_out
            self.env.cr.execute('SELECT ru.id, gg.name FROM guard_groups as gg JOIN guard_group_members as ggm ' \
                                'ON gg.id = ggm.guard_group_id JOIN guard_group_members_line as ggml ' \
                                'ON ggm.id = ggml.guard_group_id JOIN res_users as ru ON ru.id = ggml.member_id ' \
                                'where gg.id = %d' % (group_id))
            rows = self.env.cr.fetchall()
            if rows:
                domain_group = ['|']
                for file in rows:
                    domain_group.append(('id', '=', int(file[0])))
                #print domain_group
                return {'domain': {'member_id': domain_group}}

    news_id = fields.Many2one('news', 'News id', readonly=True)
    member_id = fields.Many2one('hr.employee','Member')
    news_member_attendee = fields.Boolean(default=True)
    news_member_no_attendee_reason = fields.Selection(NO_ATTENDEE_REASON, 'No attendee reason')
    member_id_substitute = fields.Many2one('hr.employee', 'Substitute')

    @api.onchange('member_id')
    def _substitute_filter(self):
        if self.member_id:
            member_id = self.member_id
            self.member_id_substitute = 0
            domain = [('id','!=', int(member_id))]
            return {'domain': {'member_id_substitute': domain}}
        else:
            return False

class news_members_in_line(models.Model):
    _name = 'news.members.in.line'

    NO_ATTENDEE_REASON = [('rest','Rest'),
                          ('permision','Permision'),
                          ('vacations','Vacations'),
                          ('unknown', 'Unknown'),
                          ('change','Guard change'),
                          ('suppliear','There is no supplier')]

    @api.onchange('guard_group_in')
    def _in_groups_members_filter(self):
        if self.guard_group_in:
            group_id = self.guard_group_in
            self.env.cr.execute('SELECT ru.id, gg.name FROM guard_groups as gg JOIN guard_group_members as ggm ' \
                                'ON gg.id = ggm.guard_group_id JOIN guard_group_members_line as ggml ' \
                                'ON ggm.id = ggml.guard_group_id JOIN res_users as ru ON ru.id = ggml.member_id ' \
                                'where gg.id = %d' % (group_id))
            rows = self.env.cr.fetchall()
            if rows:
                domain_group = ['|']
                for file in rows:
                    domain_group.append(('id', '=', int(file[0])))
                # print domain_group
                return {'domain': {'member_id': domain_group}}

    news_id = fields.Many2one('news', 'News id', readonly=True)
    member_id = fields.Many2one('hr.employee','Member')
    news_member_attendee = fields.Boolean(default=True)
    news_member_no_attendee_reason = fields.Selection(NO_ATTENDEE_REASON, 'No attendee reason')
    member_id_substitute = fields.Many2one('hr.employee', 'Substitute')

class guard_groups(models.Model):
    _name = 'guard.groups'

    name = fields.Char('Guard group name', size=50)
    group_headquarter = fields.Many2one('headquarter', string='Group Headquarter')
    group_leader = fields.Many2one('hr.employee', string='Group Leader')
    guard_group_members = fields.One2many('guard.group.members.line', 'guard_group_id', string='Group members')

class res_users_guard_groups_members(models.Model):
    _inherit = 'res.users'

    guard_groups_id = fields.Many2one('guard.groups', 'Guard group id')

class guard_groups_members_line(models.Model):
    _name = 'guard.group.members.line'

    guard_group_id = fields.Many2one('guard.group', readonly=True)
    member_id = fields.Many2one('hr.employee', 'Members')



class guard_groups_members(models.Model):
    _name = 'guard.group.members'

    guard_group_id = fields.Many2one('guard.groups', 'Guard group id')
    group_leader = fields.Many2one('hr.employee', 'Group leader')
    #guard_group_members = fields.Many2many('res.users', 'users_groups_rel', string='Group members')
    #guard_group_members = fields.One2many('guard.group.members.line', 'guard_group_id', string='Group members')

class guard_change(models.Model):
    _name = 'guard.change'

    change_date = fields.Date(string='Date')
    change_group = fields.Many2one('guard.groups', string='Guard Group')
    change_headquarter = fields.Char(string='Group Headquerter', related='change_group.group_headquarter.name')
    change_group_leader = fields.Many2one('hr.employee','Group Leader')#, related='change_group.group_leader.partner_id.name')
    change_vehicle = fields.Many2one('fleet.vehicle', string='Unit')
    change_notes = fields.Text(string='Notes')
    change_third_service = fields.Boolean(string='Third Service')
    change_viatic = fields.Boolean(string='Viatics')
    change_viatic_motive = fields.Char(string='Viatics Motive')
    change_members = fields.One2many('guard.change.line', 'guard_change_id', 'Members')

    @api.onchange('change_group')
    def onchange_change_group(self):
        if self.change_group:
            group_id = self.change_group.id
            members = self.env['guard.group.members.line'].search([('guard_group_id', '=', group_id)])
            if members:
                res = []
                for member in members:
                    res.append((0, 0, {'member_id': member.member_id}))
                self.change_members = res
            else:
                self.change_members = [(2, 0)]

class guard_change_line(models.Model):
    _name = 'guard.change.line'

    guard_change_id = fields.Many2one('guard.change', 'Guard Change')
    member_id = fields.Many2one('hr.employee', 'Member')


class provisional_employee(models.Model):
    _name = 'provisional.employee'

    name = fields.Char(string='Nombre',size=60)
    identification_number = fields.Char('Cédula', size=10)
    job_title = fields.Many2one('job.title','Cargo')

class job_title(models.Model):
    _name = 'job.title'
    _rec_name = 'job_title_employee'

    job_title_employee = fields.Char(string='Cargo',size=60)

