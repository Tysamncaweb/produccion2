# coding: utf-8

###############################################################################

from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models,fields


class WizNroctrl(osv.osv_memory):
    _name = 'wiz.nroctrl'
    _description = "Wizard that changes the invoice control number"



    def set_noctrl(self,context):
        """ Change control number of the invoice
        """
        account_invoice = self.env['account.invoice'].search([])

        if context is None:
            context = {}
        if not self.sure:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the"
                  " option"))
        inv_obj = self.env['account.invoice']
        n_ctrl = self.name
        for noctrl in account_invoice :
            if noctrl.nro_ctrl ==  n_ctrl:
                raise osv.except_osv(
                    _("Error!"),
                    _("El Numero de Control ya Existe"))
        active_ids = context.get('active_ids', [])
        inv_obj.browse(active_ids).write({'nro_ctrl': n_ctrl})
        return {}


    name = fields.Char('Control Number', required=True)
    sure = fields.Boolean('Are you sure?')

WizNroctrl()
