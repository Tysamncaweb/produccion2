# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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
##############################################################################

from openerp.osv import osv
from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_supplier_advance = fields.Many2one(
        'account.account',
        string="Account Supplier Advance",
        domain="[('internal_type','=','payable')]",
        help="This account will be used for advance payment of suppliers",
        default="_get_account_supplier_customer_advance")

    property_account_customer_advance = fields.Many2one(
        'account.account',
        string="Account Customer Advance",
        domain="[('internal_type','=','receivable')]",
        help="This account will be used for advance payment of custom")

    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        if res.has_key('property_account_supplier_advance') and res.has_key('property_account_customer_advance'):
            if res.get('supplier'):
                res.update({
                    'property_account_supplier_advance': self.env.user.company_id.supplier_advance_account_id.id,
                })
            if res.get('customer'):
                res.update({
                    'property_account_customer_advance': self.env.user.company_id.customer_advance_account_id.id,
                })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: