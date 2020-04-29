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


import time

from odoo import api
#from openerp.addons import decimal_precision as dp
from odoo import fields, models, exceptions, api
from odoo.tools.translate import _


class AccountWhSrc(models.Model):

    _name = "account.wh.src"
    _description = "Social Responsibility Commitment Withholding"


    name = fields.Char('Description', size=64, readonly=True,
                            states={'draft': [('readonly', False)]},
                            help="Description of withholding")
    code = fields.Char(
            'Code', size=32, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Withholding reference")
    number = fields.Char(
            'Number', size=32, states={'draft': [('readonly', False)]},
            help="Withholding number")
    type = fields.Selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ], string='Type', readonly=False,
            help="Withholding type")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], string='Estado', readonly=True, default='draft',
            help="Status Voucher")
    date_ret = fields.Date('Withholding date', readonly=True,
                                states={'draft': [('readonly', False)]},
                                help="Keep empty to use the current date")
    date = fields.Date(
            'Date', readonly=True, states={'draft': [('readonly', False)]},
            help="Date")
    #period_id': fields.Many2one(
     #       'account.period', 'Force Period', domain=[('state', '!=', 'done')],
      #      readonly=True, states={'draft': [('readonly', False)]},
       #     help="Keep empty to use the period of the validation"
        #         " (Withholding date) date.")
    account_id = fields.Many2one(
            'account.account', 'Account', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            help="The pay account used for this withholding.")
    partner_id = fields.Many2one(
            'res.partner', 'Partner', readonly=True, required=True,
            states={'draft': [('readonly', False)]},
            help="Withholding customer/supplier")
    currency_id = fields.Many2one(
            'res.currency', 'Currency', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._get_currency(),
            help="Currency")
    journal_id = fields.Many2one(
            'account.journal', 'Journal', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._get_journal(),
            help="Journal entry")
    company_id = fields.Many2one(
            'res.company', 'Company', required=True,
            default=lambda s: s._get_company(),
            help="Company")
    line_ids = fields.One2many(
            'account.wh.src.line', 'wh_id', 'Local withholding lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help="Invoices which deductions will be made")
    wh_amount = fields.Float(
            'Amount', required=True,
    #        digits_compute=dp.get_precision('Withhold'),
            help="Amount withheld")

    uid_wh_agent = fields.Boolean(
             string="uid_wh_agent", compute='_get_wh_agent', store=False,
            help='indicates whether the current user is agent')

    partner_list = fields.Char(
             string='Lista', compute='_get_p_agent', store=False,
            method=False,
            help='partners are only allowed to be withholding agents')


    _sql_constraints = [
    ]


    @api.multi
    def name_get(self):
        """ To generate a name for src record
        """
        if isinstance(self._ids, (int)):
            ids = [self._ids]
        if not self.ids :
            return []
        res = []
        data_move = self.env['account.wh.src'].browse(
            )
        for move in data_move:
            if not move.name:
                if move.number:
                    name = move.number
                else:
                   name = 'CRS * ID = ' + str(move.id)
            else:
                name = move.name
            res.append((move.id, name))
        return res

    @api.one
    def _get_uid_wh_agent(self):
        """ Return true if current partner is social responsability agent and
        return false in otherwise
        """
        context = self._context or {}
        rp_obj = self.env['res.partner']
        ru_obj = self.env['res.users']
        ru_brw = ru_obj.browse()
        acc_part_brw = rp_obj._find_accounting_partner(
            ru_brw.company_id.partner_id)
        return acc_part_brw.wh_src_agent

    @api.one
    def _get_partner_agent(self):
        """ Return a list of browse partner depending of invoice type
        """
        obj_partner = self.env['res.partner']
        args = [('parent_id', '=', False)]
        context = self._context or {}
        res = []

        if context.get('type') in ('out_invoice',):
            args.append(('wh_src_agent', '=', True))
        partner_ids = obj_partner.search(args)
        if partner_ids:
            partner_brw = obj_partner.browse(
                partner_ids)
            res = [item.id for item in partner_brw]
        return res

    @api.model
    def default_get(self, field_list):
        """ Update fields uid_wh_agent and partner_list to the create a
        record
        """
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        context = self._context or {}
        res = super(AccountWhSrc, self).default_get(
             field_list)
        res.update({'uid_wh_agent': self._get_uid_wh_agent(
            )})
        res.update({'partner_list': self._get_partner_agent(
            )})

        return res



    def _get_p_agent(self):
        """ Create a dictionary with ids partner and their browse item
        """
        context = self._context or {}
        res = {}.fromkeys(self.ids, self._get_partner_agent(
            ))
        return res

    def _get_wh_agent(self):
        """ Create a dictionary with ids agent partner and their browse item
        """
        context = self._context or {}
        res = {}.fromkeys(self.ids, self._get_uid_wh_agent(
                                                      ))
        return res

    def _get_company(self):
        user = self.env['res.users'].browse()
        return user.company_id.id


    def _get_currency(self):
        user = self.env['res.users'].browse()
        return user.company_id.currency_id.id

    @api.multi
    def _get_journal(self):
        """
        Return a SRC journal depending of invoice type
        """
        context = dict(self._context or {})
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'src_sale',
                        'in_invoice': 'src_purchase'}
        journal_obj = self.env['account.journal']
        user = self.env['res.users'].browse(
            )
        company_id = context.get('company_id', user.company_id.id)
        domain = [('company_id', '=', company_id)]
        domain += [('type', '=', type2journal.get(
            type_inv, 'src_purchase'))]
        res = journal_obj.search( domain, limit=1)
        return res and res[0] or False


    @api.onchange('partner_id')
    def onchange_partner_id(self
                            ):
        """ Return account depending of the invoice
        @param type: invoice type
        @param partner_id: partner id
        """
        if self._context is None:
            context = {}
        acc_part_brw = False
        acc_id = False
        rp_obj = self.env['res.partner']
        wh_line_obj = self.env['account.wh.src.line']

        if self.partner_id:
            #partner = rp_obj.browse(self.partner_id)
            acc_part_brw = rp_obj._find_accounting_partner(self.partner_id)
            if self.type and self.type in ('out_invoice', 'out_refund'):
                acc_id = acc_part_brw.property_account_receivable_id \
                    and acc_part_brw.property_account_receivable_id.id or False
            else:
                acc_id = acc_part_brw.property_account_payable_id \
                    and acc_part_brw.property_account_payable_id.id or False

       # part_brw = self.ids and rp_obj._find_accounting_partner(self.browse(
        #    self, self.ids[0]).partner_id)
        wh_lines = self.ids and wh_line_obj.search(
                                              [('wh_id', '=', self.ids[0])])
        if not self.partner_id:
            if wh_lines:
                wh_line_obj.unlink(wh_lines)
            wh_lines = []
        if self.partner_id and acc_part_brw and self.partner_id.id != acc_part_brw.id:
            if wh_lines:
                wh_line_obj.unlink(wh_lines)
            wh_lines = []

        return {'value': {
            'line_ids': wh_lines,
            'account_id': acc_id,
        }
        }
    @api.multi
    def action_date_ret(self):
        """ if the retention date is empty, is filled with the current date
        """
        for wh in self.browse():
            if not wh.date_ret:
                self.write([wh.id],
                           {'date_ret': time.strftime('%Y-%m-%d')})
        return True

    @api.multi
    def action_draft(self):
        """ Passes the document to draft status
        """
        context = self._context or {}
        inv_obj = self.env['account.invoice']

        brw = self.browse( self.ids[0])
        inv_ids = [i.invoice_id.id for i in brw.line_ids]
        if inv_ids:
            inv_obj.write( {'wh_src_id': False})

        return self.write( {'state': 'draft'})

    @api.multi
    def action_confirm(self):
        """ Retention is valid to pass a status confirmed
        """
       # context = self._context or {}
        inv_obj = self.env['account.invoice']

        brw = self.browse(self.ids[0])
        line_ids = brw.line_ids
        if not line_ids:
            raise exceptions.except_orm(
                _('Invalid Procedure!'), _("No retention lines"))

        res = [True]
        res += [False for i in line_ids
                if (i.wh_amount <= 0.0 or
                    i.base_amount <= 0.0 or
                    i.wh_src_rate <= 0.0)]
        if not all(res):
            raise exceptions.except_orm(
                _('Invalid Procedure!'),
                _("Verify retention lines do not have Null values(0.00)"))

        res = 0.0
        for i in line_ids:
            res += i.wh_amount
        if abs(res - brw.wh_amount) > 0.0001:
            raise exceptions.except_orm(
                _('Invalid Procedure!'),
                _("Check the amount of withholdings"))

        inv_ids = [i.invoice_id.id for i in brw.line_ids]
        if inv_ids:
            inv_obj.write({'wh_src_id': self.ids[0]})

        return self.write({'state': 'confirmed'})

    @api.multi
    def action_done(self):
        """ Pass the document to state done
        """
        if self._context is None:
            context = {}

        self.action_date_ret()
        self.action_number()
        self.action_move_create()

        return self.write( {'state': 'done'})

    def _dummy_cancel_check(self):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True
    @api.multi
    def cancel_check(self):
        '''
        Unique method to check if we can cancel the Withholding Document
        '''
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids

        if not self._dummy_cancel_check():
            return False
        return True


    def cancel_move(self):
        """ Delete move lines related with withholding vat and cancel
        """
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        am_obj = self.env['account.move']
        for ret in self.browse():
            if ret.state == 'done':
                for ret_line in ret.line_ids:
                    if ret_line.move_id:
                        am_obj.button_cancel( [ret_line.move_id.id])
                        am_obj.unlink( [ret_line.move_id.id])
            ret.write({'state': 'cancel'})
        return True


    def clear_wh_lines(self):
        """ Clear lines of current withholding document and delete wh document
        information from the invoice.
        """
        context = self._context or {}
        awsl_obj = self.env['account.wh.src.line']
        ai_obj = self.env['account.invoice']
        if self.ids:
            awsl_ids = awsl_obj.search([('wh_id', 'in', self.ids)]
                                       )
            ai_ids = awsl_ids and [
                awsl.invoice_id.id
                for awsl in awsl_obj.browse(awsl_ids)]
            if ai_ids:
                ai_obj.write(
                             {'wh_src_id': False})
            if awsl_ids:
                awsl_obj.unlink(awsl_ids)

        return True


    def action_cancel(self):
        """ Call cancel_move and return True
        """
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        context = self._context or {}
        self.cancel_move()
        self.clear_wh_lines()
        return True

    @api.multi
    def copy(self, default=None):
        """ Lines can not be duplicated in this model
        """
        # NOTE: use ids argument instead of id for fix the pylint error W8106
        # method-required-super.
        if False:
            return super(AccountWhSrc, self).copy(default)

        raise exceptions.except_orm(
            _('Invalid Procedure!'),
            _("You can not duplicate lines"))

    def unlink(self):
        """ Overwrite the unlink method to throw an exception if the
        withholding is not in cancel state."""
        context = self._context or {}
        for src_brw in self.browse():
            if src_brw.state != 'cancel':
                raise exceptions.except_orm(
                    _("Invalid Procedure!!"),
                    _("The withholding document needs to be in cancel state to"
                      " be deleted."))
            else:
                super(AccountWhSrc, self).unlink(
                    )
        return True

    @api.multi
    def action_move_create(self):
        """ Build account moves related to withholding invoice
        """
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        context.update({'wh_src': True})
        ret = self.browse(self.ids[0])
        for line in ret.line_ids:
            if line.move_id:
                raise exceptions.except_orm(
                    _('Invoice already withhold !'),
                    _("You must omit the follow invoice '%s' !") %
                    (line.invoice_id.number,))

        acc_id = ret.account_id.id
        journal_id = ret.journal_id.id
        demo_enabled = self.env['ir.module.module'].search(
                 [('name', '=', 'base'), ('demo', '=', True)])
        args = [('id', 'in')]
        if not demo_enabled:
                args.append(('special', '=', False))

        if ret.line_ids:
            for line in ret.line_ids:
                    writeoff_account_id, writeoff_journal_id = False, False
                    amount = line.wh_amount
                    if line.invoice_id.type in ['in_invoice', 'in_refund']:
                        name = 'COMP. RET. CRS ' + ret.number + ' Doc. ' + (
                            line.invoice_id.supplier_invoice_number or '')
                    else:
                        name = 'COMP. RET. CRS ' + ret.number + ' Doc. ' + (
                            line.invoice_id.number or '')
                 #   ret_move = inv_obj.ret_and_reconcile(
                   #     self, [line.invoice_id.id], amount, acc_id,
                  #       journal_id, writeoff_account_id,
                   #     writeoff_journal_id, ret.date_ret, name, [line]
                  #  )
                 #   rl = {
                #        'move_id': ret_move['move_id'],
                #    }
                    #lines = [(1, line.id)]
                    self.write({'line_ids': line})

                    if (line.invoice_id.type in [
                        'out_invoice', 'out_refund']):
                        inv_obj.write({'wh_src_id': ret.id})
            else:
                return False
        return True

    @api.multi
    def action_number(self, *args):
        """ Is responsible for generating a number for the document if it does
        not have one
        """
       # obj_ret = self.browse()
        if self.type == 'out_invoice':
            self._cr.execute(
                'SELECT id, number '
                'FROM account_wh_src '
                'WHERE id IN (' + ','.join([str(item) for item in self.ids]) + ')')

            for (aws_id, number) in self._cr.fetchall():
                if not number:
                    number = self.env['ir.sequence'].get(
                        'account.wh.src.%s' % self.type)
                self._cr.execute('UPDATE account_wh_src SET number=%s '
                           'WHERE id=%s', (number, aws_id))

        return True

    @api.multi
    def wh_src_confirmed(self):
        """ Confirm src document
        """
        return True


