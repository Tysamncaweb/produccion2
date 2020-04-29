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

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    a = fields.Many2one('headquarter', required=True, string='Ubicación / Sede')
    b = fields.Char(string='Serial de Bateria', required=True)
    c = fields.Char(string='Serial de Carroceria', required=True)
    d = fields.Selection([('Operativo','Operativo'),
                                             ('Dañado','Dañado'),
                                             ('En Mantenimiento','En Mantenimiento')], string='Estado del Vehiculo', required=True)
    e = fields.Text(string='Observaciones')
    f = fields.Date(string='Fecha de Vencimiento de RCV', required=True)
    g = fields.Boolean(string='¿Homologado?')
    h = fields.Binary(string='Foto 1-D')
    i = fields.Binary(string='Foto 2-D')
    j = fields.Binary(string='Foto 1-I')
    k = fields.Binary(string='Foto 2-I')
    l = fields.Binary(string='Foto')
    m = fields.Binary(string='Foto')