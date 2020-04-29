# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Change: jeduardo **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################

from odoo import models, fields, api, exceptions

#from odoo import decimal_precision as dp

class withholding_islr_history(models.Model):
    _inherit = 'islr.wh.historical.data'

    # period_id = fields.Many2one('account.period', u'Período', readonly=True)
    base_amount = fields.Float('Cantidad Objeto de Retención', readonly=False)
    withheld_islr = fields.Float('Impuesto Retenido', readonly=False)
    withheld_islr_acum = fields.Float('Impuesto Retenido Acumulado', readonly=False)
    #withholding_islr_rate = fields.Float('Tasa de Retención', readonly=False)
    partner_id = fields.Many2one('res.partner', 'Proveedor', readonly=False)

#    _order = "period_id"

    '''
    def get_sumary_data(self, partner_id):
        res = []
        for p in partner_id:
            self.cr.execute("""select
	                        wh.base_amount,
	                        wh.withheld_islr,
	                        wh.withheld_islr_acum,
	                        wh.fiscalyear_id,
	                        wh.period_id,
	                        wh.partner_id,
	                        ap.name,
	                        af.name as fiscal_name
                        from
	                        islr_wh_historical_data as wh,account_period as ap, account_fiscalyear as af
                        where
				            wh.period_id = ap.id
				            and ap.fiscalyear_id = af.id
	                        and partner_id in (%s)
	                        and period_id between %s and %s
                        order by period_id
                """, (p, period_id[0],period_id[1]))
            temp = cr.dictfetchall()
            res+=temp
        return res

withholding_islr_history()
'''

class IslrWhDoc(models.Model):
    _inherit = "islr.wh.doc"

    @api.multi
    def action_done(self):
        if self._context is None: context = {}
        if not hasattr(self.ids, '__iter__'): ids = [self.ids]

        self.save_islr_record(self)
        res = super(IslrWhDoc, self).action_done(self)
        return res

    @api.multi
    def save_islr_record(self):
        wh_islr_histroy_obj=  self.pool.get('islr.wh.historical.data')
        wh_doc_line_obj = self.pool.get('islr.wh.doc.line')
        islr_history_data = {}
        concept_ids = False
        ba = 0.0
        rate = 0.0
        wihtheld_amount = 0.0
        wihtheld_amount_acum = 0.0
        wihtheld_amount_x_concept_line = 0.0
        fiscal_year = False
        historic_ids = None

        for islrwhdoc in self.browse(self):
            islr_history_data.update({'partner_id': islrwhdoc.partner_id.id})
                                   #   'period_id': islrwhdoc.period_id.id})
            historic_ids = wh_islr_histroy_obj.search( [('partner_id','=',islrwhdoc.partner_id.id)])
                                                           #, ('period_id','=', islrwhdoc.period_id.id)])
            if historic_ids:
                for h in wh_islr_histroy_obj.browse( historic_ids,self):
                    wihtheld_amount_acum = h.withheld_islr_acum
                    ba = h.base_amount
                    wihtheld_amount = h.withheld_islr   #monto retenido existente en el periodo actual

            concept_ids = islrwhdoc.concept_ids
            if concept_ids:
                for cl in wh_doc_line_obj.browse( concept_ids.ids,self):
                    ba += cl.base_amount
                    rate = cl.retencion_islr
                    wihtheld_amount_x_concept_line += cl.base_amount*rate/100   #monto retenido acumulado por concepto de una misma factura en el periodo actual
                    fiscal_year = cl.fiscalyear_id.id
                wihtheld_amount += wihtheld_amount_x_concept_line   #agrega monto retenido de una nueva factura a un periodo que ya registrado
                wihtheld_amount_acum = wihtheld_amount if wihtheld_amount_acum == 0 else wihtheld_amount_acum + wihtheld_amount_x_concept_line
                #wihtheld_amount_acum += wihtheld_amount
            islr_history_data.update({'base_amount':ba,
                                  'withheld_islr':wihtheld_amount,
                                  'fiscalyear_id':fiscal_year,
                                  'withheld_islr_acum':wihtheld_amount_acum})

            if historic_ids:
                wh_islr_histroy_obj.write( historic_ids, islr_history_data)
            else:
                wh_islr_histroy_obj.create(islr_history_data, self)

            self.update_wh_acum( fiscal_year, islrwhdoc.partner_id.id,self)

    @api.multi
    def update_wh_acum(self, fiscalyear_id, partner_id):
        acum = 0.0
        acum_temp = 0.0
        retenido = 0.0
        wh_islr_histroy_obj = self.pool.get('islr.wh.historical.data')
        history_ids = wh_islr_histroy_obj.search( [('fiscalyear_id', '=', fiscalyear_id),
                                                           ('partner_id', '=', partner_id)])
        history_data = wh_islr_histroy_obj.browse(self, history_ids )
        for hd in history_data:
            if retenido == 0 and acum == 0:
                acum = hd.withheld_islr_acum
                retenido = hd.withheld_islr
                acum_temp = acum
            else:
                acum = acum_temp + hd.withheld_islr
                acum_temp = acum
                wh_islr_histroy_obj.write( hd.id, {'withheld_islr_acum':acum})



IslrWhDoc()
'''
class account_period_close(models.TransientModel):
    """
        close period
    """
    _inherit = "account.period.close"

    def data_save(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        islr_wh_doc_obj = self.pool.get('islr.wh.doc')
        wh_islr_histroy_obj = self.pool.get('islr.wh.historical.data')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        withheld_islr_acum = 0.0
        islr_history_data = {
            'base_amount': 0.0,
            'withheld_islr': 0.0,
            'withheld_islr_acum': 0.0
        }


        for id in context['active_ids']:
            islr_history_data.update({'period_id':id})
            fiscalyear = period_obj.read(cr,uid,id,['fiscalyear_id','name'])
            period_month = fiscalyear['name'].split('/')[0]
            islr_history_data.update({'fiscalyear_id': fiscalyear['fiscalyear_id'][0]})
            date_stop = fiscalyear_obj.read(cr, uid,fiscalyear['fiscalyear_id'][0],['date_stop'])['date_stop']
            partner_ids = partner_obj.search(cr,uid,[('supplier','=',True),('active','=',True)])
            for p_id in partner_ids:
                islr_history_data.update({'partner_id': p_id, 'withheld_islr_acum':withheld_islr_acum})
                if date_stop and period_month in date_stop:
                    islr_wh_doc_obj.update_wh_acum(cr, uid, fiscalyear['fiscalyear_id'][0], p_id)
                else:
                    history_ids = wh_islr_histroy_obj.search(cr,uid,[('period_id','=',id),('partner_id', '=', p_id)])
                    if not history_ids:
                        wh_islr_histroy_obj.create(cr, uid, islr_history_data, context)
        res = super(account_period_close, self).data_save(cr, uid, ids, context)
        return res

account_period_close()
'''