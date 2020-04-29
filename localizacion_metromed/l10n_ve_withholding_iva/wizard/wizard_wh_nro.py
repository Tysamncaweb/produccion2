# coding: utf-8
###########################################################################



from odoo.osv import osv
from odoo.tools.translate import _
from  odoo import  fields

class WizardChangeNumberWhIva(osv.osv_memory):
    _name = 'wizard.change.number.wh.iva'
    _description = "Wizard that changes the withholding number"

    def default_get(self, cr, uid, field_list, context=None):
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        context = context or {}
        data = super(WizardChangeNumberWhIva, self).default_get(
            cr, uid, field_list, context)
        if (context.get('active_model') == 'account.wh.iva' and
                context.get('active_id')):
            wh_iva = self.pool.get('account.wh.iva').browse(
                cr, uid, context['active_id'], context=context)
            if wh_iva.number:
                nro = wh_iva.number.split('-')
                per = wh_iva.period_id.code.split('-')
                new_number = '%s-%s-%s' % (per[1], per[2], nro[2])
                data.update({'name': new_number})
        return data

    def set_number(self, cr, uid, ids, context):
        data = self.pool.get('wizard.change.number.wh.iva').read(
            cr, uid, ids)[0]
        if not data['sure']:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the"
                  " option"))
        wh_obj = self.pool.get('account.wh.iva')
        number = data['name']

        wh_iva = wh_obj.browse(cr, uid, context['active_id'])
        if wh_iva.state != 'done':
            raise osv.except_osv(
                _("Error!"),
                _('You can\'t change the number when state <> "Done"'))

        wh_obj.write(cr, uid, context['active_id'], {'number': number},
                     context=context)
        return {}


    name = fields.Char('Withholding number',required=True)
    sure = fields.Boolean('Are you sure?')

WizardChangeNumberWhIva()
