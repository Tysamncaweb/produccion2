# -*- coding: utf-8 -*-
##############################################################################
#
#    autor: Tysamnca.
#
##############################################################################

from odoo import fields, models

class ResParther(models.Model):
    _inherit = 'res.partner'

    active_client = fields.Boolean(string ='Activo',default =False)