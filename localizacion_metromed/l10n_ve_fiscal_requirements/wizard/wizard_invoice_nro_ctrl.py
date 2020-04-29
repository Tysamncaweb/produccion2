# coding: utf-8


from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models,fields


class WizardInvoiceNroCtrl(osv.osv_memory):

    _name = "wizard.invoice.nro.ctrl"

    invoice_id = fields.Many2one(
            'account.invoice', 'Invoice',
            help="Invoice to be declared damaged.")

    date = fields.Date('Date',help="Date used for declared damaged paper. Keep empty to use the")

    sure =  fields.Boolean('Are You Sure?')


    def action_invoice_create(self,wizard_brw, inv_brw):

        """
        If the invoice has control number, this function is responsible for
        passing the bill to damaged paper
        @param wizard_brw: nothing for now
        @param inv_brw: damaged paper
        """
        invoice_line_obj = self.env['account.invoice.line']
        invoice_obj = self.env['account.invoice']
        acc_mv_obj = self.env['account.move']
        acc_mv_l_obj = self.env['account.move.line']
        tax_obj = self.env['account.invoice.tax']
        uid = self._uid
        res_company = self.env['res.company'].search([('id','=',uid)])
        if inv_brw.nro_ctrl:
            invoice = ({
                'name': 'PAPELANULADO_NRO_CTRL_%s' % (
                    inv_brw.nro_ctrl and inv_brw.nro_ctrl or ''),
            })
            invoice = invoice
            inv_brw = inv_brw.id
            invoice_obj.browse(inv_brw).write(invoice)
        else:
            raise osv.except_osv(
                _('Validation error!'),
                _("You can run this process just if the invoice have Control"
                  " Number, please verify the invoice and try again."))

        invoice_line_obj = invoice_line_obj.search([('invoice_id', '=', inv_brw)])
        for line in invoice_line_obj:
            id = line.id
            invoice_line = ({
                'quantity': 0.00,
                'invoice_line_tax_id': [],
                'price_unit': 0.00})
            invoice_line_obj.browse(id).write(invoice_line)
        tax_ids = self.env['account.tax'].search([])
        tax = tax_obj.search([('invoice_id', '=', inv_brw)])
        if tax:
            tax_obj.browse(tax.id).write({'invoice_id': []})
        invoice_tax = {
                'name': 'SDCF',
                'tax_id': tax_ids and tax_ids[0].id,
                'amount': 0.00,
                'base': 0.00,
                'account_id': res_company.acc_id.id,
                'invoice_id': inv_brw
        }

        invoice_tax = invoice_tax
        tax_obj.create(invoice_tax)

        move_id = invoice_obj.browse(inv_brw)
        move_id = move_id.move_id.id
        if move_id:
            acc_mv_obj.browse(move_id).button_cancel()
            acc_mv_obj.browse(move_id).write({'ref': 'Damanged Paper','amount':0.00})
            for i in acc_mv_l_obj.search([('move_id','=', move_id)]):
                id =i.id
                sql = "UPDATE account_move_line set debit = 0.00,credit = 0.00,balance = 0.00,debit_cash_basis = 0.00,credit_cash_basis = 0.00,balance_cash_basis = 0.00,amount_residual = 0.00,tax_base_amount = 0.00 WHERE id = %s" % (id)
                self._cr.execute(sql)

            invoice_ob = invoice_obj.browse(inv_brw).id
            if invoice_ob:
                sql = "UPDATE account_invoice set state = 'paid' ,residual = 0.00 , residual_signed = 0.00 , residual_company_signed = 0.00 WHERE id = %s" % (invoice_ob)
                self._cr.execute(sql)

        return inv_brw

    def new_open_window(self, list_ids, xml_id, module):
        """ Generate new window at view form or tree
        """
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj._get_id(module, xml_id)
        imd_id = mod_obj.browse(result).res_id
        result = act_obj.search_read([('id','=',imd_id)])[0]
        result['res_id'] = list_ids
        return result


    def create_invoice(self):
        """ Create a invoice refund
        """
        context = self._context or {}
        wizard_brw = self.browse(self._ids)
        inv_id = self._context.get('active_id')
        for wizard in wizard_brw:
            if not wizard.sure:
                raise osv.except_osv(
                    _("Validation error!"),
                    _("Please confirm that you know what you're doing by"
                      " checking the option bellow!"))
            if (wizard.invoice_id and wizard.invoice_id.company_id.jour_id and
                    wizard.invoice_id and wizard.invoice_id.company_id.acc_id):
                inv_id = self.action_invoice_create(wizard,wizard.invoice_id)
            else:
                raise osv.except_osv(
                    _('Validation error!'),
                    _("You must go to the company form and configure a journal"
                      " and an account for damaged invoices"))
        return self.new_open_window([inv_id],'action_invoice_tree1', 'account')

WizardInvoiceNroCtrl()
