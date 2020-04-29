# coding: utf-8
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 26/11/2012
#    Version: 0.0.0.0
#
#    Description: Gets a CSV file from data collector and import it to
#                 sale order
#
##############################################################################

from odoo import fields, models
from odoo.tools.translate import _
from odoo import exceptions


class IslrWhChangeConcept(models.Model):

    _name = 'islr.wh.change.concept'


    sure= fields.Boolean('Are you Sure?')
    new_concept_id= fields.Many2one(
            'islr.wh.concept', 'New Income Wh Concept', required=True)

    def income_wh_change(self):
        context = self._context or {}
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        iwcc_brw = self.browse( ids[0])
        if not iwcc_brw.sure:
            raise exceptions.except_orm(
                _('Warning!'), _('You have to tick the "Are you Sure" Check'))
        ail_obj = self.env('account.invoice.line')
        ail_brw = ail_obj.browse(context.get('active_id'))
        inv_brw = ail_brw.invoice_id
        if inv_brw.state != 'open':
            raise exceptions.except_orm(
                _('Warning!'),
                _('This Button is meant to be used with Invoices in'
                  ' "Open State"'))

        ail_brw.write({'concept_id': iwcc_brw.new_concept_id.id})
        inv_brw.refresh()

        if inv_brw.islr_wh_doc_id:
            if inv_brw.islr_wh_doc_id.state == 'draft':
                inv_brw.islr_wh_doc_id.compute_amount_wh()
            else:
                raise exceptions.except_orm(
                    _('Warning!'),
                    _('Income Withholding from this invoice must be cancelled'
                      ' prior to change concept'))
        else:
            if (inv_brw.check_invoice_type() and
                    inv_brw.check_withholdable_concept()):
                inv_brw._create_islr_wh_doc()

        return {'type': 'ir.actions.act_window_close'}
