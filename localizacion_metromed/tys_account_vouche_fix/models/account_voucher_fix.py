# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models,api,_
import logging
_logger = logging.getLogger(__name__)

class account_voucher(models.Model):
    _inherit = 'account.voucher'
    _description = 'Fix onchange_third_check_receipt_ids method bug'

    @api.multi
    def onchange_third_check_receipt_ids(self, third_check_receipt_ids,
                                         journal_id, partner_id, currency_id, type, date, state):

        data = {}
        # if len(ids) < 1:
        if len(self) < 1:
            data.update({'warning': {'title': _('ATENTION !'), 'message': _('Journal must be fill')}})

        amount = 0.00
        for check in third_check_receipt_ids:
            amount += check[2].get('amount', 0.00) if check[2] else 0.00
        data['amount'] = amount

        vals = self.onchange_partner_id(partner_id, journal_id,
                                        amount, currency_id, type, date)
        data.update(vals.get('value'))

        return {'value': data}