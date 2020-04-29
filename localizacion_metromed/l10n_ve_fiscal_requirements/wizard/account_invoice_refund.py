# coding: utf-8
##############################################################################


import ast
import datetime, time
from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import fields


class AccountInvoiceRefund(osv.osv_memory):

    """Refunds invoice"""

    _inherit = 'account.invoice.refund'

    nro_ctrl = fields.Char(
        'Control Number', size=32,
        help="Code used for intern invoice control")

    loc_req = fields.Boolean(
        string='Required by Localization',
        default=lambda s: s._get_loc_req(),
        help='This fields is for technical use')

    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")

    '''
    def default_get(self):
       
        if context is None:
            context = {}
        res = super(AccountInvoiceRefund, self).default_get(self)
        if context.get('active_id'):
            code = datetime.datetime.today().strftime('%m/%Y')
            period_obj = self.pool.get('account.period')
            period_ids = period_obj.search([('code', '=', code)],
                                           context=context)
            period_id = period_ids and period_ids[0]

            res.update({'period': period_id})
        return res

    '''

    def _get_loc_req(self):
        """Get if a field is required or not by a Localization
        @param uid: Integer value of the user
        """
        res = False
        rc_obj = self.env['res.company']
        ru_brw = self.env['res.users'].browse(self._uid)
        rc_brw = rc_obj.browse(ru_brw.company_id.id)
        if rc_brw.country_id and rc_brw.country_id.code == 'VE':
            res = True
        return res

    #rsosa, ID 81
    def change_nro_ctrl(self,num_control):
        res={'value': {'nro_ctrl': False}}
        if not num_control:
            return False
        invoice_id = self._context.get('active_id')
        invoice_obj = self.env['account.invoice']
        partner_id = invoice_obj.browse(invoice_id).partner_id
        invoice_srch = invoice_obj.search([('type', 'in', ['in_invoice', 'out_invoice']),
                                           ('nro_ctrl', '=', num_control), ('partner_id','=',partner_id.id)])
        if len(invoice_srch) > 0:
            res.update({'warning': {'title': 'Error de Validacion', 'message': 'El Numero de Control proporcionado ya fue usado para otro documento del mismo partner'}})
        else:
            res['value']['nro_ctrl'] = num_control
        
        return res

    def _get_journal(self):
        """ Return journal depending of the invoice type
        """
        obj_journal = self.env['account.journal']
        context = self._context or {}
        journal = obj_journal.search([('type', '=', 'sale_refund')])
        if context.get('type', False):
            if context['type'] in ('in_invoice', 'in_refund'):
                journal = obj_journal.search([('type', '=', 'purchase_refund')])
        return journal and journal[0] or False


    """
    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        
        context = dict(context or {})
        journal_obj = self.pool.get('account.journal')
        res = super(AccountInvoiceRefund, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        journal_type = context.get('journal_type', 'sale_refund')
        if journal_type in ('sale', 'sale_refund'):
            journal_type = 'sale_refund'
        else:
            journal_type = 'purchase_refund'
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(
                    cr, uid, '', [('type', '=', journal_type)],
                    context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
        return res
    """

    def _get_orig(self, inv, ref):
        """ Return  default origin value
        """
        context = self._context or {}
        nro_ref = ref
        if inv.type == 'out_invoice':
            nro_ref = inv.number
        orig = ('Devolucion FACT:' + (nro_ref or '') +
                '- DE FECHA:' + (inv.date_invoice or '') +
                ' TOTAL:' + str(inv.amount_total) or '')
        return orig

    def cn_iva_validate(self, invoice):
        """
        Validates if retentions have been changes to move the state confirmed
        and done
        """
        context = self._context or {}
        ret_iva_id = False
        ret_islr_id = False
        im_obj = self.env['ir.model']
        res = im_obj.browse(im_obj.search([('model', '=', 'account.invoice')]))[0].field_id
        for i in res:
            if i.name == 'wh_iva_id':
                if invoice.wh_iva_id:
                    ret_iva_id = invoice.wh_iva_id.id
            if i.name == 'islr_wh_doc_id':
                if invoice.islr_wh_doc_id:
                    ret_islr_id = invoice.islr_wh_doc_id.id

        #Se necesita withholding_iva awi_obj = self.env['account.wh.iva']
        #Se necesita withholding_islr iwd_obj = self.env['islr.wh.doc']
        #wf_service = workflow

        #Se necesita withholding_iva
        #if ret_iva_id:
        #    awi_obj.compute_amount_wh(cr, uid, [ret_iva_id], context=context)
        #    wf_service.trg_validate(uid, 'account.wh.iva', ret_iva_id,
        #                            'wh_iva_confirmed', cr)
        #    wf_service.trg_validate(uid, 'account.wh.iva', ret_iva_id,
        #                            'wh_iva_done', cr)

        #se necesita withholding_islr
        #if ret_islr_id:
        #    iwd_obj.action_confirm1(cr, uid, [ret_islr_id], context=context)
        #    wf_service.trg_validate(uid, 'islr.wh.doc', ret_islr_id,
        #                            'act_done', cr)

        return True

    def compute_refund(self, mode='refund'):
        wzd_brw = self.browse(self._ids[0])
        inv_obj = self.env['account.invoice']
        #reconcile_obj = self.env['account.move.reconcile']
        full_reconcile_obj = self.env['account.full.reconcile']
        partial_reconcile_obj = self.env['account.partial.reconcile']
        account_m_line_obj = self.env['account.move.line']
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        #wf_service = workflow
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        res_users_obj = self.env['res.users']
        context = self._context or {}
        #for form in self.read(cr, uid, ids, context=context):
        for form in self:
            created_inv = []
            date = False
            period = False
            description = False
            nroctrl = False
            company = res_users_obj.browse(self._uid).company_id
            #journal_brw = form.get('journal_id', False)
            journal_brw = form.journal_id or False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(
                        _('Error !'),
                        _('Can not %s draft/proforma/cancel invoice.') % (
                            mode))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(
                        _('Error !'),
                        _('Can not %s invoice which is already reconciled,'
                          ' invoice should be unreconciled first. You can only'
                          ' Refund this invoice') % (mode))
                #period = form.get('period') and form.get('period')[0] or False
                #Cambie el campo periodo por el campo date para pruebas verificar el mejor proceder
                period = form.date and form.date[0] or False
                #if not period:
                        # Take period from the current date
                #    period = self.pool.get('account.period').find(
                #        cr, uid, context=context)
                #    period = period and period[0] or False
                #    if not period:
                #        raise osv.except_osv(
                #            _('No Pediod Defined'),
                #            _('You have been left empty the period field that'
                #              ' automatically fill with the current period.'
                #              ' However there is not period defined for the'
                #              ' current company. Please check in'
                #              ' Accounting/Configuration/Periods'))
                #    self.write(cr, uid, ids, {'period': period},
                #               context=context)

                if not journal_brw:
                    journal_id = inv.journal_id.id
                else:
                    #journal_id = journal_brw[0]
                    journal_id = journal_brw.id

                #if form['date']:
                if form.date:
                    date = form.date
                    #if not form.period:
                    #    self._cr.execute("select name from ir_model_fields \
                    #                        where model = 'account.period' \
                    #                        and name = 'company_id'")
                    #    result_query = self._cr.fetchone()
                    #    if result_query:
                    #        self._cr.execute(
                    #            "select p.id "
                    #            "from account_fiscalyear y, account_period p "
                    #            "where y.id=p.fiscalyear_id and date(%s)"
                    #            " between p.date_start AND p.date_stop and"
                    #            " y.company_id = %s limit 1""", (
                    #                date, company.id,))
                    #    else:
                    #        self._cr.execute("""SELECT id
                    #                    from account_period where date(%s)
                    #                    between date_start AND  date_stop  \
                    #                    limit 1 """, (date,))
                    #    res = self._cr.fetchone()
                    #    if res:
                    #        period = res[0]
                else:
                    # Take current date
                    # date = inv.date_invoice
                    date = time.strftime('%Y-%m-%d')
                if form.description:
                    description = form.description
                else:
                    description = inv.name

                if inv.type in ('in_invoice', 'in_refund'):
                    if form.nro_ctrl:
                        nroctrl = form.nro_ctrl
                    else:
                        raise osv.except_osv(
                            _('Control Number !'),
                            _('Missing Control Number on Invoice Refund!'))

                #if not period:
                #    raise osv.except_osv(_('Data Insufficient !'),
                #                         _('No Period found on Invoice!'))
                #refund_id = inv_obj.refund([inv.id], inv.date_invoice, date,
                refund_id = inv.refund(inv.date_invoice, date,
                                           description, journal_id)

                #refund = inv_obj.browse(refund_id[0])
                refund = inv_obj.browse(refund_id.id)
                # Add parent invoice
                #self._cr.execute(
                #    "update account_invoice set date_due='%s',nro_ctrl='%s',"
                #    " check_total='%s', parent_id=%s where id =%s" % (
                #        date, nroctrl, inv.check_total, inv.id, refund.id))
                self._cr.execute(
                    "update account_invoice set date_due='%s',nro_ctrl='%s',"
                    " parent_id=%s where id =%s" % (
                        date, nroctrl, inv.id, refund.id))
                #inv_obj.button_compute(refund_id)

                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids[line.account_id.id] = [line.id]
                        if not isinstance(line.reconcile_id,
                                          openerp.osv.orm.browse_null):
                            reconcile_obj.unlink(line.reconcile_id.id)
                    #era yn workflow evaluar nuevo funcionamiento
                    #wf_service.trg_validate(uid, 'account.invoice',
                    #                        refund.id, 'invoice_open', cr)

                    refund = inv_obj.browse(refund_id[0])
                    self.cn_iva_validate(refund)

                    for tmpline in refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[tmpline.account_id.id].append(
                                tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(
                            to_reconcile_ids[account],
                            writeoff_period_id=period,
                            writeoff_journal_id=inv.journal_id.id,
                            writeoff_acc_id=inv.account_id.id)
                if mode == 'modify':
                    invoice = inv_obj.read(
                        [inv.id], [
                            'name', 'type', 'number',
                            'supplier_invoice_number', 'comment', 'date_due',
                            'partner_id', 'partner_insite', 'partner_contact',
                            'partner_ref', 'payment_term', 'account_id',
                            'currency_id', 'invoice_line', 'tax_line',
                            'journal_id', 'period_id'],
                        )
                    invoice = invoice[0]
                    del invoice['id']
                    invoice_lines = inv_line_obj.browse(
                        invoice['invoice_line'])

                    invoice_lines = inv_obj._refund_cleanup_lines(
                        invoice_lines)
                    tax_lines = inv_tax_obj.browse(
                        invoice['tax_line'])
                    tax_lines = inv_obj._refund_cleanup_lines(
                        tax_lines)
                    # Add origin value
                    orig = self._get_orig(
                        inv, invoice['supplier_invoice_number'])
                    invoice.update({
                        'type': inv.type,
                        'date_invoice': date,
                        'state': 'draft',
                        'number': False,
                        'invoice_line': invoice_lines,
                        'tax_line': tax_lines,
                        'period_id': period,
                        'name': description,
                        'origin': orig,

                    })
                    for field in ('partner_id', 'account_id', 'currency_id',
                                  'payment_term', 'journal_id'):
                        invoice[field] = invoice[field] and invoice[field][0]
                    inv_id = inv_obj.create(invoice, {})
                    if inv.payment_term.id:
                        data = inv_obj.onchange_payment_term_date_invoice(
                            [inv_id], inv.payment_term.id, date)
                        if 'value' in data and data['value']:
                            inv_obj.write([inv_id], data['value'])
                    created_inv.append(inv_id)

                    new_inv_brw = inv_obj.browse(created_inv[1])
                    inv_obj.write(
                        created_inv[0],
                        {'name': wzd_brw.description,
                         'origin': new_inv_brw.origin})
                    inv_obj.write(
                        created_inv[1],
                        {'origin': inv.origin,
                         'name': wzd_brw.description})
                if inv.type in ('out_invoice', 'out_refund'):
                    xml_id = 'action_invoice_tree1'
                    # if hasattr(inv, 'sale_ids'):
                    # for i in inv.sale_ids:
                    # cr.execute('insert into sale_order_invoice_rel
                    # (order_id,invoice_id) values (%s,%s)', (i.id,
                    # refund_id[0]))
                else:
                    xml_id = 'action_invoice_tree2'
                result = mod_obj.get_object_reference('account',
                                                      xml_id)
                xml_id = result and result[1] or False
                result = act_obj.search([('id','=',xml_id)])
                invoice_domain = ast.literal_eval(result.domain)
                invoice_domain.append(('id', 'in', [created_inv[0].id]))
                result['domain'] = invoice_domain

                if wzd_brw.filter_refund == 'cancel':
                    orig = self._get_orig(inv,
                                          inv.number)
                    inv_obj.search([('id','=',created_inv[0])]).write(
                                  {'origin': orig,
                                   'name': wzd_brw.description})

                elif wzd_brw.filter_refund == 'refund':
                    orig = self._get_orig(inv,
                                          inv.number)
                    inv_obj.write(
                                  {'origin': inv.origin,
                                   'name': wzd_brw.description})
            return result



    def validate_total_payment_inv(self):
        """ Method that validate if invoice is totally paid.
        @param ids: list of invoices.
        return: True: if invoice is paid.
                False: if invoice is not paid.
        """
        res = False
        inv_obj = self.env['account.invoice']
        for inv in inv_obj.browse(self._ids):
            res = inv.reconciled
        return res

    def validate_wh(self):
        """ Method that validate if invoice has non-yet processed withholds.

        return: True: if invoice is does not have wh's or it does have and
                      those ones are validated.
                False: if invoice is does have and those wh's are not yet
                       validated.

        in the meantime this function is DUMMY,
        and the developer should use it to override and get advantage of it.
        """
        return True

    def unreconcile_paid_invoices(self, invoiceids):
        """ Method that unreconcile the payments of invoice.
        @param invoiceids: list of invoices.
        return: True: unreconcile successfully.
                False: unreconcile unsuccessfully.
        """
        inv_obj = self.env['account.invoice']
        moveline_obj = self.env['account.move.line']
        voucher_obj = self.env['account.voucher']
        res = True
        rec = []
        mid = []
        if self.validate_total_payment_inv():
            for inv in inv_obj.browse(invoiceids):
                #movelineids = inv_obj.move_line_id_payment_get([inv.id])
                movelineids = moveline_obj.search([('move_id','=',inv.move_id.id), ('account_id','=',inv.account_id.id)])
                #for moveline in moveline_obj.browse(movelineids):
                for moveline in movelineids:
                    #if moveline.reconcile_id:
                    if moveline.reconciled:
                        rec += [moveline.full_reconcile_id.id]
                    #if moveline.reconcile_partial_id:
                    #    rec += [moveline.reconcile_partial_id.id]
                #movelines = moveline_obj.search(
                #    [('|'), ('reconcile_id', 'in', rec),
                #     ('reconcile_partial_id', 'in', rec)])
                movelines = moveline_obj.search([('full_reconcile_id','in',rec)])
                #for mids in moveline_obj.browse(movelines):
                for mids in movelines:
                    mid += [mids.move_id.id]
                voucherids = voucher_obj.search([('move_id', 'in', mid)])
            if voucherids:
                voucher_obj.cancel_voucher(voucherids)
            else:
                res = False
        return res

    def invoice_refund(self):
        """ Create a invoice refund
        """
        context = self._context or {}
        inv_obj = self.env['account.invoice']
        #period_obj = self.env['account.period']
        wzr_brw = self.browse(self._ids)[0]
        date = wzr_brw.date and wzr_brw.date.split('-')
        #period = wzr_brw and wzr_brw.period and wzr_brw.period.id
        #period_ids = date and len(date) == 3 and period_obj.search(
        #    [('code', '=', '%s/%s' % (date[1], date[0]))])
        #if period not in period_ids:
        #    raise osv.except_osv(
        #        _('Error !'),
        #        _('The date should be chosen to belong to the period'))
        if not self.validate_wh():
            inv = inv_obj.browse(context.get('active_ids'))[0]
            raise osv.except_osv(
                _('Error !'),
                _('There are non-valid withholds for the document %s which'
                  ' refund is being processed!' % inv and
                  inv.wh_iva_id.code or "vacio"))
        self.unreconcile_paid_invoices(context.get('active_ids'))
        data_refund = self.browse(self._ids)[0].filter_refund
        return self.compute_refund(data_refund)

AccountInvoiceRefund()
