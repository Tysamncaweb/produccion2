# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
###############################################################################

from odoo import fields, models, api, exceptions, _

class ChangeInvoicePettyCashwizard(models.TransientModel):

    """
    Wizard that changes the invoice sin_cred field.
    """
    _name = 'change.invoice.petty.cash'
    _description = 'Change Invoice Tax Exempt'

    sin_cred = fields.Boolean('Tax Exempt',default=lambda s: s._context.get('invoice_sin_cred'),
            help='Tax Exempt')
    sure = fields.Boolean('Are you sure?')

    @api.multi
    def sin_fiscal_book(self):
        """
        Change the sin cred field in the invoice
        @return
        """
        context = self._context or {}
        ids = isinstance(self.ids, (int, int)) and [self.ids] or self.ids
        inv_obj = self.env['account.invoice']
        inv_ids = context.get('active_ids', [])
        data = self.browse(ids[0])
        invoice = inv_obj.browse(self._context['active_id'])

        if not data.sure:
            raise exceptions("Error!, Please confirm that you want to do this by checking the option")
        if inv_ids:
            invoice.write({'sin_cred': self.sin_cred})
        return {}
