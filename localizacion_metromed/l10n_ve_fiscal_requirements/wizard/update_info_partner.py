# coding: utf-8

from odoo.osv import osv


class UpdateInfoPartner(osv.osv_memory):
    _name = 'update.info.partner'

    def update_info(self,cr):
        """ OpenERP osv memory wizard : update_info_partner
        """
        context = self._context or {}
        seniat_url_obj = self.env['seniat.url']
        self._cr.execute('''SELECT id FROM res_partner WHERE vat ilike 'VE%';''')
        record = self._cr.fetchall()
        pids = [item[0] for item in record]
        seniat_url_obj.connect_seniat(pids,all_rif=True)
        return{}


UpdateInfoPartner()
