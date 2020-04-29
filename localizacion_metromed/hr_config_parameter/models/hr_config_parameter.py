# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HrConfigParameter(models.Model):

    _name = "hr.config.parameter"
    _description = "Store hr configuration parameters"

    key = fields.Char(string="Key", size=256, required=True, select=1)
    value = fields.Text(string="Value", required=True)

    _sql_constraints = [
        ('key_uniq', 'unique (key)', 'Key most be unique.')
    ]

    @api.multi
    def _get_param(self, key, default=False):
        """
        Retrieve the value a given key

        :param string key: The key of the parameter value to retrieve.
        :param string default: default value if parameter is missing.
        :return: The value of the parameter, or ``default`` if it does exist.
        """
        ids = self.search([('key','=',key)])
        if not ids:
            return default
        value = ids.value
        return value

    @api.multi
    def _set_param(self, key, value):
        """
        Sets the value of a parameter.

        :param string key: The key of the parameter value to set.
        :param string value: The value to set.
        :return: The previous value of the parameter or False if it did
                 no exist.
        :rtype: string
        """
        ids = self.search([('key', '=', key)])
        if ids:
            param = self.browse(ids)
            old = param.value
            self.write({'value': value})
            return old
        else:
            self.create({'key': key, 'value': value})
            return False

    @api.multi
    def _hr_get_parameter(self, parameter=None, is_string=False):
        str_value = ''
        if parameter:
            str_value = self._get_param(parameter)
            if str_value:
                str_value = str(str_value).strip()
                if not is_string:
                    if not str_value.isdigit():
                        raise ValidationError(_(u'El parámetro %s no esta correctamente configurado.\n Por favor comuníquese con el administrador del sistema')%(parameter))
            else:
                raise ValidationError(_(
                    u'El parámetro %s no esta correctamente configurado.\n Por favor comuníquese con el administrador del sistema') % (parameter))
        return str_value
    #ac = self.small_accounting_account account.account(1,)
    #self.env['account_move.line'].seacrh([('account_id','=',ac.id)])