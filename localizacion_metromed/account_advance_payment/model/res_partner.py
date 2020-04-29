# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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

from odoo import fields, models, api, exceptions, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _supplier_customer_advance_get(self, field, arg,
                                       context=None):
        res = {}
        for record_id in self.ids:
            res = {record_id: {'customer_advance': 0.0,
                               'supplier_advance': 0.0}}
        return res

    property_account_supplier_advance = fields.Many2one(
            related='account.account.id',
            string="Account Supplier Advance",
            domain="[('internal_type','=','payable')]",
            help="This account will be used for advance payment of suppliers")
    property_account_customer_advance = fields.Many2one(
            relation='account.account.id',
            string="Account Customer Advance",
            domain="[('internal_type','=','receivable')]",
            help="This account will be used for advance payment of customers")
