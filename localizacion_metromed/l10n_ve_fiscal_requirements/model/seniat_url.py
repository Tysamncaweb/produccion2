# coding: utf-8


import logging
import re
import urllib
from xml.dom.minidom import parseString

from odoo import fields,models
from odoo.tools.translate import _


class SeniatUrl(models.Model):

    """ OpenERP Model : seniat_url
    """
    _name = 'seniat.url'
    _description = "Seniat config needed to run auto-config partner"
    logger = logging.getLogger('res.partner')

    name = fields.Char (
            'URL Seniat for Partner Information', size=255,
            required=True, readonly=False,
            help='''In this field enter the URL from Seniat for search the
            fiscal information from partner''')

    url_seniat = fields.Char(
            'URL Seniat for Retention Rate',
            size=255, required=True, readonly=False,
            help='''In this field enter the URL from Seniat for search the
            retention rate from partner (RIF)''')

    url_seniat2 = fields.Char(
            'URL Seniat for Retention Rate',
            size=255, required=True, readonly=False, help='''In this field enter
            the URL from Seniat for search the retention rate from partner
            (CI or Passport)''')


    #    Update Partner Information

    def _get_valid_digit(self,vat, context=None):
        '''
        @param vat: string
        returns validating digit
        '''
        divisor = 11
        vat_type = {'V': 1, 'E': 2, 'J': 3, 'P': 4, 'G': 5}
        mapper = {1: 3, 2: 2, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2}
        valid_digit = None

        vat_type = vat_type.get(vat[0].upper())
        if vat_type:
            sum_vat = vat_type * 4
            for i in range(8):
                sum_vat += int(vat[i + 1]) * mapper[i + 1]

            valid_digit = divisor - sum_vat % divisor
            if valid_digit >= 10:
                valid_digit = 0
        return valid_digit

    def _validate_rif(self, vat, context=None):
        '''validates if the VE VAT NUMBER is right
        @param vat: string: Vat number to Check
        returns vat when right otherwise returns False

        '''
        if not vat:
            return False

        if 'VE' in vat:
            vat = vat[2:]

        if re.search(r'^[VJEGP][0-9]{9}$', vat):
            valid_digit = self._get_valid_digit(vat, context=context)
            if valid_digit is None:
                return False
            if int(vat[9]) == valid_digit:
                return vat
            else:
                self._print_error(_('Vat Error !'), _('Invalid VAT!'))
        elif re.search(r'^([VE][0-9]{1,8})$', vat):
            vat = vat[0] + vat[1:].rjust(8, '0')
            valid_digit = self._get_valid_digit( vat, context=context)
            vat += str(valid_digit)
            return vat
        return False

    def _load_url(self, retries, url):
        """ Check that the seniat url is loaded correctly
        """
        str_error = '404 Not Found'
        while retries > 0:
            try:
                url_obj = urllib.urlopen(url)
                url_str = url_obj.read()
                ok = '404 Not Found' not in url_str
                if ok:
                    log_msg = "Url Loaded correctly %s" % url
                    self.logger.info(log_msg)
                    return url_str

            except  ValueError as e:
                if e.errno == 101:
                    log_msg = "Url could not be loaded %s" % str_error
                    self.logger.warning(log_msg)
                else:
                    log_msg = "This is a unspected error %s" % str_error
                    self.logger.warning(log_msg)
            retries -= 1
        return str_error

    def _parse_dom(self, dom, rif, context=None):
        """
        This function extracts the information partner of the string and
        returns
        """
        context = context or {}
        rif_aux = dom.childNodes[0].getAttribute('rif:numeroRif')
        name = dom.childNodes[0].childNodes[0].firstChild.data
        wh_agent = dom.childNodes[0].childNodes[
            1].firstChild.data.upper() == 'SI' and True or False
        vat_subjected = dom.childNodes[0].childNodes[
            2].firstChild.data.upper() == 'SI' and True or False
        wh_rate = dom.childNodes[0].childNodes[3].firstChild.data
        log_msg = "rif: %s found" % rif
        self.logger.info(log_msg)
        if name.count('(') > 0:
            name = name[:name.index('(')].rstrip()
        return {'name': name,
                'vat_subjected': vat_subjected,
                'vat': 'VE' + rif_aux,
                'wh_iva_rate': wh_rate,
                'wh_iva_agent': wh_agent}

    def _print_error(self, error, msg):
        """ Shows an error on the screen
        """
        raise self.except_osv(error, msg)

    def _eval_seniat_data(self, xml_data, vat, context=None):
        """ Returns false when there was no error in the query in url SENIAT and
        return true when there was error in the query.
        """
        context = context or {}
        if not context.get('all_rif'):
            if xml_data.find('450') >= 0 and not vat.find('450') >= 0:
                self._print_error(_('Vat Error !'), _('Invalid VAT!'))
            elif xml_data.find('452') >= 0 and not vat.find('452') >= 0:
                self._print_error(_('Vat Error !'), _('Unregistered VAT!'))
            elif xml_data.find("404") >= 0 and not vat.find('404') >= 0:
                self._print_error(_('No Connection !'), _(
                    "Could not connect! Check the URL "))
            else:
                return False
        else:
            if xml_data.find('450') >= 0 or xml_data.find('452') >= 0 or \
                    xml_data.find("404") >= 0:
                return True
            else:
                return False

    def _get_rif(self,vat, url1, url2, context=None):
        """ Partner information transforms XML to string and returns.
        """
        if context is None:
            context = {}

        xml_data = self._load_url(3, url1 % vat)
        if not self._eval_seniat_data(xml_data, vat, context=context):
            dom = parseString(xml_data)
            return self._parse_dom( vat, url2, context=context)

    def check_rif(self, vat):
        context = self._context or {}
        return self._dom_giver(vat)

    def _dom_giver(self,vat, context):
        """ Check and validates that the vat is a passport,
        id or rif, to send information to SENIAT and returns the
        partner info that provides.
        """
        if context is None:
            context = {}

        url_obj = self.browse(self.search(self._cr, self._uid, []))[0]
        url1 = url_obj.name + '%s'
        url2 = url_obj.url_seniat + '%s'
        vat = self._validate_rif(vat, context=None)
        if vat:
            return self._get_rif(vat, url1, url2,context)
        else:
            return False

    def _update_partner(self, context):
        """ Indicates that the partner was updated with information provided by seniat
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        rp_obj = self.env['res.partner']
        rp_obj.write({'seniat_updated': True})

    def update_rif(self, context=None):
        """ Updates the partner info if it have a vat
        """
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        if context.get('exec_wizard'):
            res = self._dom_giver(self, context['vat'],context)
            if res:
                self._update_partner(context)
                return res
            else:
                return False
        for partner in rp_obj.browse(self):
            if not partner.vat or partner.vat[:2] != 'VE':
                continue
            rp_obj.write(self, partner.id, {'seniat_updated': False})

            try:
                res = self._dom_giver(self, partner.vat[2:],context)
            except self.except_osv:
                continue

            if res:
                rp_obj.write(self, partner.id, res)
                self._update_partner(partner.id)
            else:
                if not context.get('all_rif'):
                    return False
        return True

    def connect_seniat(self,context=None, all_rif=False):
        """ Adds true value to the field all_rif to denote that rif was charged with
        SENIAT database
        """
        context = context or {}
        ctx = context.copy()
        if all_rif:
            ctx.update({'all_rif': True})
        self.update_rif(context=ctx)
        return True
