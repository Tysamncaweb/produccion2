# -*- coding: utf-8 -*-

from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        invoice = self.env['calling'].search([('id', '=', self._context.get('calling_id',None))])
        if invoice:
            invoice.write({'quotation_number': result._ids})
        return result

