# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Cambios:
#
# 28/12/2015: Se modifica por herencia el modulo account_checkbook (Chequeras) para agregar
#             un campo relacion many2one llamado "Cuenta Transitoria", como parte del requerimiento 
#             del modulo de Conciliacion de Cheques.
#
#
#
##############################################################################

from odoo import fields, models

class account_checkbook(models.Model):
    _name = 'account.checkbook'
    _inherit = 'account.checkbook'
    
#cuenta_transitoria = fields.Many2one('account.account','Cuenta Transitoria',required=True)
