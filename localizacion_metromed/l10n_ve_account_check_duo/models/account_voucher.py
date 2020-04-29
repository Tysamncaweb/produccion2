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

from odoo import models, fields, api,exceptions, _, netsvc
import logging
_logger = logging.getLogger(__name__)

class account_payment(models.Model):

    _inherit = 'account.payment'
    _description = 'Change the journal_id in Check Model'

    issued_check_ids = fields.One2many('account.issued.check','voucher_id',string="cheques Propios", required=False, readonly=True, states={'draft':[('readonly',False)]})
    third_check_receipt_ids = fields.One2many('account.third.check','voucher_id', 'Third Checks', required=False, readonly=True, states={'draft':[('readonly',False)]})
    third_check_ids = fields.Many2many('account.third.check','third_check_voucher_rel', 'third_check_id', 'voucher_id','Third Checks',required=False,readonly=True, states={'draft':[('readonly',False)]})
    show_check_page = fields.Boolean('Show Check Page')
    use_issued_check = fields.Boolean('Use Issued Checks') #
    use_third_check = fields.Boolean('Use Third Checks')

   # _defaults = {

    #    'show_check_page': False,
     #   'use_issued_check': False,
      #  'use_third_check': False,
    #}

    @api.model
    def _amount_checks(self,voucher_id):
        res = {}
        res['issued_check_amount'] = 0.00
        res['third_check_amount'] = 0.00
        res['third_check_receipt_amount'] = 0.00
        if voucher_id:
            voucher_obj = self.env['account.payment'].browse(voucher_id)
            if voucher_obj.issued_check_ids:
                for issued_check in voucher_obj.issued_check_ids:
                    res['issued_check_amount'] += issued_check.amount
            if voucher_obj.third_check_ids:
                for third_check in voucher_obj.third_check_ids:
                    res['third_check_amount'] += third_check.amount
            if voucher_obj.third_check_receipt_ids:
                for third_rec_check in voucher_obj.third_check_receipt_ids:
                    res['third_check_receipt_amount'] += third_rec_check.amount
        return res  
    @api.multi
    def onchange_issued_checks(self,issued_check_ids, third_check_ids, journal_id, partner_id, currency_id,
                               type, date, amount):
                                                             
        data = {}
        new_amount = 0.00
        third_checks = self.env['account.third.check'].browse(third_check_ids[0][2])
        if third_checks.exists():
            for check in third_checks:
                new_amount += check.amount
        #modificación para que el monto total sea igual al de los cheques generados.
        for check in issued_check_ids:
            if check[2]:
                new_amount += check[2].get('amount', 0.00)
        
        if new_amount == 0.0: new_amount = amount
        data['amount'] = new_amount
        
        vals = self.onchange_partner_id(partner_id, journal_id, new_amount, currency_id, type, date)
        if vals: data.update(vals.get('value'))
        return {'value': data}

    @api.onchange('issued_check_ids')
    def total_amount(self):
        total_amount = 0
        for Reglon in self.issued_check_ids:
            total_amount += Reglon.amount
        if total_amount > 0: self.amount = total_amount

    @api.onchange('third_check_ids')
    def amount_total(self):
        amount_total = 0
        for Reglon in self.third_check_ids:
            amount_total += Reglon.amount
        if amount_total > 0: self.amount = amount_total


    @api.multi
    def onchange_third_check_receipt_ids(self,third_check_receipt_ids,
                                        journal_id, partner_id, currency_id, type,date,state):
                                       
        data = {} 
        # if len(ids) < 1:
        if len(self) < 1:
            data.update({'warning': {'title': _('ATENTION !'), 'message': _('Journal must be fill')}})
                     
        amount = 0.00
        for check in third_check_receipt_ids:
            #TYSAMNCA_14OCT2016_rsosa: solución a incidencia en creacion de nuevo pago
            amount += len(check[2]) > 0 and check[2].get('amount', 0.00) or 0.0
        data['amount'] = amount
        
        vals = self.onchange_partner_id(partner_id, journal_id,
                amount, currency_id, type, date)

        # PSI_23NOV2016_jmespiz: solución a incidencia en creacion de nuevo pago por validacion dict
        if vals and vals.get('value'):
            data.update(vals.get('value'))
        
        return {'value': data}

    @api.multi
    def onchange_third_check_ids(self,issued_check_ids, third_check_ids, journal_id, partner_id,
                                 currency_id, type, date, amount):
        
        data = {}
        new_amount = 0.00
        third_checks = self.env['account.third.check'].browse(third_check_ids[0][2])
        if third_checks.exists():
            for check in third_checks:
                new_amount += check.amount
            for check in issued_check_ids:
                if check[2]:
                    new_amount += check[2].get('amount', 0.00)
                
        if new_amount == 0.0: new_amount = amount
        data['amount'] = amount

        vals = self.onchange_partner_id(partner_id, journal_id, new_amount, currency_id, type, date)
        if vals: data.update(vals.get('value'))

        return {'value': data}

    @api.multi
    def onchange_journal(self,journal_id, line_ids, tax_id, partner_id, date, amount,
                         ttype, company_id):
        '''
        Override the onchange_journal function to check which are the page and fields that should be shown
        in the view.
        '''
        ret = super(account_payment, self).onchange_journal(journal_id, line_ids, tax_id, partner_id,
                                                    date, amount, ttype, company_id)
        
        if not journal_id:
            return ret
        
        journal_obj = self.env['account.journal']
        journal = journal_obj.browse([journal_id])
        if isinstance(journal, list):
            journal = journal[0]
        
        if journal.use_issued_check:
            ret['value']['use_issued_check'] = True
        else:
            ret['value']['use_issued_check'] = False
        
        if journal.use_third_check:
            ret['value']['use_third_check'] = True
        else:
            ret['value']['use_third_check'] = False
        
        if ttype in ['sale', 'receipt']:
            if not journal.use_third_check:
                ret['value']['show_check_page'] = False
            else:
                if journal.type == 'bank':
                    ret['value']['show_check_page'] = True
                else:
                    ret['value']['show_check_page'] = False
        
        elif ttype in ['purchase', 'payment']:
            if not journal.use_issued_check and not journal.use_third_check:
                ret['value']['show_check_page'] = False
            else:
                if journal.type == 'bank':
                    ret['value']['show_check_page'] = True
                else:
                    ret['value']['show_check_page'] = False
        return ret
        ###############################
        #  Aqui te toca Programar     #
        ###############################

    @api.multi
    def action_move_line_create(self):

        for voucher_obj in self:
            wf_service = netsvc.LocalService('workflow')
            _logger.info(" comienzo voucher_obj.type : %s", voucher_obj.type)
            if voucher_obj.type == 'payment':
                if voucher_obj.issued_check_ids:
                    for check in voucher_obj.issued_check_ids:
                        check.write({
                            'issued': True,
                            'receiving_partner_id': voucher_obj.partner_id.id,
                        })
                        wf_service.trg_validate(self.env.uid, 'account.issued.check', check.id, 'draft_handed', self.env.cr)
                else:
                    if voucher_obj.third_check_ids:
                        for check in voucher_obj.third_check_ids:

                            check_obj = self.env['account.third.check']
                            #result = check_obj.browse(self, check.id)
                            result = check_obj.browse(check.id)
                            if result.state != 'holding':
                                raise exceptions.except_orm(_('State!'), _('The check must be in holding state.'))
                                return False
                            else:
                                check.write({'destiny_partner_id': voucher_obj.partner_id,
                                             })
                                # _logger.info("por el else de tercero result.state: %s",result.state)
                                wf_service.trg_validate(self.env.uid, 'account.third.check', check.id, 'draft_holding', self.env.cr)
                                wf_service.trg_validate(self.env.uid, 'account.third.check', check.id, 'holding_handed', self.env.cr)

            elif voucher_obj.type == 'receipt':
                _logger.info("priemro voucher_obj.type: %s and voucher_obj %s",(voucher_obj.type, voucher_obj))

                for check in voucher_obj.third_check_receipt_ids:
                    check.write({
                        'source_partner_id': voucher_obj.partner_id.id,
                    })
                    wf_service.trg_validate(self.env.uid, 'account.third.check', check.id, 'draft_holding', self.env.cr)
        return super(account_payment, self).action_move_line_create()


    @api.multi
    def proforma_voucher(self):
        '''
        Override the proforma_voucher function (called when voucher workflow moves to act_done activity)
        to check, when the associated journal is marked with validate_only_checks, if the total amount is
        the same of the sum of checks.
        '''
        for voucher in self:
            if voucher.journal_id.validate_only_checks:
                check_amount = 0
                compare_amounts = False

                if voucher.type == 'payment':
                    compare_amounts = True
                    for issued_check in voucher.issued_check_ids:
                        check_amount += issued_check.amount
                    for third_check in voucher.third_check_ids:
                        check_amount += third_check.amount

                if voucher.type == 'receipt':
                    compare_amounts = True
                    for third_check in voucher.third_check_receipt_ids:
                        check_amount += third_check.amount

                voucher_amount = voucher.amount

                if compare_amounts and voucher_amount != check_amount:
                    title = _('Cannot Validate Voucher')
                    message = _('The associated journal force that the total amount is the same as the one paid with checks.')
                    raise exceptions.except_orm(title, message)

        return super(account_payment, self).proforma_voucher()

