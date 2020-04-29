# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ , exceptions
from odoo.osv import expression
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat

"""class account_fiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = "date_start, id"

    name = fields.Char('Fiscal Year', size=64, required=True)
    code = fields.Char('Code', size=6, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('End Date', required=True),
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
    state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True, defult='dreft')

    @api.constrains('date_start','date_stop')
    def _check_duration(self):
        obj_fy = self.browse()
        if obj_fy.date_stop < obj_fy.date_start:
            raise ValidationError('Error!\nThe start date of a fiscal year must precede its end date.')
        return True

    def create_period3(self):
        return self.create_period(3)

    def create_period(self, interval=1):
        period_obj = self.env['account.period']
        for fy in self.browse():
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            period_obj.create({
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)

                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    def find(self, dt=None, exception=True):
        res = self.finds(dt, exception)
        return res and res[0] or False

    def finds(self, dt=None, exception=True):

        if not dt:
            dt = fields.date.context_todazy(self)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if self.company_id:
            company_id = self.company_id.id
        else:
            company_id = self.env.user.company_id.id
        args.append(('company_id', '=', company_id))
        ids = self.search(args)
        if not ids:
            if exception:
                raise exceptions.except_osv(_('Error!'), _('There is no fiscal year defined for this date.\nPlease create one from the configuration of the accounting menu.'))
            else:
                return []
        return ids

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        if args is None:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('code', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        ids = self.search(expression.AND([domain, args]), limit=limit)
        return self.name_get()

class account_period(models.Model):
    _name = 'account.period'
    _description = "Account period"

    PERIOD_STATE = [('draft', 'Open'), ('done', 'Closed')]

    name = fields.Char('Period Name', size=64, required=True)
    code = fields.Char('Code', size=12)
    special = fields.boolean('Opening/Closing Period', size=12, help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done': [('readonly', True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done': [('readonly', True)]})
    #TODO Check ODOO11 fiscal_year class
    #fiscalyear_id = fields.many2one('account.fiscalyear', 'Fiscal Year', required=True, states={'done': [('readonly', True)]}, select=True)
    state = fields.selection(PERIOD_STATE, 'Status', default='draft', readonly=True, help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    #TODO check ODOO11 related field syntax
    #company_id = fields.related('fiscalyear_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True)
    #TODO check how order works in ODOO11
    #_order = "date_start, special desc"
    #TODO check ODOO11 sql constarint syntax
    # _sql_constraints = [
    #     ('name_company_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
    # ]

    @api.multi
    def _check_duration(self):
        obj_period = self.browse(self._ids[0])
        if obj_period.date_stop < obj_period.date_start:
            return False
        return True

    @api.multi
    def _check_year_limit(self):
         for obj_period in self.browse(self._ids):
             if obj_period.special:
                 continue

             if obj_period.fiscalyear_id.date_stop < obj_period.date_stop or \
                             obj_period.fiscalyear_id.date_stop < obj_period.date_start or \
                             obj_period.fiscalyear_id.date_start > obj_period.date_start or \
                             obj_period.fiscalyear_id.date_start > obj_period.date_stop:
                 return False

             pids = self.search([('date_stop', '>=', obj_period.date_start), ('date_start', '<=', obj_period.date_stop),
                                 ('special', '=', False), ('id', '<>', obj_period.id)])
             for period in pids:
                 if period.fiscalyear_id.company_id.id == obj_period.fiscalyear_id.company_id.id:
                     return False
         return True
    #TODO check how _constraint work in ODOO11
   #  _constraints = [
   #      (_check_duration, 'Error!\nThe duration of the Period(s) is/are invalid.', ['date_stop']),
   #      (_check_year_limit,
   #       'Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.',
   #       ['date_stop'])
   #  ]

    @api.multi
    def next(self, period, step):
        ids = self.search([('date_start', '>', period.date_start)])
        if len(ids) >= step:
            return ids[step - 1]
        return False

    @api.multi
    def find(self, dt=None):
        if not dt:
            dt = fields.Date.today()
        args = [('date_start', '<=', dt), ('date_stop', '>=', dt), ('company_id', '=', self.env.user.company_id.id)]

        result = []
        #TODO check for account_period_prefer_normal value and how it works
        # WARNING: in next version the default value for account_periof_prefer_normal will be True
        #if context.get('account_period_prefer_normal'):
            # look for non-special periods first, and fallback to all if no result is found
        #    result = self.search(cr, uid, args + [('special', '=', False)], context=context)
        #if not result:
        result = self.search(args)
        if not result:
            raise exceptions.except_osv(_('Error!'),
                                 _('There is no period defined for this date: %s.\nPlease create one.') % dt)
        return result

    @api.multi
    def action_draft(self):
        mode = 'draft'
        for period in self.browse():
            #TODO check for ODOO11 fiscalyear process
            if period.fiscalyear_id.state == 'done':
                raise exceptions.except_osv(_('Warning!'),
                                     _('You can not re-open a period which belongs to closed fiscal year'))
        self._cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(self._ids),))
        self._cr.execute('update account_period set state=%s where id in %s', (mode, tuple(self._ids),))
        return True

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('code', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        ids = self.search(expression.AND([domain, args]), limit=limit)
        return self.name_get()

    @api.model
    def write(self, vals):
        if 'company_id' in vals:
            #TODO add account.move.line to depends
            move_lines = self.env['account.move.line'].search([('period_id', 'in', self._ids)])
            if move_lines:
                raise exceptions.except_osv(_('Warning!'), _(
                    'This journal already contains items for this period, therefore you cannot modify its company field.'))
        return super(account_period, self).write(vals)

    @api.multi
    def build_ctx_periods(self, period_from_id, period_to_id):
        if period_from_id == period_to_id:
            return [period_from_id]
        period_from = self.browse(period_from_id)
        period_date_start = period_from.date_start
        company1_id = period_from.company_id.id
        period_to = self.browse(period_to_id)
        period_date_stop = period_to.date_stop
        company2_id = period_to.company_id.id
        if company1_id != company2_id:
            raise exceptions.except_osv(_('Error!'), _('You should choose the periods that belong to the same company.'))
        if period_date_start > period_date_stop:
            raise exceptions.except_osv(_('Error!'), _('Start period should precede then end period.'))
        # /!\ We do not include a criterion on the company_id field below, to allow producing consolidated reports
        # on multiple companies. It will only work when start/end periods are selected and no fiscal year is chosen.

        # for period from = january, we want to exclude the opening period (but it has same date_from, so we have to check if period_from is special or not to include that clause or not in the search).
        if period_from.special:
            return self.search([('date_start', '>=', period_date_start), ('date_stop', '<=', period_date_stop)])
        return self.search([('date_start', '>=', period_date_start), ('date_stop', '<=', period_date_stop),
                                      ('special', '=', False)])
"""

