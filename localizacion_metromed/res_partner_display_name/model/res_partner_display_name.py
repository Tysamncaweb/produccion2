# -*- coding: UTF-8 -*-
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
#    type of the change:  Created for Roselyn Volcan
#    Change:   rvolcan **  12/08/2016 **  res.partner **  Modified
#    Comments: Campo y funciones para el modulo de res_partner.
#
##############################################################################


from odoo import fields, models, exceptions, api
from datetime import datetime
from dateutil import relativedelta
#rvolcan: formato de fecha yyyy-mm-dd
_DATETIME_FORMAT = "%Y-%m-%d"
#from curses.ascii import isdigit
import re

class res_partner(models.Model):
    _inherit = "res.partner"
    _description = "display_name"

    date = fields.Date('Date', select=1)
    #fax = fields.Char(string="Fax", size=13)

    # validacion de fecha
    @api.onchange('date')
    def onchange_date(self):
        #res = {}
        fecha = self.date
        if fecha:
            age = self._calculate_date(self.date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.date = fecha
            else:
                self.date = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}



    @api.multi
    def _calculate_date(self, value):
        age = 0
        if value:
                ahora = datetime.now().strftime(_DATETIME_FORMAT)
                age = relativedelta.relativedelta(datetime.strptime(ahora,_DATETIME_FORMAT), datetime.strptime(value,_DATETIME_FORMAT))
        return age



