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
{   'active': False,
    'colaboradora': 'Michel Castillo',
    'author': 'tysamnca',
    'category': 'Generic Modules/Accounting',
    'data': [   'view/account_check_duo_view.xml',
                'view/account_voucher_view.xml',
                'view/partner_view.xml',
                'view/account_view.xml',
                'security/ir.model.access.csv',
                'view/check_third_sequence.xml',
                'report/report_check_duo_pdf_view.xml',
                'view/ticket_deposit_view.xml',
                'view/account_checkbook_view.xml',
                'data/account_data.xml',
                'view/account_payment_view.xml'],
    'demo': [],
    'depends': ['account',
                'account_voucher',
               ],
    'description': '\n\n    \n\n This module provides to manage checks (issued and third) \n\n    Add models of Issued Checks and Third Checks. (Accounting/Banck ans Cash/Checks/)\n\n    Add options in Jorunals for using  checks in vouchers.\n\n    Add range of numbers for issued check (CheckBook).Accounting/configuration/Miscellaneous/CheckBooks.\n\n    Add ticket deposit for third checks. Change states from Holding to deposited.(Accounting/Banck ans Cash/Checks/)\n\n    \n\n\t\t',
    'installable': True,
    'auto_install': False,
    'name': 'Account Check Duo',
    'test': [],
    'version': '8.0.0.0.1'}