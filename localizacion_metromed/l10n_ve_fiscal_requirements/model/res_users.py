# coding: utf-8


from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        """To create a new record,
        adds a Boolean field to true
        indicates that the partner is a company
        """
        if self._context is None:
            context = {}
        context = dict(self._context or {})
        context.update({'create_company': True})
        self.with_context(context)
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, values):
        """ To write a new record,
        adds a Boolean field to true
        indicates that the partner is a company
        """
        context = dict(self._context or {})
        context.update({'create_company': True})
        self.with_context(context)
        return super(ResUsers, self).write(values)

ResUsers()
