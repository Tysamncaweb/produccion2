# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
###############################################################################

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'


    wh_src_collected_account_id = fields.Many2one(
            'account.account',
            string="Collected Withholding SRC Account",
            method=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used when applying a withhold to"
                 " an Supplier")

   # wh_src_paid_account_id = fields.Many2one(
    #        'account.account',
     #       string="Paid Withholding SRC Account",
           # domain="[('type', '=', 'other')]",
      #      help="This account will be used when applying a withhold to a"
       #          " Customer")

