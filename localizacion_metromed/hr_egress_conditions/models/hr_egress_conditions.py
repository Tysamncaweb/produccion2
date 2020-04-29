# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class hrEgressConditions(models.Model):
    _name = 'hr.egress.conditions'
    _description = "Registro de Motivos"

    name =fields.Char("Motivo de Egreso", size=150)
    description = fields.Text("Descripción del Motivo de Egreso", size=256)