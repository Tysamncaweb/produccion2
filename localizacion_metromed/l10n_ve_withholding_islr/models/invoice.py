# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
##############################################################################
from odoo import api
from odoo import fields, models
from odoo import exceptions
from odoo.tools.translate import _


class AccountInvoiceLine(models.Model):

    """ It adds a field that determines if a line has been retained or not
    """
    _inherit = "account.invoice.line"


       
    apply_wh = fields.Boolean(
            string='Withheld', default=False,
            help="Indicates whether a line has been retained or not, to"
                 " accumulate the amount to withhold next month, according"
                 " to the lines that have not been retained.")
    concept_id = fields.Many2one('islr.wh.concept', 'Concept of Islr', ondelete='cascade',  help="Concept of Income Withholding asociate this rate",
                                 default=lambda self: self.env['islr.wh.concept'].search([('name', '=', 'NO APLICA RETENCION')]))
    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'Open'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancelled'),
                              ], index=True, readonly=True, default='draft', track_visibility='onchange', copy=False,
            help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
                   " * The 'Pro-forma' status is used when the invoice does not have an invoice number.\n"
                   " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
                   " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
                   " * The 'Cancelled' status is used when user cancel invoice.")

    @api.model
    def islr_wh_change_concept(self, ids):
    
        '''Generate a new windows to change the income wh concept in current
        invoice line'''
        
        self._context = self._context or {}
        ids = isinstance(ids, (int)) and [ids] or ids
        obj_model = self.env['ir.model.data']
        ail_brw = self.browse()
        if not ail_brw.invoice_id.state == 'open':
            raise exceptions.except_orm(
                _('Warning!'),
                _('This Button is meant to be used with Invoices in'
                  ' "Open State"'))
        model_data_ids = obj_model.search(
            [('model', '=', 'ir.ui.view'),
                      ('name', '=', 'islr_wh_change_concept')])
        resource_id = obj_model.browse( model_data_ids,
                                     fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'islr.wh.change.concept',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def product_id_change(
            self, product, uom, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        """ Onchange information of the product invoice line
        at once in the line of the bill
        @param product: new product for the invoice line
        @param uom: new measuring unit of product
        @param qty: new quantity for the invoice line
        @param name: new description for the invoice line
        @param type: invoice type
        @param partner_id: partner of the invoice
        @param fposition_id: fiscal position of the invoice
        @param price_unit: new Unit Price for the invoice line
        @param currency_id:
        """
        data = super(AccountInvoiceLine, self).product_id_change(self,
            product, uom, qty, name, type, partner_id, fposition_id,
            price_unit, currency_id, company_id)
        if product:
            pro = self.env['product.product'].browse(product)
            data[data.keys()[1]]['concept_id'] = pro.concept_id.id
        return data


    @api.model
    def create(self, vals):
        """ Initialilizes the fields wh_xml_id and apply_wh,
        when it comes to a new line
        """
        context = self._context or {}
        if context.get('new_key', False):
            vals.update({'wh_xml_id': False,
                         'apply_wh': False,
                         })
        return super(AccountInvoiceLine, self).create(vals)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'


    status = fields.Selection([
            ('pro', 'Processed withholding, xml Line generated'),
            ('no_pro', 'Withholding no processed'),
            ('tasa', 'Not exceed the rate,xml Line generated'),
            ], string='Status', readonly=True, default='no_pro',
            help=''' * The \'Processed withholding, xml Line generated\' state
            is used when a user is a withhold income is processed.
            * The 'Withholding no processed\' state is when user create a
            invoice and withhold income is no processed.
            * The \'Not exceed the rate,xml Line generated\' state is
            used when user create invoice,a invoice no exceed the
            minimun rate.''')


    @api.multi
    def action_invoice_open(self):
        var = super(AccountInvoice, self).action_invoice_open()
        #if var:
        #    self._compute_retenida()
        if 'islr' in self._module and self.company_id.partner_id.islr_withholding_agent and self.partner_id.islr_withholding_agent:
            if self.state == 'open':
                for ilids in self.invoice_line_ids:
                    self.check_invoice_type()
                    self.check_withholdable_concept()
                    islr_wh_doc_id = self._create_islr_wh_doc()
                    islr_wh_doc_id and self.write({'islr_wh_doc_id': islr_wh_doc_id.id})
        return var

    # BEGIN OF REWRITING ISLR
    def check_invoice_type(self):
        """ This method check if the given invoice record is from a supplier
        """
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        inv_brw = self.browse(ids)
        return inv_brw.type in ('in_invoice', 'in_refund')

    def check_withholdable_concept(self):
        """ Check if the given invoice record is ISLR Withholdable
        """
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        '''Generate a new windows to change the income wh concept in current
        invoice line'''
        iwdi_obj = self.env['islr.wh.doc.invoices']
        return iwdi_obj._get_concepts(ids)


    @api.model
    def _create_doc_invoices(self,islr_wh_doc_id):
        """ This method link the invoices to be withheld
        with the withholding document.
        """
        # TODO: CHECK IF THIS METHOD SHOULD BE HERE OR IN THE ISLR WH DOC
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        doc_inv_obj = self.env['islr.wh.doc.invoices']
        iwhdi_ids = []
        for inv_id in ids:
            iwhdi_ids.append(doc_inv_obj.create(
                {'invoice_id': inv_id,
                 'islr_wh_doc_id': islr_wh_doc_id.id}))
        return iwhdi_ids

    @api.model
    def _create_islr_wh_doc(self):
        """ Function to create in the model islr_wh_doc
        """
        context = dict(self._context or {})
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids

        wh_doc_obj = self.env['islr.wh.doc']
        rp_obj = self.env['res.partner']

        #row = self.browse(ids)
        acc_part_id = rp_obj._find_accounting_partner(self.partner_id)

        res = False
        if self.type in ('out_refund', 'in_refund'):
            return False
        if not (self.type in ('out_invoice', 'in_invoice') and rp_obj._find_accounting_partner(self.company_id.partner_id).islr_withholding_agent):
            return True

        context['type'] = self.type
        wh_ret_code = wh_doc_obj.retencion_seq_get()

        if wh_ret_code:
            journal = wh_doc_obj._get_journal(self.partner_id)
            values = {
                'name': wh_ret_code, #TODO (REVISAR)_('IVA WH - ORIGIN %s' %(inv_brw.number)),
                'partner_id': acc_part_id.id,
             #   'period_id': row.period_id.id,
                'account_id': self.account_id.id,
                'type': self.type,
                'journal_id': journal.id,
                'date_uid': self.date_invoice,
                'company_id': self.company_id.id,
                'date_ret':self.date_invoice
            }
            if self.company_id.propagate_invoice_date_to_income_withholding:
                values['date_uid'] = self.date_invoice

            islr_wh_doc_id = wh_doc_obj.create(values)
            iwdi_id = self._create_doc_invoices(islr_wh_doc_id)

            self.env['islr.wh.doc'].compute_amount_wh([islr_wh_doc_id])


            if self.company_id.automatic_income_wh is True:
                wh_doc_obj.write(
                                 {'automatic_income_wh': True})
        else:
            raise exceptions.except_orm(_('Invalid action !'), _(
                "No se ha encontrado el numero de secuencia!"))

        return islr_wh_doc_id

    @api.multi
    def copy(self, default=None):
        """ Inicializes the fields islr_wh_doc and status
        when the line is duplicated
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        default = default or {}
        default = default.copy()
        default.update({'islr_wh_doc': True,
                        'status': 'no_pro',
                        })
        self = self._with_context(new_key=True)
        return super(AccountInvoice, self).copy(default)
    #tys_euranga se modifica la funcion colocando @api.multi

    @api.multi
    def _refund_cleanup_lines(self, lines):
        """ Initializes the fields of the lines of a refund invoice
        """
        result = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        for i, line in enumerate(lines):
            for name, field in line._fields.items():
                if name == 'concept_id' or name == 'apply_wh' or name == 'wh_xml_id':
                    result[i][2][name] = False
                #if name == 'apply_wh':
                #    result[i][2][name] = False
                #if name == 'wh_xml_id':
                #    result[i][2][name] = False
        #for xres, yres, zres in result:
        #    if 'concept_id' in zres:
        #        zres['concept_id'] = zres.get(
        #            'concept_id', False) and zres['concept_id']
        #    if 'apply_wh' in zres:
        #        zres['apply_wh'] = False
        #    if 'wh_xml_id' in zres:
        #        zres['wh_xml_id'] = 0
        #    result.append((xres, yres, zres))
        return result

    def validate_wh_income_done(self):
        """ Method that check if wh income is validated in invoice refund.
        @params: ids: list of invoices.
        return: True: the wh income is validated.
                False: the wh income is not validated.
        """
        for inv in self.browse():
            if inv.type in ('out_invoice', 'out_refund') \
                    and not inv.islr_wh_doc_id:
                rislr = True
            else:
                rislr = not inv.islr_wh_doc_id and True or \
                    inv.islr_wh_doc_id.state in (
                        'done') and True or False
                if not rislr:
                    raise exceptions.except_orm(
                        _('Error !'),
                        _('The Document you are trying to refund has a income'
                          ' withholding "%s" which is not yet validated!' %
                          inv.islr_wh_doc_id.code))
        return True
    @api.model
    def _get_move_lines(self,
                        to_wh,
                        pay_journal_id,
                        writeoff_acc_id,
                        writeoff_journal_id,
                        date,
                        name):
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
        rp_obj = self.env['res.partner']
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        res = super(AccountInvoice, self)._get_move_lines(to_wh,
                                                          pay_journal_id,
                                                          writeoff_acc_id,
                                                          writeoff_journal_id,
                                                          date,
                                                          name)

        if not context.get('income_wh', False):
            return res

        inv_brw = self.browse(ids)
        acc_part_id = rp_obj._find_accounting_partner(inv_brw.partner_id)

        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1,
                 'in_refund': -1}
        direction = types[inv_brw.type]

        for iwdl_brw in to_wh:
            rec = iwdl_brw.concept_id.property_retencion_islr_receivable
            pay = iwdl_brw.concept_id.property_retencion_islr_payable
            if inv_brw.type in ('out_invoice', 'out_refund'):
                acc = rec and rec.id or False
            else:
                acc = pay and pay.id or False
            if not acc:
                raise exceptions.except_orm(_('Missing Account in Tax!'),
                                        _("Tax [%s] has missing account. "
                                          "Please, fill the missing fields"
                                          ) % (iwdl_brw.concept_id.name,))

            res.append((0, 0, {
                'debit': direction * iwdl_brw.amount < 0 and - direction *
                                                         iwdl_brw.amount,
                'credit': direction * iwdl_brw.amount > 0 and direction *
                                                          iwdl_brw.amount,
                'account_id': acc,
                'partner_id': acc_part_id.id,
                'ref': inv_brw.number,
                'date': date,
                'currency_id': False,
                'name': name.strip() + ' - ISLR: ' + iwdl_brw.islr_wh_doc_id.code.strip()
            }))
        return res
