# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
class HrEmployee(models.Model):
    '''
    Pay Slip
    '''
    _inherit = 'hr.employee'
    _description = 'Pay Slip'

    full_name = fields.Char(string='2do. Nombre', size=256)
    firstname = fields.Char(string='1er. Nombre', size=64)
    firstname2 = fields.Char(string='2do. Nombre', size=64)
    lastname = fields.Char(string='1er. Apellido', size=64)
    lastname2 = fields.Char(string='2do. Apellido', size=64)

    def concat_name(self):
        full_name = ''
        if self.firstname and self.lastname:
            full_name = self.firstname + ' ' + ((self.firstname2 and self.firstname2 + ' ') or '') + self.lastname + ((self.lastname2 and ' ' + self.lastname2) or '')
        return full_name

    @api.onchange('firstname','firstname2','lastname','lastname2')
    def onchange_name_filed(self):
        full_name = self.concat_name()
        res = {
            'value': {
                'full_name': full_name,
                'name': full_name,
            },
        }
        return res