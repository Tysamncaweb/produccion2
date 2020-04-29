# coding: utf-8

import base64

import odoo.addons  as addons
from odoo import  fields ,models
from odoo.tools.translate import _


class SplitInvoiceConfig(models.TransientModel):

    """ Fiscal Requirements installer wizard
    """
    _name = 'split.invoice.config'
    _inherit = 'res.config'


    name = fields.Integer(
            'Max Invoice Lines', required=True, default=50,
            help='Select the maximum number of lines in your customer'
                 ' invoices')

    def default_get(self, fields_list=None):
        """ Default value to the config_logo field
        """
        defaults = super(SplitInvoiceConfig, self).default_get(
        fields_list=fields_list)
        logo = open(addons.get_module_resource(
            'l10n_ve_split_invoice', 'images', 'puente-maracaibo.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    def execute(self):
        """
        In this method I will configure the maximum number of lines in your
        invoices.
        """
        wiz_data = self
        if wiz_data.name < 1:
            raise ValueError(_('The number of customer invoice lines must be at least one'))
        company = self.env['res.users'].company_id
        company_obj = self.env['res.company']
        company_id = company_obj.search([('id', '=', company.id)])
        data = {'lines_invoice': wiz_data.name}
        company_obj.write(company_id,data)


SplitInvoiceConfig()