class AccountWhSrcLine(models.Model):

    _name = "account.wh.src.line"
    _description = "Social Responsibility Commitment Withholding Line"


    name = fields.Char(
            'Description', size=64, required=True,
            help="Local Withholding line Description")

    wh_id = fields.Many2one(
            'account.wh.src', 'Local withholding', ondelete='cascade',
            help="Local withholding")
    invoice_id = fields.Many2one(
            'account.invoice', 'Invoice', required=True, ondelete='set null',
            help="Withholding invoice")
    base_amount = fields.Float(
            'Base Amount',
        #    digits_compute=dp.get_precision('Base Amount to be Withheld'),
            help='amount to be withheld')
    wh_amount = fields.Float(
            'Withheld Amount', #digits_compute=dp.get_precision('Withhold'),
            help='withheld amount')
    move_id = fields.Many2one(
            'account.move', 'Account Entry', readonly=True,
            help="Account Entry")
    wh_src_rate = fields.Float(
            'Withholding Rate', help="Withholding rate")


    _sql_constraints = [

    ]
    @api.onchange('invoice_id','parent.type','base_amount','wh_src_rate')
    def onchange_invoice_id(self):
        """ Change src information to change the invoice
        @param type: invoice type
        @param invoice_id: new invoice id
        @param base_amount: new base amount
        @param wh_src_rate: new rate of the withhold src
        """
    #    self.invoice_id = False
   #     self.base_amount = 0.0
  #      self.wh_src_rate = 5.0
        if self._context is None:
            context = {}
        res = {}
        inv_obj = self.env['account.invoice']
        if not self.invoice_id:
            return {'value': {
                'invoice_id': False,
                'base_amount': 0.0,
                'wh_src_rate': 0.0,
                'wh_amount': 0.0, }
            }

        inv_brw = inv_obj.browse(self.invoice_id.id)
        base_amount = self.base_amount or inv_brw.amount_untaxed
        wh_src_rate = self.wh_src_rate or inv_brw.wh_src_rate or 5.0
        wh_amount = base_amount * wh_src_rate / 100.0
        res = {'value': {
            'base_amount': base_amount,
            'wh_src_rate': wh_src_rate,
            'wh_amount': wh_amount,
        }
        }
        return res
