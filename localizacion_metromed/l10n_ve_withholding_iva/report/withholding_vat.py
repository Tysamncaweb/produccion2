# coding: utf-8
###########################################################################

import time

#from odoo.report import report_sxw
#from odoo.tools.translate import _
from odoo import models, api, _
from odoo.exceptions import UserError, Warning, ValidationError

class IvaReport(models.AbstractModel):
    _name = 'report.l10n_ve_withholding_iva.template_wh_vat'
    #_name = 'report.l10n_ve_withholding_iva.template_wh_vat'

    #_inherit = 'report.abstract_report'
    #_template = 'l10n_ve_withholding_iva.template_wh_vat'

    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['account.wh.iva'].browse(docids)}
        res = dict()
        return {
            'data': data['form'],
            'model': self.env['report.l10n_ve_withholding_iva.template_wh_vat'],
            'lines': res, #self.get_lines(data.get('form')),
            #date.partner_id
        }

    def get_period(self, date):
        if not date:
            raise Warning (_("You need date."))
        split_date = date.split('-')
        return str(split_date[1]) + '/' + str(split_date[0])

    def get_date(self, date):
        if not date:
            raise Warning(_("You need date."))
        split_date = date.split('-')
        return str(split_date[2]) + '/' + (split_date[1]) + '/' + str(split_date[0])

    def get_direction(self, partner):
        direction = ''
        direction = ((partner.street and partner.street + ', ') or '') +\
                    ((partner.street2 and partner.street2 + ', ') or '') +\
                    ((partner.city and partner.city + ', ') or '') +\
                    ((partner.state_id.name and partner.state_id.name + ',')or '')+ \
                    ((partner.country_id.name and partner.country_id.name + '') or '')
        #if direction == '':
        #    raise ValidationError ("Debe ingresar los datos de direccion en el proveedor")
            #direction = 'Sin direccion'
        return direction

    def get_tipo_doc(self, tipo=None):
        if not tipo:
            return []
        types = {'out_invoice': '1', 'in_invoice': '1', 'out_refund': '2',
                 'in_refund': '2'}
        return types[tipo]

