# -*- coding: utf-8 -*-
##############################################################################
#
#    autor: Tysamnca.
#
##############################################################################

from odoo import api, models, fields, _, exceptions, time


class AccountWhMunici(models.Model):
    _name = "account.wh.munici"
    _description = "Local Withholding"

    @api.model
    #Tipo de factura devuelta
    def _get_type(self):
        context = self._context or {}
        inv_type = context.get('type','in_invoice')
        return inv_type

    def _get_journal(self):
        if self._context is None:
            context = {}
            type_inv = context.get('type','in_invoice')
            type2journal = {'out_invoice': 'mun_sale', 'in_invoice':
                'mun_purchase'}
            journal_obj = self.env['account.journal']
            res = journal_obj.search([('type', '=', type2journal.get(
                type_inv, 'mun_purchase'))], limit=1)
            if res:
                return res[0]
            else:
                return False

    def _get_currency(self):
        if self._context is None:
            context = {}
            user = self.env['res.users'].browse(self.ids)[0]
            if user.company_id:
                return user.company_id.currency_id.id
            else:
                return self.env['res.currency'].search(
                     [('rate', '=', 1.0)])[0]

    def _get_company(self):
        user = self.env['res.users'].browse(self.ids)
        return user.company_id.id

    name = fields.Char('Description', size=64, readonly=True, states={'draft': [('readonly', False)]}, required=True,
                       help="Description of withholding")
    code = fields.Char('Code', size=32, readonly=True, states={'draft': [('readonly', False)]},
                       help="Withholding reference")
    number = fields.Selection([('out_invoice', 'Customer Invoice'),
                               ('in_invoice', 'Supplier Invoice'), ],
                              string='Type', readonly=True, default=lambda s: s._get_type(), help="Withholding type")
    type = fields.Selection([('out_invoice', 'Customer Invoice'),
                             ('in_invoice', 'Supplier Invoice'), ],
                            string='Type', readonly=True, default=lambda s: s._get_type(), help="Withholding type")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')],
                             string='State', readonly=True, default='draft', help="Estado del Comprobante")
    date_ret = fields.Date('Withholding date', readonly=True, states={'draft': [('readonly', False)]},
                           help="Keep empty to use the current date")
    date = fields.Date('Date', readonly=True, states={'draft': [('readonly', False)]}, help="Date")
    account_id = fields.Many2one('account.account', 'Account', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 help="The pay account used for this withholding.")
    """period_id = fields.Many2one('account.period', 'Force Period', domain=[('state', '<>', 'done')], readonly=True,
                                states={'draft': [('readonly', False)]},
                                help="Keep empty to use the period of the validation(Withholding"" date) date.")"""
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}, default=lambda s: s._get_currency(),
                                  help="Currency")
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True, required=True,
                                 states={'draft': [('readonly', False)]}, help="Withholding customer/supplier")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s._get_company(),
                                 help="Company")
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, default=lambda s: s._get_journal(),
                                 help="Journal entry")
    munici_line_ids = fields.One2many('account.wh.munici.line', 'retention_id', 'Local withholding lines',
                                      readonly=True, states={'draft': [('readonly', False)]},
                                      help="Invoices to will be made local withholdings")
    amount = fields.Float('Amount', help="Amount withheld")
    move_id = fields.Many2one('account.move', 'Account Entry', help='account entry for the invoice')

    @api.multi
    def action_cancel(self):
        #context = self._context or {}
        self.cancel_move()
        self.clear_munici_line_ids()
        self.state = 'cancel'
        return True

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi
    def cancel_move(self):
        ret_brw = self.browse(self.ids)
        account_move_obj = self.env['account.move']
        for ret in ret_brw:
            if ret.state == 'done':
                for ret_line in ret.munici_line_ids:
                    if ret_line.move_id:
                        account_move_obj.button_cancel([ret_line.move_id.id])
                        account_move_obj.unlink([ret_line.move_id.id])
            self.write({'state': 'cancel'})
        return True

    @api.multi
    def write(self, vals):
        #context = self._context or {}
        #ids = isinstance(self) and [self.ids] or self.ids

        loc_amt = self.calculate_wh_total()
        vals.update({'amount':loc_amt})
        res = super(AccountWhMunici, self).write(vals)
        self._update_check()
        return res

    @api.model
    def create(self,vals):
        """ Validate before create record
        """

        loc_amt = self.calculate_wh_total()
        vals.update({'amount':loc_amt})
        new_id = super(AccountWhMunici, self).create(vals)
        self._update_check()
        return new_id


    def calculate_wh_total(self):
        local_amount = 0.0
        for line in self.munici_line_ids:
            local_amount += line.amount
        return local_amount


    def clear_munici_line_ids(self):
        #context = self._context or {}
        wml_obj = self.env['account.wh.munici.line']
        ai_obj = self.env['account.invoice']
        lista = []
        if self.ids:
            wml_ids = wml_obj.search([('retention_id', 'in', self.ids)])
            ai_ids = wml_ids and [wml.invoice_id.id for wml in wml_ids]
            if ai_ids:
                ai_obj.write( {'wh_muni_id': False})
            if wml_ids:
                wml_obj.unlink()
        return True

    @api.multi
    def action_confirm(self):
        #values = {}
        obj = self.browse(self.ids[0])
        total = 0.0
        for o in obj:
            for i in self.munici_line_ids:
            #if i.amount >= i.invoice_id.check_total * 0.15:
            #    raise exceptions.except_orm(_('Invalid action !'), _(
            #        "The line containing the document '%s' looks as if the"
            #        " amount withheld was wrong please check.!") % (
            #                i.invoice_id.supplier_invoice_number))
                total += i.amount
        #self.amount = total
            o.write({'amount': total, 'state': 'confirmed'})
        return True

    @api.multi
    def action_number(self):
        obj_ret = self.browse(self.ids)[0]
        if obj_ret.type == 'in_invoice':
            self.env.cr.execute('SELECT id, number '
                       'FROM account_wh_munici '
                       'WHERE id IN (' + ','.join(
                [str(item) for item in self.ids]) + ')')

            for (awm_id, number) in self.env.cr.fetchall():
                if not number:
                    number = self.env['ir.sequence'].get('account.wh.muni.%s' % obj_ret.type)
                self.env.cr.execute('UPDATE account_wh_munici SET number=%s '
                           'WHERE id=%s', (number, awm_id))
        return True

    @api.multi
    def action_done(self):
        """ The document is done
        """
        #if self._context is None:
        #    context = {}
        self.action_number()
        self.action_move_create()
        self.state = 'done'
        return True

    @api.multi
    def action_move_create(self):
        """Queda pendiente revisar el punto referente al periodo, porque en el 11 hay un tema con respecto a esto"""
        inv_obj = self.env['account.invoice']
        ctx = dict(self._context, muni_wh=True,
                   company_id=self.env.user.company_id.id)
        for ret in self.with_context(ctx):
            #Busca si ya hay retenciones para esta factura
            for line in self.munici_line_ids:
                if line.move_id or line.invoice_id.wh_local:
                    raise exceptions.except_orm(_('Invoice already withhold !'), _(
                        "You must omit the follow invoice '%s' !") % (line.invoice_id.name,))

            acc_id = self.account_id.id
            if not self.date_ret:
                self.write({'date_ret':time.strftime('%Y-%m-%d')})
                ret = self.browse(ret.id)

            #period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            #if not period_id:
            #    period_ids = self.env['account.period'].search(self.uid, [
            #        ('date_start', '<=', ret.date_ret or time.strftime('%Y-%m-%d')),
            #        ('date_stop', '>=', ret.date_ret or time.strftime('%Y-%m-%d'))])
            #    if len(period_ids):
            #        period_id = period_ids[0]
            #    else:
            #]        raise exceptions.except_orm(
            #            _('Warning !'),
            #            _("There was not found a fiscal period for this date:"
            #              " '%s' please check.!") % (ret.date_ret or time.strftime('%Y-%m-%d')))
            if ret.munici_line_ids:
                for line in ret.munici_line_ids:
                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount
                    name = 'COMP. RET. MUN ' + ret.number
                    self.with_context({'wh_county':'wh_county'})
                    ret_move = inv_obj.ret_and_reconcile(amount, acc_id, journal_id,
                                        writeoff_account_id, writeoff_journal_id,
                                        ret.date_ret, name, line, None,'wh_county')
                    # make the retencion line point to that move
                    rl = {'move_id': ret_move.id,}
                    lines = [(1, line.id, rl)]
                    self.write({'munici_line_ids': lines})
                    inv_obj.write({'wh_muni_id': ret.id})
        return True

    @api.onchange('type','partner_id')
    def onchange_partner_id(self):
        context = self._context or {}
        acc_id = False
        rp_obj = self.env['res.partner']
        if self.partner_id:
            acc_part_brw = rp_obj._find_accounting_partner(rp_obj.browse(self.ids))
            if self._get_type() in ('out_invoice', 'out_refund'):
                acc_id = (acc_part_brw.property_account_receivable_id and
                          acc_part_brw.property_account_receivable.id or False)
            else:
                acc_id = (acc_part_brw.property_account_payable and
                          acc_part_brw.property_account_payable.id or False)
        result = {'value': {
            'account_id': acc_id}
        }
        return result

    def _update_check(self):


        #ids = isinstance((int)) and [self.ids] or self.ids
        rp_obj = self.env['res.partner']
        for awm_id in self.ids:
            inv_str = ''
            awm_brw = self.browse(awm_id)
            for line in awm_brw.munici_line_ids:
                acc_part_brw = rp_obj._find_accounting_partner(
                    line.invoice_id.partner_id)
                if acc_part_brw.id != awm_brw.partner_id.id:
                    inv_str += '%s' % '\n' + (
                        line.invoice_id.name or line.invoice_id.number or '')
            if inv_str:
                raise exceptions.except_orm(
                    _('Incorrect Invoices !'),
                    _("The following invoices are not from the selected"
                      " partner: %s " % (inv_str,)))

        return True

    @api.multi
    def unlink(self):

        if self.state != 'cancel':
            raise exceptions.except_orm(
                _("Invalid Procedure!!"),
                _("The withholding document needs to be in cancel state"
                  " to be deleted."))
        return super(AccountWhMunici, self).unlink()
        #return True

    def confirm_check(self):

        #ids = isinstance(self.ids,int) and [self.ids] or self.ids

        if not self.check_wh_lines(self.ids):
            return False
        return True

    def check_wh_lines(self):
        #context = self._context or {}
        #ids = isinstance(self.ids, int) and [self.ids] or self.ids
        awm_brw = self.browse(self.ids)
        if not awm_brw.munici_line_ids:
            raise exceptions.except_orm(
                _("Missing Values !"),
                _("Missing Withholding Lines!"))
        self.state = 'confirmed'
        return True

