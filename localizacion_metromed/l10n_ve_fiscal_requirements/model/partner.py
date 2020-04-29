# coding: utf-8
##############################################################################


import re

from odoo.addons import decimal_precision as dp
from odoo import fields,models,api
from odoo.osv.orm import except_orm
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_country_code(self,ids):
        """
        Return the country code of the user company. If not exists, return XX.
        """
        user_company = self.env['res.users'].browse(self._uid).company_id
        return user_company.partner_id and user_company.partner_id.country_id \
            and user_company.partner_id.country_id.code or 'XX'

    seniat_updated = fields.Char(
        'Seniat Updated',
        help="This field indicates if partner was updated using SENIAT"
             " button")

    wh_iva_rate = fields.Float(
        string='Rate',
        digits=dp.get_precision('Withhold'),
        help="Vat Withholding rate")

    wh_iva_agent = fields.Boolean(
        'Wh. Agent',
        help="Indicate if the partner is a withholding vat agent")


    @api.model
    def default_get(self,fields_list):
        """ Load the country code of the user company to form to be created.
        """
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        context = self._context or {}
        res = super(ResPartner, self).default_get(fields_list)
        res.update({'uid_country': self._get_country_code(self)})
        return res


    '''
       def name_search(self, name='', args=None, operator='ilike', context=None,limit=80):
           """
           Gets el id of the partner with the vat or the name and return the name
           """
           if context is None:
               context = {}
           args = args or []
           ids = []
           if len(name) >= 2:
               ids = self.search(self [('vat', operator, name)] + args,
                                 limit=limit, context=context)
           if not ids:
               ids = self.search(self [('name', operator, name)] + args,
                                 limit=limit, context=context)
           return self.name_get(self, ids, context=context)
       '''


    #def _get_uid_country(self, cr, uid, ids, field_name, args, context=None):
    def _get_uid_country(self, field_name, args):
        """ Return a dictionary of key ids as invoices, and value the country code
        of the user company.
        """
        context = self._context or {}
        res = {}.fromkeys(self._ids, self._get_country_code())
        return res

    uid_country = fields.Char( type='char', string="uid_country", size=20,
            help="country code of the current company")


    #seniat_updated = False,
    #wh_iva_rate =  lambda *a: 100.0


    def _check_partner_invoice_addr(self):
        
        context = self._context or {}
        partner_obj = self.browse(self)
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE' and \
                not partner_obj.parent_id:
            res = partner_obj.type == 'invoice'
            if res:
                return True
            else:
                return False
        else:
            return True


    def _check_vat_uniqueness(self):
        

        context = self._context or {}

        user_company = self.env['res.users'].browse(self).company_id
        acc_part_brw = self._find_accounting_partner(user_company.partner_id)

        if acc_part_brw.country_id and acc_part_brw.country_id.code != 'VE':
            return True

        for rp_brw in self.browse(self):
            acc_part_brw = self._find_accounting_partner(rp_brw)
            if acc_part_brw.country_id and \
                    acc_part_brw.country_id.code != 'VE':
                continue
            elif not acc_part_brw.country_id:
                continue
            if rp_brw.id == acc_part_brw.id and not acc_part_brw.vat:
                return False
            elif rp_brw.id == acc_part_brw.id and acc_part_brw.vat:
                duplicates = self.search(self[
                    ('vat', '=', rp_brw.vat),
                    ('parent_id', '=', False), ('id', '!=', rp_brw.id)])
                if duplicates:
                    return False
                continue
        return True


    def _check_vat_mandatory(self):
        """ This method will check the vat mandatoriness in partners
        for those user logged on with a Venezuelan Company

        The method will return True when:
            *) The user's company is not from Venezuela
            *) The partner being created is the one for the a company being
               created [TODO]

        The method will return False when:
            *) The user's company is from Venezuela AND the vat field is empty
               AND:
                +) partner is_company=True AND parent_id is not NULL
                +) partner with parent_id is NULL
                +) partner with parent_id is NOT NULL AND type of address is
                   invoice
        """

        context = self._context or {}
        # Avoiding Egg-Chicken Syndrome
        # TODO: Refine this approach this is big exception
        # One that can be handle by end user, I hope so!!!
        if context.get('create_company', False):
            return True

        user_company = self.env['res.users'].browse(self).company_id
        acc_part_brw = self._find_accounting_partner(user_company.partner_id)
        # Check if the user is not from a VE Company
        if acc_part_brw.country_id and acc_part_brw.country_id.code != 'VE':
            return True

        for rp_brw in self.browse(self):
            # not use find_accounting_partner function at this point
            # because return false. Theorically can't be false
            acc_part_brw = rp_brw
            while not acc_part_brw.is_company and acc_part_brw.parent_id:
                acc_part_brw = acc_part_brw.parent_id
            if (acc_part_brw.country_id and
                    acc_part_brw.country_id.code != 'VE'):
                continue
            elif not acc_part_brw.country_id:
                continue
            if rp_brw.id == acc_part_brw.id and not acc_part_brw.vat:
                return False

        return True

    def _validate(self):
        """ Validates the fields
        """

        # In the original orm.py openerp does not allow using
        # context within the constraint because we have to yield
        # the same result always,
        # we have overridden this behaviour
        # TO ALLOW PASSING CONTEXT TO THE RESTRICTION IN RES.PARTNER
        context = self._context or {}
        lng = context.get('lang')
        trans = self.env['ir.translation']
        error_msgs = []
        for constraint in self._constraints:
            fun, msg, field_list = constraint
            # We don't pass around the context here: validation code
            # must always yield the same results.
            if not fun(self):
                # Check presence of __call__ directly instead of using
                # callable() because it will be deprecated as of Python 3.0
                if hasattr(msg, '__call__'):
                    tmp_msg = msg(self)
                    if isinstance(tmp_msg, tuple):
                        tmp_msg, params = tmp_msg
                        translated_msg = tmp_msg % params
                    else:
                        translated_msg = tmp_msg
                else:
                    translated_msg = trans._get_source(self,self._name,
                                                       'constraint', lng, msg)
                error_msgs.append(
                    _("Error occurred while validating the field(s) %s: %s") %
                    (','.join(field_list), translated_msg)
                )
                self._invalids.update(field_list)
        if error_msgs:
            raise except_orm('ValidateError', '\n'.join(error_msgs))
        else:
            self._invalids.clear()
    '''
    _sql_constraints =[
        (_check_vat_mandatory,
         _("Error ! VAT is mandatory in the Accounting Partner"),
         ['country_id', 'vat']),
        (_check_vat_uniqueness,
         _("Error ! Partner's VAT must be a unique value or empty"), []),
        # (_check_partner_invoice_addr,
        #  _('Error ! The partner does not have an invoice address.'), []),
    ]
    '''

    def vat_change_fiscal_requirements(self, value):
        """ Checks the syntax of the vat
        """
        context = self._context or {}
        if not value:
            return super(ResPartner, self).vat_change(value)
        res = self.search(self [('vat', 'ilike', value)])
        if res:
            rp = self.browse(self,res[0])
            return {'warning': {
                'title': _('Vat Error !'),
                'message': _('The VAT [%s] looks like ' % value +
                             '[%s] which is' % rp.vat.upper() +
                             ' already being used by: %s' % rp.name.upper())
            }
            }
        else:
            return super(ResPartner, self).vat_change(self, value)

    def check_vat_ve(self, vat):
        """ Check Venezuelan VAT number, locally called RIF.
        RIF: JXXXXXXXXX RIF VENEZOLAN
             IDENTIFICATION CARD: VXXXXXXXXX
             FOREIGN IDENTIFICATION CARD: EXXXXXXXXX
        """

        context = self._context or {}
        if re.search(r'^[VJEGP][0-9]{9}$', vat):
            return True
        if re.search(r'^([VE][0-9]{1,8}|[D][0-9]{9})$', vat):
            return True
        return False

    def vies_vat_check(self, country_code, vat_number):
        """
        Validate against  VAT Information Exchange System (VIES)
        """
        if country_code.upper() != "VE":
            return super(ResPartner, self).vies_vat_check(country_code, vat_number)
        else:
            return super(ResPartner, self).simple_vat_check(country_code, vat_number)

    def update_rif(self):
        """ Load the rif and name of the partner from the database seniat
        """
        context = self._context or {}
        su_obj = self.env['seniat.url']
        return su_obj.update_rif(self)

    def button_check_vat(self):
        """ Is called by the button that load information of the partner from database
        SENIAT
        """
        context = dict(self._context or {})
        context.update({'update_fiscal_information': True})
        super(ResPartner, self).check_vat(self)
        user_company = self.env['res.users'].browse(self).company_id
        if user_company.vat_check_vies:
            # force full VIES online check
            self.update_rif(self)
        return True
