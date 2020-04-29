# -*- coding: utf-8 -*-
##############################################################################
#
#    autor: Tysamnca.
#
##############################################################################
from odoo import  api, fields, models, _,exceptions

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def copy(self, default=None):
        """ Initialized fields to the copy a register
                """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        default = default or {}
        default = default.copy()
        default.update({'wh_local': False, 'wh_muni_id': False})
        return super(AccountInvoice, self).copy(default)

    def _get_move_lines(self,to_wh, journal_id, writeoff_account_id, writeoff_journal_id,date,name):
        """ Generate move lines in corresponding account
        @param to_wh: whether or not withheld
        @param period_id: Period
        @param pay_journal_id: pay journal of the invoice
        @param writeoff_acc_id: account where canceled
        @param writeoff_period_id: period where canceled
        @param writeoff_journal_id: journal where canceled
        @param date: current date
        @param name: description
        """
        context = self._context or {}
        res = super(AccountInvoice, self)._get_move_lines(to_wh, journal_id, writeoff_account_id, writeoff_journal_id,date,name)
        rp_obj = self.env['res.partner']
        if context.get('muni_wh', False):
            invoice = self.browse()
            acc_part_brw = rp_obj._find_accounting_partner(
                to_wh.invoice_id.partner_id)
            types = {
                'out_invoice': -1,
                'in_invoice': 1,
                'out_refund': 1,
                'in_refund': -1
            }
            direction = types[invoice.type]
            if self.to_wh.retention_id.type == 'in_invoice':
                acc = acc_part_brw.property_wh_munici_payable and \
                    acc_part_brw.property_wh_munici_payable.id or False
            else:
                acc = acc_part_brw.property_wh_munici_receivable and \
                    acc_part_brw.property_wh_munici_receivable.id or False
            if not acc:
                raise exceptions.except_orm(
                    _('Missing Local Account in Partner!'),
                    _("Partner [%s] has missing Local account. Please, fill"
                      " the missing field") % (acc_part_brw.name,))
            res.append((0, 0, {
                'debit': direction * to_wh.amount < 0 and
                (-direction * to_wh.amount),
                'credit': direction * to_wh.amount > 0 and
                direction * to_wh.amount,
                'partner_id': acc_part_brw.id,
                'ref': invoice.number,
                'date': date,
                'currency_id': False,
                'name': name,
                'account_id': acc,
            }))
            self.residual = self.residual + direction * to_wh.amount
            self.residual_company_signed = self.residual_company_signed + direction * to_wh.amount
        return res

    def _retenida_munici(self):

        context = self._context or {}
        res = {}
        for inv_id in self.ids:
            res[inv_id] = self.test_retenida_muni()
        return res

    def _get_inv_munici_from_line(self):
        context = self._context or {}
        move = {}
        aml_brw = self.env['account.move.line'].browse(self)
        for line in aml_brw:
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(self,
                 [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def _get_inv_munici_from_reconcile(self):
        context = self._context or {}
        move = {}
        amr_brws = self.env['account.move.reconcile'].browse(self)
        for amr_brw in amr_brws:
            for line in amr_brw.line_partial_ids:
                move[line.move_id.id] = True
            for line in amr_brw.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.env['account.invoice'].search(
                self, [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def test_retenida_muni(self):
        type2journal = {'out_invoice': 'mun_sale',
                        'out_refund': 'mun_sale',
                        'in_invoice': 'mun_purchase',
                        'in_refund': 'mun_purchase'}
        type_inv = self.browse().type
        type_journal = type2journal.get(type_inv, 'mun_purchase')
        res = self.ret_payment_get()
        if not res:
            return False
        ok = True

        self.env.cr.execute('select l.id'
                   ' from account_move_line l'
                   ' inner join account_journal j on (j.id=l.journal_id)'
                   ' where l.id in (' + ','.join(
                       [str(item) for item in res]) + ') and j.type=' +
                   '\'' + type_journal + '\'')
        ok = ok and bool(self.env.cr.fetchone())
        return ok

    def action_cancel(self):
        """ Verify first if the invoice have a non cancel local withholding doc.
        If it has then raise a error message. """
        #context = self._context or {}
        for inv_brw in self.browse():
            if inv_brw.wh_muni_id:
                raise exceptions.except_orm(
                    _("Error!"),
                    _("You can't cancel an invoice that have non cancel"
                      " Local Withholding Document. Needs first cancel the"
                      " invoice Local Withholding Document and then you can"
                      " cancel this invoice."))
        return super(AccountInvoice, self).action_cancel()

    # Sobreescritura del metodo create(Para mostrar el valor del impuesto municipal en la vista tree de la factura)
    # Se comentaron ambos metodos porque se realizo la función sobreescribiendo el metodo action_invoice_open
    """@api.model
    def create(self, values):
        record = super(AccountInvoice, self).create(values)
        for ti in record.tax_line_ids:
            if ti.tax_id.type_tax == 'municipal':
                record.amount_muni = ti.amount
        return record

    # Sobreescritura del metodo write(Para mostrar el valor del impuesto municipal en la vista tree de la factura) Da error, se queda en el bucle for
    @api.multi
    def write(self, values):
        for to in self.tax_line_ids:
            if to.tax_id.type_tax == 'municipal':
                self.amount_muni = to.amount
        return super(AccountInvoice, self).write(values)"""

    @api.multi
    def action_invoice_open(self):
        var = super(AccountInvoice, self).action_invoice_open()
        for var in self.tax_line_ids:
            if var.tax_id.type_tax == 'municipal':
                self.amount_muni = var.amount
        return var


    wh_local = fields.Boolean(string='Local Withholding', compute='_retenida_munici', store=True,
                              help="The account moves of the invoice have been withheld with \account moves of the payment(s).")
    wh_muni_id = fields.Many2one('account.wh.munici', 'Wh. Municipality', readonly=True, help="Withholding muni.")

    amount_muni = fields.Monetary(string='Impuesto Municipal')

