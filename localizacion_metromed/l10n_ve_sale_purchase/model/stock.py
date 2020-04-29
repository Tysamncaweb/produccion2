# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
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
from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    #euranga07/12/2016 se realizar mejora

    @api.model
    def action_invoice_create(self, journal_id=False,
                              group=False,
                              type='out_invoice',  # pylint: disable=W0622
                              ):
        """
        Function that adds the concept of retention to the invoice_lines from
        a purchase order or sales order with billing method from picking list
        """
        if self._context is None:
            context = {}
        data = super(StockPicking, self).action_invoice_create(self, journal_id, group, type)
        # picking_id = data.keys()[0]
        # invoice_id = data[picking_id]
        invoice_brw = self.env['account.invoice'].browse(self, data)
        invoice_line_obj = self.env['account.invoice.line']
        for ail_brw in invoice_brw.invoice_line:
            invoice_line_obj.write({
                'concept_id':
                ail_brw.product_id and
                ail_brw.product_id.concept_id and
                ail_brw.product_id.concept_id.id or False})
        return data

######### Se comento porque no hace falta en el CORE ###################
  #  nro_ctrl = fields.Char(
   #         'Invoice ref.', size=32, readonly=True,
    #        states={'draft': [('readonly', False)]}, help="Invoice reference")

