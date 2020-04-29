# coding: utf-8
###########################################################################


import time

from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, exceptions, _


class AccountWhIvaLineTax(models.Model):
    _name = 'account.wh.iva.line.tax'

    @api.multi
    @api.depends('inv_tax_id')
    def _get_base_amount(self):
        """ Return withholding amount
        """
        for record in self:
            f_xc = self.env['l10n.ut'].sxc(
                record.inv_tax_id.invoice_id.currency_id.id,
                record.inv_tax_id.invoice_id.company_id.currency_id.id,
                record.wh_vat_line_id.retention_id.date)
            record.base = f_xc(record.inv_tax_id.base)
            record.amount = f_xc(record.inv_tax_id.amount)

    @api.multi
    def _set_amount_ret(self):
        """ Change withholding amount into iva line
        @param value: new value for retention amount
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        for record in self:
            if record.wh_vat_line_id.retention_id.type != 'out_invoice':
                continue
            if not record.amount_ret:
                continue
            sql_str = """UPDATE account_wh_iva_line_tax set
                    amount_ret='%s'
                    WHERE id=%d """ % (record.amount_ret, record.id)
            self._cr.execute(sql_str)
        return True

    @api.multi
    @api.depends('amount', 'wh_vat_line_id.wh_iva_rate')
    def _get_amount_ret(self):
        """ Return withholding amount
        """
        for record in self:
            # TODO: THIS NEEDS REFACTORY IN ORDER TO COMPLY WITH THE SALE
            # WITHHOLDING
            record.amount_ret = round(
                (record.amount * record.wh_vat_line_id.wh_iva_rate / 100.0) +
                0.00000001, 2)

    inv_tax_id = fields.Many2one(
        'account.invoice.tax', string='Invoice Tax',
        ondelete='set null', help="Tax Line")
    wh_vat_line_id = fields.Many2one(
        'account.wh.iva.line', string='VAT Withholding Line', required=True,
        ondelete='cascade', help="Line withholding VAT")
    tax_id = fields.Many2one(
        'account.tax', string='Tax',
        related='inv_tax_id.tax_id', store=True, readonly=True,
        ondelete='set null', help="Tax")
    name = fields.Char(
        string='Tax Name', size=256,
        related='inv_tax_id.name', store=True, readonly=True,
        ondelete='set null', help=" Tax Name")
    base = fields.Float(
        string='Tax Base', digit=dp.get_precision('Withhold'),
        store=True, compute='_get_base_amount',
        help="Tax Base")
    amount = fields.Float(
        string='Taxed Amount', digits=dp.get_precision('Withhold'),
        store=True, compute='_get_base_amount',
        help="Withholding tax amount")
    company_id = fields.Many2one(
        'res.company', string='Company',
        related='inv_tax_id.company_id', store=True, readonly=True,
        ondelete='set null', help="Company")
    amount_ret = fields.Float(
        string='Withheld Taxed Amount',
        store=True, compute='_get_amount_ret', inverse='_set_amount_ret',
        help="Vat Withholding amount")


class AccountWhIvaLine(models.Model):
    _name = "account.wh.iva.line"
    _description = "Vat Withholding line"

    @api.multi
    def load_taxes(self):
        """ Clean and load again tax lines of the withholding voucher
        """
        awilt = self.env['account.wh.iva.line.tax']
        partner = self.env['res.partner']
        for rec in self:
            if rec.invoice_id:
                rate = rec.retention_id.type == 'out_invoice' and \
                    partner._find_accounting_partner(
                        rec.invoice_id.company_id.partner_id).wh_iva_rate or \
                    partner._find_accounting_partner(
                        rec.invoice_id.partner_id).wh_iva_rate
                rec.write({'wh_iva_rate': rate})

                #crear el id en las lineas
                self.write({'retention_id': rec.invoice_id.wh_iva_id.id})

                # Clean tax lines of the withholding voucher
                #awilt.search([('wh_vat_line_id', '=', rec.id)]).unlink()
                # Filter withholdable taxes

                for tax in rec.invoice_id.tax_line_ids:
                    # Load again tax lines of the withholding voucher
                    awilt.create({'wh_vat_line_id': rec.id,
                                  'inv_tax_id': tax.id,
                                  'tax_id': tax.tax_id.id})
        return True


    @api.multi
    @api.depends('tax_line.amount_ret', 'tax_line.base', 'invoice_id')
    def _amount_all(self):
        """ Return amount total each line
        """
        for rec in self:
            if rec.invoice_id:
                if rec.invoice_id.type == 'in_refund':
                    rec.amount_tax_ret = sum(l.amount_ret for l in rec.tax_line)
                    rec.base_ret = sum(l.base for l in rec.tax_line)
                else:
                    rec.amount_tax_ret = sum(l.amount_ret for l in rec.tax_line)
                    rec.base_ret = sum(l.base for l in rec.tax_line)

    name = fields.Char(
        string='Description', size=64, required=True,
        help="Withholding line Description")
    retention_id = fields.Many2one(
        'account.wh.iva', string='Vat Withholding',
        ondelete='cascade', help="Vat Withholding")
    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', required=True,
        ondelete='restrict', help="Withholding invoice")
    supplier_invoice_number = fields.Char(
        string='Número de factura del proveedor', size=64,
        #related='invoice_id.supplier_invoice_number',
        store=True)
    tax_line = fields.One2many(
        'account.wh.iva.line.tax', 'wh_vat_line_id', string='Taxes',
        help="Invoice taxes")
    amount_tax_ret = fields.Float(
        string='importe del impuesto',
        compute='_amount_all',store=True,
        help="Withholding tax amount")
    base_ret = fields.Float(
        string='Wh. amount',store=True,
        compute='_amount_all',
        help="Withholding without tax amount")
    move_id = fields.Many2one(
        'account.move', string='Entrada de cuenta',store=True,
        ondelete='restrict', help="Account entry")
    wh_iva_rate = fields.Float(
        string='Tasa de retención de IVAt Rate',
        help="Vat Withholding rate")
    date = fields.Date(
        string='Fecha del Voucher',
        related='retention_id.date',
        help='Emission/Voucher/Document date')
    date_ret = fields.Date(
        string='Fecha de contabilidad',
        related='retention_id.date_ret',
        help='Accouting date. Date Withholding')

    _sql_constraints = [
        ('ret_fact_uniq', 'unique (invoice_id)', 'The invoice has already'
         ' assigned in withholding vat, you cannot assigned it twice!')
    ]

    @api.multi
    def invoice_id_change(self, invoice_id):
        """ Return invoice data to assign to withholding vat
        @param invoice: invoice for assign a withholding vat
        """
        result = {}
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice:
            self._cr.execute('select retention_id '
                             'from account_wh_iva_line '
                             'where invoice_id=%s' % (invoice_id))
            ret_ids = self._cr.fetchone()
            if bool(ret_ids):
                ret = self.env['account.wh.iva'].browse(ret_ids[0])
                raise exceptions.except_orm(
                    'Assigned Invoice !',
                    "The invoice has already assigned in withholding"
                    " vat code: '%s' !" % (ret.code))
            result.update({
                'name': invoice.name,
                'supplier_invoice_number': invoice.supplier_invoice_number})

        return {'value': result}


class AccountWhIva(models.Model):
    _name = "account.wh.iva"
    _description = "Withholding Vat"
    number_2 =fields.Char('numero respaldo')

    @api.model
    def create(self, values):
        wh_iva_id = super(AccountWhIva, self).create(values)
        wh_iva_id._partner_invoice_check()
        return wh_iva_id


    @api.multi
    def name_get(self,):
        res = []
        for item in self:
            if item.number and item.state == 'done':
                res.append((item.id, '%s (%s)' % (item.number, item.name)))
            else:
                res.append((item.id, '%s' % (item.name)))
        return res

    @api.multi
    @api.depends('wh_lines.amount_tax_ret', 'wh_lines.base_ret')
    def _amount_ret_all(self):
        """ Return withholding amount total each line
        """
        for rec in self:
            if rec.wh_lines:
                rec.total_tax_ret = sum(l.amount_tax_ret for l in rec.wh_lines)
                rec.amount_base_ret = sum(l.base_ret for l in rec.wh_lines)
    @api.model
    def _get_type(self):
        """ Return invoice type
        """
        context = self._context
        return context.get('type', 'in_invoice')

    @api.model
    def _get_journal(self):

        """ Return a iva journal depending of invoice type
        """
        partner_id = self._context.get('uid')
        partner = self.env['res.partner'].search([('id','=',partner_id )])
        purchase_journal_id = partner.purchase_journal_id.id
        res = self.env['account.journal'].search([('id','=',purchase_journal_id)])
        return res


    @api.model
    def _get_fortnight(self):
        """ Return currency to use
        """
        dt = time.strftime('%Y-%m-%d')
        tm_mday = time.strptime(dt, '%Y-%m-%d').tm_mday
        return tm_mday <= 15 and 'False' or 'True'

    @api.model
    def _get_currency(self):
        """ Return currency to use
        """
        if self.env.user.company_id:
            return self.env.user.company_id.currency_id.id
        return self.env['res.currency'].search([('rate', '=', 1.0)], limit=1)

    name = fields.Char(
        string='Description', size=64,
        help="Description of withholding")
    '''
    code = fields.Char(
        string='Internal Code', size=32, readonly=True,
        #states={'draft': [('readonly', False)]}, default=_get_wh_iva_seq,
        help="Internal withholding reference")
    '''
    number = fields.Char(
        string='Number', size=32,
        help="Withholding number")
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ], string='Type', readonly=True, default=_get_type,
        help="Withholding type")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
        ], string='State', readonly=True, default='draft',
        help="Withholding State")
    date_ret = fields.Date(
        string='Accounting date',
        help="Keep empty to use the current date")
    date = fields.Date(
        string='Fecha del Vale',
        help="Emission/Voucher/Document Date")
    account_id = fields.Many2one(
        'account.account', string='Account',
        help="The pay account used for this withholding.")
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=_get_currency,
        help="Currency")
    period_id = fields.Date( string='Periodo')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id.id,
        help="Company")
    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        help="Withholding customer/supplier")
    journal_id = fields.Many2one(
        'account.journal', string='Journal', default=_get_journal,
        help="Journal entry")
    wh_lines = fields.One2many(
        'account.wh.iva.line', 'retention_id',
        string='Vat Withholding lines',
        help="Vat Withholding lines")
    amount_base_ret = fields.Float(
        string='Amount', digits=dp.get_precision('Withhold'),
        compute='_amount_ret_all',
        help="Compute amount without tax")
    total_tax_ret = fields.Float(
        string='Cantidad retenida de impuesto de IVA', digits=dp.get_precision('Withhold'),
        compute='_amount_ret_all',
        help="Compute amount withholding tax vat")
    fortnight = fields.Selection([
        ('False', "First Fortnight"),
        ('True', "Second Fortnight")
        ], string="Quincena",  default=_get_fortnight,
        help="Withholding type")
    consolidate_vat_wh = fields.Boolean(
        string='Consolidar Quincena de Retencion de IVA',
        help='If set then the withholdings vat generate in a same'
        ' fornight will be grouped in one withholding receipt.')
    third_party_id = fields.Many2one(
        'res.partner', string='Socio de terceros',
        help='Third Party Partner')

    @api.multi
    def action_cancel(self):
        """ Call cancel_move and return True
        """
        self.get_reconciled_move()
        self.cancel_move()
        self.clear_wh_lines()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def get_reconciled_move(self):
        awil_obj = self.env['account.wh.iva.line']
        awil_brw = awil_obj.search([('retention_id','=',self.id)])

        dominio = [('move_id', '=', awil_brw.move_id.id),
                   ('reconciled', '=', True)]
        obj_move_line = self.env['account.move.line'].search(dominio)

        if obj_move_line:
            raise exceptions.ValidationError(
                ('El Comprobante ya tiene una aplicacion en la factura %s, debe desconciliar el comprobante para poder cancelar') % awil_brw.invoice_id.number)
        else:
            return True

    @api.multi
    def cancel_move(self):
        """ Delete move lines related with withholding vat and cancel
        """
        # moves = self.pool.get('account.move')
        #moves =  self.env['res.partner']
        moves = []
        for ret in self:
            if ret.state == 'done':
                for ret_line in ret.wh_lines:
                    if ret_line.move_id:
                        ret_line.move_id.reverse_moves(self.date_ret, self.journal_id)
            # second, set the withholding as cancelled
            ret.write({'state': 'cancel'})
        return True

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.model
    def _get_valid_wh(self, amount_ret, amount, wh_iva_rate,
                      offset=0.5):
        """ This method can be override in a way that
        you can afford your own value for the offset
        @param amount_ret: withholding amount
        @param amount: invoice amount
        @param wh_iva_rate: iva rate
        @param offset: compensation
        """

        return (amount_ret >= amount * (wh_iva_rate - offset) / 100.0 and
                amount_ret <= amount * (wh_iva_rate + offset) / 100.0)

    @api.multi
    def check_wh_taxes(self):
        """ Check that are valid and that amount retention is not greater than amount
        """
        note = _('Taxes in the following invoices have been miscalculated\n\n')
        error_msg = ''
        for record in self:
            wh_line_ids = []
            for wh_line in record.wh_lines:
                for tax in wh_line.tax_line:
                    if not record._get_valid_wh(
                            tax.amount_ret, tax.amount,
                            tax.wh_vat_line_id.wh_iva_rate):
                        if wh_line.id not in wh_line_ids:
                            note += _('\tInvoice: %s, %s, %s\n') % (
                                wh_line.invoice_id.name,
                                wh_line.invoice_id.number,
                                wh_line.invoice_id.supplier_invoice_number or
                                '/')
                            wh_line_ids.append(wh_line.id)
                        note += '\t\t%s\n' % tax.name
                    if tax.amount_ret > tax.amount:
                        porcent = '%'
                        error_msg += _(
                            "The withheld amount: %s(%s%s), must be less than"
                            " tax amount %s(%s%s).") % (
                                tax.amount_ret, wh_line.wh_iva_rate, porcent,
                                tax.amount, tax.amount * 100, porcent)
            if wh_line_ids and record.type == 'in_invoice':
                raise exceptions.except_orm(
                    _('Miscalculated Withheld Taxes'), note)
        if error_msg:
            raise exceptions.except_orm(_('Invalid action !'), error_msg)
        return True

    @api.multi
    def check_vat_wh(self):
        """ Check whether the invoice will need to be withheld taxes
        """
        res = {}
        for obj in self:
            if obj.type == 'out_invoice' and \
                    (not obj.date or not obj.date_ret):
                raise exceptions.except_orm(
                    _('Error!'),
                    _('Must indicate: Accounting date and (or) Voucher Date'))
            for wh_line in obj.wh_lines:
                if not wh_line.tax_line:
                    res[wh_line.id] = (
                        wh_line.invoice_id.name,
                        wh_line.invoice_id.number,
                        wh_line.invoice_id.supplier_invoice_number)
        if res:
            note = _(
                'The Following Invoices Have not already been withheld:\n\n')
            for i in res:
                note += '* %s, %s, %s\n' % res[i]
            note += _('\nPlease, Load the Taxes to be withheld and Try Again')

            raise exceptions.except_orm(
                _('Invoices with Missing Withheld Taxes!'), note)
        return True

    @api.multi
    def check_invoice_nro_ctrl(self):
        """ Method that check if the control number of the invoice is set
        Return: True if the control number is set, and raise an exception
        when is not.
        """
        res = {}
        for obj in self:
            for wh_line in obj.wh_lines:
                if not wh_line.invoice_id.nro_ctrl:
                    res[wh_line.id] = (
                        wh_line.invoice_id.name,
                        wh_line.invoice_id.number,
                        wh_line.invoice_id.supplier_invoice_number)
        if res:
            note = _('The Following Invoices will not be withheld:\n\n')
            for i in res:
                note += '* %s, %s, %s\n' % res[i]
            note += _('\nPlease, Write the control number and Try Again')

            raise exceptions.except_orm(
                _('Invoices with Missing Control Number!'), note)
        return True

    @api.multi
    def write_wh_invoices(self):
        """ Method that writes the wh vat id in sale invoices.
        Return: True: write successfully.
                False: write unsuccessfully.
        """
        for obj in self:
            if obj.type in ('out_invoice', 'out_refund'):
                for wh_line in obj.wh_lines:
                    if not wh_line.invoice_id.write({'wh_iva_id': obj.id}):
                        return False
        return True

    @api.model
    #@api.onchange('partner_id')
    def _check_partner(self):
        """ Determine if a given partner is a VAT Withholding Agent
        """
        partner = self.env['res.partner']
        for obj in self:
            if obj.type in ('out_invoice', 'out_refund'):
                if not partner._find_accounting_partner(
                        obj.partner_id).wh_iva_agent:
                    raise exceptions.ValidationError(
                        _('The partner must be withholding vat agent .'))
            else:
                if not partner._find_accounting_partner(
                        obj.company_id.partner_id).wh_iva_agent:
                    raise exceptions.ValidationError(
                        _('The partner must be withholding vat agent .'))

    _sql_constraints = [
        ('ret_num_uniq', 'unique (type,partner_id,company_id)',
         'number must be unique by partner and document type!')
    ]

    @api.multi
    def write(self, values):
        #print("values: ", values)

        res = super(AccountWhIva, self).write(values)
        self._partner_invoice_check()
        return res

    @api.multi
    def action_move_create(self):
        """ Create movements associated with retention and reconcile
        """
        ctx = dict(self._context,
                   vat_wh=True,
                   company_id=self.env.user.company_id.id)
        for ret in self.with_context(ctx):
            for line in ret.wh_lines:
                if line.move_id or line.invoice_id.wh_iva:
                    raise exceptions.except_orm(
                        _('Invoice already withhold !'),
                        _("You must omit the follow invoice '%s' !") %
                        (line.invoice_id.name))

            # TODO: Get rid of field in future versions?
            # We rather use the account in the invoice
            #acc_id = ret.account_id.id


            if ret.wh_lines:
                for line in ret.wh_lines:
                    if line.invoice_id.type in ['in_invoice', 'in_refund']:
                        name = ('COMP. RET. IVA ' + (ret.number if ret.number else str()) + ' Doc. ' + (line.invoice_id.supplier_invoice_number if line.invoice_id.supplier_invoice_number else str()))
                    else:
                        name = ('COMP. RET. IVA ' + (ret.number if ret.number else str()) + ' Doc. ' + (line.invoice_id.number if line.invoice_id.number else str()))

                    #invoice = self.env['account.invoice'].with_context(ctx).browse(line.invoice_id.id)
                    invoice = line.invoice_id
                    amount = line.amount_tax_ret
                    #amount = self.total_tax_ret
                    account_id = line.invoice_id.account_id.id
                    journal_id = ret.journal_id.id
                    writeoff_account_id = False
                    writeoff_journal_id = False
                    date = ret.date_ret
                    name = name
                    line_tax_line = line.tax_line
                    #print('line_id', line.id)
                    wh_iva_tax_line = self.env['account.wh.iva.line.tax'].search([('wh_vat_line_id','=',line.id)])
                    #print("wh_iva_tax_line", wh_iva_tax_line )
                    ret_move = invoice.ret_and_reconcile(
                        abs(amount), account_id, journal_id,
                        writeoff_account_id,writeoff_journal_id,
                        date,name,wh_iva_tax_line)

                    if (line.invoice_id.currency_id.id !=
                            line.invoice_id.company_id.currency_id.id):
                        f_xc = self.env['l10n.ut'].sxc(
                            line.invoice_id.currency_id.id,
                            line.invoice_id.company_id.currency_id.id,
                            line.retention_id.date)
                        for ml in self.env['account.move.line'].search([('move_id','=',ret_move.id )]):
                            ml.write({
                                'currency_id': line.invoice_id.currency_id.id})

                            if ml.credit:
                                ml.write({
                                    'amount_currency': f_xc(ml.credit) * -1})

                            elif ml.debit:
                                ml.write({
                                    'amount_currency': f_xc(ml.debit)})
                    ret_move.post()
                    # make the withholding line point to that move

                    rl = {'move_id': ret_move.id}
                    lines = [(1, line.id, rl)]
                    ret.write({'wh_lines': lines})

                    if (rl and line.invoice_id.type
                            in ['out_invoice', 'out_refund']):
                        invoice.write({'wh_iva_id': ret.id})
            return True

    @api.multi
    def clear_wh_lines(self):
        """ Clear lines of current withholding document and delete wh document
        information from the invoice.
        """
        if self.ids:
            wil = self.env['account.wh.iva.line'].search([
                ('retention_id', 'in', self.ids)])

            wil_tax = self.env['account.wh.iva.line.tax'].search(
                [('wh_vat_line_id','=', wil.ids)])
            invoice = wil.mapped("invoice_id")
            if wil: wil.unlink()
            for wilt in wil_tax: wilt.unlink()
            if invoice: invoice.write({'wh_iva_id': False})

        return True

    @api.multi
    def _partner_invoice_check(self):
        """ Verify that the partner associated of the invoice is correct
        @param values: Contain withholding lines, partner id and invoice_id
        """
        partner = self.env['res.partner']
        for record in self:
            inv_str = str()
            for line in record.wh_lines:
                acc_part_id = partner._find_accounting_partner(
                    line.invoice_id.partner_id)
                if acc_part_id.id != record.partner_id.id:
                    inv_str += '%s' % '\n' + (
                        line.invoice_id.name or
                        line.invoice_id.number or '')

            if inv_str:
                raise exceptions.except_orm(
                    _('Incorrect Invoices !'),
                    _("The following invoices are not from the selected"
                      " partner: %s ") % (inv_str))

        return True
    '''
    @api.multi
    def check_wh_lines_fortnights(self):
        """ Check that every wh iva line belongs to the wh iva fortnight."""
        #period = self.env['account.period']
        error_msg = str()
        fortnight_str = {'True': ' - Second Fortnight)',
                         'False': ' - First Fortnight)'}
        for awi_brw in self:
            if awi_brw.type in ['out_invoice']:
                return True
            for awil_brw in awi_brw.wh_lines:
                awil_period_id, awil_fortnight = period.find_fortnight(
                    awil_brw.invoice_id.date_invoice)
                if awil_period_id != awi_brw.period_id.id or \
                   awil_fortnight != awi_brw.fortnight:
                    error_msg += \
                        (" * Line '" + awil_brw.invoice_id.number +
                         "' belongs to (" +
                         period.browse(awil_period_id).name +
                         fortnight_str[awil_fortnight] +
                         ".\n")
            if error_msg:
                raise exceptions.except_orm(
                    _("Invalid action !"),
                    _("Some withholding lines being withheld dont match"
                      " with the withholding document period and"
                      " fortnight.\n\n * Withholding VAT document correspond"
                      " to (" + awi_brw.period_id.name + fortnight_str[
                          awi_brw.fortnight] + ".\n\n" + error_msg))
            else:
                return True
    '''

    @api.multi
    def compute_amount_wh(self):
        """ Calculate withholding amount each line
        """
        #if self.check_wh_lines_fortnights():
        for retention in self:
            whl_ids = [line.id for line in retention.wh_lines]
            if whl_ids:
                awil = self.env['account.wh.iva.line'].browse(whl_ids)
                awil.load_taxes()
        return True

    @api.multi
    def _dummy_cancel_check(self):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True

    @api.multi
    def _check_tax_iva_lines(self):
        """Check if this IVA WH DOC is being used in a TXT IVA DOC"""
        til = self.env["txt.iva.line"].search([
            ('txt_id.state', '!=', 'draft'),
            ('voucher_id', 'in', self.ids)])

        if not til:
            return True

        note = _('The Following IVA TXT DOC should be set to Draft before'
                 ' Cancelling this Document\n\n')
        ti_ids = list(set([til_brw.txt_id.id for til_brw in til]))
        for ti_brw in self.env['txt.iva'].browse(ti_ids):
            note += '%s\n' % ti_brw.name
            raise exceptions.except_orm(_("Invalid Procedure!"), note)

    @api.multi
    def cancel_check(self):
        '''
        Unique method to check if we can cancel the Withholding Document
        '''

        if not self._check_tax_iva_lines():
            return False
        if not self._dummy_cancel_check():
            return False
        return True

    @api.multi
    def _dummy_confirm_check(self):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True

    @api.multi
    def confirm_check(self):
        '''
        Unique method to check if we can confirm the Withholding Document
        '''
        if (not self.check_wh_lines() or
                #not self.check_wh_lines_fortnights() or
                not self.check_invoice_nro_ctrl() or
                not self.check_vat_wh() or
                not self.check_wh_taxes() or
                not self.write_wh_invoices() or
                not self._dummy_confirm_check()):
            return False
        else:
            consulta = self.env['account.wh.iva'].search([('name', '=', self.name),('number_2','!=',False)])
            if not consulta:
                if self.type in ['in_invoice', 'in_refund']:
                    self.number = self.update_ret_number()
                    self.number_2 = self.number
                else:
                    self.number
            else:
                if self.type in ['in_invoice', 'in_refund']:
                    self.number = consulta[-1].number_2
            #dt = time.strftime('%Y-%m-%d')

            self.write({'date_ret': self.date_ret})
            self.action_move_create()
            self.write({'state': 'done'})
        return True

    #@api.onchange('date_ret')
    @api.multi
    def update_ret_number(self):
        local_number = self.env['ir.sequence'].next_by_code('purchase.account.wh.iva.sequence')
        if local_number and self.date_ret:
            account_month = self.date_ret.split('-')[1]
            if not account_month == local_number[4:6]:
                local_number = local_number[:4] + account_month + local_number[6:]
        return local_number
    @api.multi
    def check_wh_lines(self):
        """ Check that wh iva has lines to withhold."""
        for awi_brw in self:
            if not awi_brw.wh_lines:
                raise exceptions.except_orm(
                    _("Missing Values !"),
                    _("Missing Withholding Lines!!!"))
        return True

    @api.multi
    def copy(self, default=None):
        """ Update fields when duplicating
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        if not default:
            default = {}
        for record in self:
            if record.type == 'in_invoice':
                raise exceptions.except_orm(
                    _('Alert !'),
                    _('you can not duplicate this document!!!'))

        default.update({
            'state': 'draft',
            'number': False,
            'code': False,
            'wh_lines': [],
           # 'period_id': False
        })

        return super(AccountWhIva, self).copy(default)

    @api.multi
    def unlink(self):
        """ Overwrite the unlink method to throw an exception if the
        withholding is not in cancel state."""
        for awi_brw in self:
            if awi_brw.state != 'cancel':
                raise exceptions.except_orm(
                    _("Invalid Procedure!!"),
                    _("The withholding document needs to be in cancel state"
                      " to be deleted."))
            else:
                awi_brw.clear_wh_lines()
        return super(AccountWhIva, self).unlink()


