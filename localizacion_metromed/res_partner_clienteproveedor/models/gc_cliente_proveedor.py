# -*- coding: UTF-8 -*-
#    type of the change:  Created
#    Comments: Creacion de generacion de codigo para clientes y proveedores (depends for res_partner)



from odoo import fields, models, api,exceptions
import re

class gc_cliente_proveedor(models.Model):
    _inherit = 'res.partner'


    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        if self._context.get('contact'):

            if view_type == 'tree':
                view_id = self.env['ir.ui.view'].search( [('name', '=', 'view_contact_tree')], limit=1)


            elif view_type == 'form':
                view_id = self.env['ir.ui.view'].search([('name', '=', 'res.contacts.form')], limit=1)

            if view_id:
                return super(gc_cliente_proveedor, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        return super(gc_cliente_proveedor, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
       # return super(gc_cliente_proveedor, self).fields_view_get()

    def validate_rif_er(self, field_value):
        res = {}

        rif_obj = re.compile(r"^VE[V|E|J|G][\d]{9}", re.X)
        if rif_obj.search(field_value.upper()):
            res = {
                'vat':field_value
            }
        return res

    @api.multi
    def write(self, vals):
        res = {}
        if vals.get('vat'):
            res =self.validate_rif_er(vals.get('vat', False))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678, VEE012345678, VEJ012345678 o VEG012345678. Por favor intente de nuevo'))
            if not self.validate_rif_duplicate(vals.get('vat', False)):
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'El cliente o proveedor ya se encuentra registrado con el rif: %s') % (
                                                vals.get('vat', False)))
        res = super(gc_cliente_proveedor, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = {}

        if vals.get('vat'):
            res =self.validate_rif_er(vals.get('vat'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678, VEE012345678, VEJ012345678 o VEG012345678. Por favor intente de nuevo'))
            if not self.validate_rif_duplicate(vals.get('vat', False), True):
                raise exceptions.except_orm(('Advertencia!'),
                    (u'El cliente o proveedor ya se encuentra registrado con el rif: %s y se encuentra activo') % (
                    vals.get('vat', False)))
        res = super(gc_cliente_proveedor, self).create(vals)
        return res

    def validate_rif_duplicate(self, valor, create=False):
            found = True
            partner = self.search([('vat', '=', valor)])
            if create:
                if partner and (partner.customer or partner.supplier):
                    found = False
            elif partner and (self.customer or self.supplier):
                found = False

            return found

    @api.constrains('vat', 'commercial_partner_country_id')
    def check_vat(self):
        var =0
        #Esto reemplaza la original porque este cliente queria el rif con el formato que se sugiere en la funcion validate_rif_er de este modulo.
'''
    _constraints = [
        (validar_rif_d, "El RIF que esta intentando ingresar ya existe", ['vat']),
        (validar_ci, "La CI que esta intentando ingresar ya existe", ['ci']),
    ]
gc_cliente_proveedor()
'''