class account_period(models.Model):
    _name = 'fiscal.book'
    _inherit = 'fiscal.book'
    _description = "Adds periods for fiscal book"

    TIME_PERIODS = [('this_month','This month'),
                    ('this_quarter','This quarter'),
                    ('this_year','This fiscal year'),
                    ('last_month','Last month'),
                    ('last_quarter','Last quarter'),
                    ('last_year','Last fiscal year'),
                    ('custom','Personalize')]

    date_start = fields.Date('Start of Period', required=True)
    date_stop = fields.Date('End of Period', required=True)
    time_period = fields.Selection(TIME_PERIODS, 'Time Periods')

    def get_time_period(self, period_type):
        dates_selected = {}
        if not period_type:
            #TODO action if ther is not any selection
            pass
            #return options
        today = date.today()
        if period_type == 'custom':
            dt_from = self.date_start
            dt_to = self.date_stop
        elif period_type == 'this_month':
            dt_from = today.replace(day=1) or False
            dt_to = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        elif period_type == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            dt_to = (today.replace(month=quarter * 3, day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            dt_from = dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year) or False
        elif period_type == 'this_year':
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(datetime.now())
            dt_from = company_fiscalyear_dates['date_from'] or False
            dt_to = company_fiscalyear_dates['date_to']
        elif period_type == 'last_month':
            dt_to = today.replace(day=1) - timedelta(days=1)
            dt_from = dt_to.replace(day=1) or False
        elif period_type == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            quarter = quarter - 1 if quarter > 1 else 4
            dt_to = (today.replace(month=quarter * 3, day=1, year=today.year if quarter != 4 else today.year - 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            dt_from = dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year) or False
        elif period_type == 'last_year':
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(datetime.now().replace(year=today.year - 1))
            dt_from = company_fiscalyear_dates['date_from'] or False
            dt_to = company_fiscalyear_dates['date_to']

        dt_from = dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        dt_to = dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT)
        dates_selected.update({'dt_from': dt_from, 'dt_to': dt_to})
        return dates_selected



