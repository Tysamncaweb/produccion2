# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import Warning

class Gastos(models.Model):
    _name = 'gastos.petty.cash'

    name = fields.Char('codigo')
    concepto = fields.Char('concepto')
    cta_contable = fields.Char('cuenta_contable')
