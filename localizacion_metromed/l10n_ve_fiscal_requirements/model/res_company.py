# coding: utf-8

from odoo import fields,models,api


class ResCompany(models.Model):
    _inherit = 'res.company'

    jour_id = fields.Many2one(
            'account.journal', 'Journal', required=False,
            help="Default journal for damaged invoices")

    acc_id = fields.Many2one(
            'account.account', 'Account', required=False,
            help="Default account used for invoices and lines from damaged"
                 " invoices")

    printer_fiscal = fields.Boolean(
            'Manages fiscal printer',
            help='Indicates that the company can operate a fiscal printer')


    def create(self,val):
        """ To create a new record,
        adds a Boolean field to true
        indicates that the partner is a company
        """
        if self._context is None:
            context = {}
        context = dict(self._context)
        context.update({'create_company': True})
        return super(ResCompany, self).create(val)

    def write(self, values):
        """ To write a new record,
        adds a Boolean field to true
        indicates that the partner is a company
        """
        context = dict(self._context or {})
        context.update({'create_company': True})
        return super(ResCompany, self).write(values)

ResCompany()
