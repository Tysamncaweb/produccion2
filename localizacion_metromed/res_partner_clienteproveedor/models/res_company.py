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

from odoo import fields, models

class res_company(models.Model):
    _inherit = "res.company"

    supplier_advance_account_id =fields.Many2one(
        'account.account',
        "Account Supplier Advance",
        domain="[('internal_type','=','payable')]",
        help="This account will be used for advance payment of suppliers")
    customer_advance_account_id = fields.Many2one(
        'account.account',
        "Account Customer Advance",
        domain="[('internal_type','=','receivable')]",
        help="This account will be used for advance payment of custom")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