class Accountwhmuniciline(models.Model):
    _name = "account.wh.munici.line"
    _description = "Local Withholding Line"

    name = fields.Char('Description', size=64, required=True,help="Local Withholding line Description")
    retention_id = fields.Many2one('account.wh.munici', 'Local withholding', ondelete='cascade',help="Local withholding")
    invoice_id = fields.Many2one('account.invoice', 'Invoice', required=True, ondelete='set null',help="Withholding invoice")
    amount = fields.Float('Amount',help='amout to be withhold')
    invoice_amount = fields.Float('Amount', help='Invoice amout')
    move_id = fields.Many2one('account.move', 'Account Entry', readonly=True,help="Account Entry")
    wh_loc_rate = fields.Float('Rate', help="Local withholding rate")
    concepto_id = fields.Integer('Concept', size=3, default=1,help="Local withholding concept")

    _sql_constraints = [
        ('munici_fact_uniq', 'unique (invoice_id)',
         'The invoice has already assigned in local withholding, you'
         ' cannot assigned it twice!')
    ]

    @api.model
    def defauld_get(self,field_list):
        if self._context is None:
            context = {}
        data = super(Accountwhmuniciline, self).default_get(field_list)
        self.munici_context = context
        return data

    @api.onchange('invoice_id','wh_loc_rate')
    def onchange_invoice_id(self):
        #if self._context is None:
        #    context = {}

        if not self.invoice_id:
            self.invoice_amount = 0.0
            self.amount =  0.0
            self.wh_loc_rate = 0.0

        else:
            amount_total = self.env['account.invoice'].browse(self.invoice_id.id).amount_total
            self.env.cr.execute('select retention_id '
                       'from account_wh_munici_line '
                       'where invoice_id=%s',
                       ([self.invoice_id.id]))
            ret_ids = self._cr.fetchone()
            if bool(ret_ids):
                ret = self.env[
                    'account.wh.munici'].browse(ret_ids[0])
                raise exceptions.except_orm(
                    _('Assigned Invoice !'),
                    "The invoice has already assigned in local withholding"
                    " code: '%s' !" % (ret.code,))

            total = amount_total * self.wh_loc_rate / 100.0
            self.amount = total
            self.invoice_amount = amount_total
            #return {'value': {'amount': total,
             #                 'wh_loc_rate': self.wh_loc_rate}}
    #@api.multi
    #def unlink(self):
    #    whm_obj = self.env['account.wh.munici']
    #    loc_state = whm_obj.search([('id', '=',self.retention_id)]).state
    #    if loc_state != 'cancel':
    #        raise exceptions.except_orm(
    #            _("Invalid Procedure!!"),
    #            _("The withholding document needs to be in cancel state"
    #            " to be deleted."))
    #    return super(Accountwhmuniciline, self).unlink()

class AccountInvoice(models.Model):
    _inherit = 'account.move.line'

    balance_muni = fields.Monetary(compute='_compute__quantity_balance', store=True, currency_field='company_currency_id',
                              help="Technical field holding balance (debit - credit) in municipal withholdings.",string='Balance')

    @api.multi
    @api.depends('debit', 'credit')
    def _compute__quantity_balance(self):
        type_dic = self._context
        type = type_dic.get('type',False)
        for line_id in self:
            if type == 'out_invoice':
                line_id.balance_muni = line_id.credit - line_id.debit
            else:
                line_id.balance_muni = line_id.debit - line_id.credit
