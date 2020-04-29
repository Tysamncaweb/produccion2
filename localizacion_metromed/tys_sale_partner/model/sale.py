# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



from odoo import api, exceptions, fields, models, _

class sale_order(models.Model):
    _inherit = "sale.order"

    # modificacion para incluir en la vista RIF y codigo de Cliente
    vat_partner = fields.Char('RIF Cliente')        #TODO colocar el campo como requerido en la vista
    code_partner = fields.Char('Codigo Cliente')    #TODO colcoar el campo como requerido en la vista

    #Permite agregar el rif y codigo al momento de seleccionar el cliente
    @api.onchange()
    def onchange_partner_id(self, part):
        if part:
            part = self.env['res.partner'].browse(part)
            addr = self.env['res.partner'].address_get([part.id], ['delivery', 'invoice', 'contact'])
            pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
            invoice_part = self.env['res.partner'].browse(addr['invoice'])
            payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
            dedicated_salesman = part.user_id and part.user_id.id or self.uid
            self.partner_invoice_id = addr['invoice']
            self.partner_shipping_id = addr['delivery']
            self.payment_term = payment_term
            self.user_id = dedicated_salesman
            self.vat_partner = part['vat']
            self.code_partner = part['code']
            self.delivery_onchange = self.onchange_delivery_id(False, part.id, addr['delivery'], False)
            if pricelist:
                self.pricelist_id = pricelist
            if not self._get_default_section_id() and part.section_id:
                self.section_id = part.section_id.id
            sale_note = self.get_salenote(part.id)
            if sale_note: self.note = sale_note
        else:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
            self.payment_term = False
            self.fiscal_position = False
            self.vat_partner = False
            self.code_partner = False


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'

    brand = fields.many2one('brand.brand', 'Brand', related="product_id.brand") #TODO Verificar sinntaxis de campo reñlated en ODOO 11
