# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#    Planified by: Humberto Arocha & Nhomar Hernandez
#    Audited by: Humberto Arocha           <hbto@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from odoo import fields, models, api, exceptions, _

class AccountWhIvaLine(models.Model):
    _inherit = "account.wh.iva.line"

    fb_id = fields.Many2one('fiscal.book', 'Fiscal Book',
            help='Fiscal Book where this line is related to')

    @api.multi
    def _update_wh_iva_lines(self, inv_id, fb_id):
        """
        It relate the fiscal book id to the according withholding iva lines.
        """
        inv_obj = self.env['account.invoice']
        inv = inv_obj.browse(inv_id)
        if inv.wh_iva and inv.wh_iva_id:
            awil_ids = self.search([('invoice_id', '=', inv.id)])
            self.write({'fb_id': fb_id})
        return True
