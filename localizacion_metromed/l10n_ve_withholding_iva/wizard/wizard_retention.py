# coding: utf-8
###########################################################################


from odoo.osv import osv
from odoo.tools.translate import _
from odoo import  fields

class WizRetention(osv.osv_memory):
    _name = 'wiz.vat.apply.wh'
    _description = ("Wizard that changes the retention exclusion from an"
                    " invoice")

    def set_retention(self):
        if not self.sure:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the"
                  " option"))
        inv_obj = self.env['account.invoice']
        n_retention = self.vat_apply
        inv_obj.browse(self._context.get('active_id')).write({'vat_apply': n_retention})
        return {}

    vat_apply = fields.Boolean(
            'Exclude this document from VAT Withholding')
    sure =  fields.Boolean('Are you sure?')

