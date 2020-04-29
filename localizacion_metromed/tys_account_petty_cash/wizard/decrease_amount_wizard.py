# coding: utf-8

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import Warning


class DecreaseAmountPettyCashWizard(models.TransientModel):

    """
    Wizard that decrease amount petty cash.
    """
    _name = 'decrease.amount.petty.cash.wizard'
    _description = 'Decrease amount petty cash'

    amount_decrease_petty_cash = fields.Monetary('amount decreased')
    sure = fields.Boolean('Are you sure?')
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount = fields.Monetary(string='Monto actual',
                             default=lambda self: (self.env['account.petty.cash']).browse(self._context['active_id']).petty_cash_amount_open)
    amount_new = fields.Monetary('Amount new')

    @api.onchange('amount_decrease_petty_cash')
    def _get_amount_new(self):
        self.amount_new = self.amount - self.amount_decrease_petty_cash
        return


    def validate_petty_cash_amount_open(self):
        if self.amount_decrease_petty_cash <= 0:
            raise Warning(_('El nuevo monto debe ser mayor que cero'))
        return True

    @api.multi
    def validate_petty_cash(self,petc_ids):
        '''se crea el asiento contable para crear el asiento de apertura de la caja chica'''
        petc_obj = self.env['account.petty.cash']
        petty_cash = petc_obj.browse(self._context['active_id'])
        self.validate_petty_cash_amount_open()

        vals = {
            'name': petty_cash.name,
            'date': petty_cash.petty_cash_date,
            'journal_id': petty_cash.petty_cash_journal_id.id,
            'state': 'posted',
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)
        company_id = petty_cash._get_company()

        self.move_petty_cash_ = {
            'account_id': petty_cash.petty_cash_account_id.id,
            'company_id': company_id.id,
            'currency_id': petty_cash.petty_cash_currency_id.id,
            'date_maturity': False,
            'ref': petty_cash.petty_cash_description,
            'date': petty_cash.petty_cash_date,
            # 'partner_id': self.partner_id.id,
            'move_id': move_id.id,
            'name': petty_cash.name,
            'journal_id': petty_cash.petty_cash_journal_id.id,
            'credit': self.amount_decrease_petty_cash,
            'debit': 0.0
        }

        asiento = self.move_petty_cash_
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)

        asiento['account_id'] = petty_cash.petty_cash_bank_id.default_debit_account_id.id
        asiento['credit'] = 0.0
        asiento['debit'] = self.amount_decrease_petty_cash
        move_line_id2 = move_line_obj.create(asiento)

        if move_line_id1 and move_line_id2:
            petty_cash.write({'petty_cash_status': 'validate',
                   'petty_cash_move_id': move_id.id,
                   'petty_cash_amount_open': petty_cash.petty_cash_amount_open - self.amount_decrease_petty_cash,
                   'disponible': petty_cash.petty_cash_amount_open - self.amount_decrease_petty_cash,
                   'name': petty_cash.name})
            #super(Account_petty_cash, petty_cash).write(res)
        return True

    @api.multi
    def decrease_amount(self):
        """
        Change the amount petty cash
        """

        context = self._context or {}
        ids = isinstance(self.ids, (int, int)) and [self.ids] or self.ids
        petc_obj = self.env['account.petty.cash']
        petc_ids = context.get('active_ids', [])
        data = self.browse(ids[0])
        if not data.sure:
            raise exceptions("Error!",
                "Please confirm that you want to do this by checking the option")
        if petc_ids:
            pass
            self.validate_petty_cash(petc_ids)
            #petc_obj.write(petc_ids, {'sin_cred': data.sin_cred})
        return {}

