# -*- coding: utf-8 -*-
import locale
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pytz
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta

class ReportSaleDetails1(models.AbstractModel):

    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, configs=False):
        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        if not configs:
            configs = self.env['pos.config'].search([])

        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
        today = today.astimezone(pytz.timezone('UTC'))
        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        orders = self.env['pos.order'].search([
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_stop),
            ('state', 'in', ['paid', 'invoiced', 'done']),
            ('config_id', 'in', configs.ids)])

        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty,
                        product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount': 0.0, 'base_amount': 0.0})
                        taxes[tax['id']]['tax_amount'] += tax['amount']
                        taxes[tax['id']]['base_amount'] += tax['base']
                else:
                    taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount': 0.0, 'base_amount': 0.0})
                    taxes[0]['base_amount'] += line.price_subtotal_incl

        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                    SELECT aj.name, sum(amount) total
                    FROM account_bank_statement_line AS absl,
                         account_bank_statement AS abs,
                         account_journal AS aj 
                    WHERE absl.statement_id = abs.id
                        AND abs.journal_id = aj.id 
                        AND absl.id IN %s 
                    GROUP BY aj.name
                """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []
        name = []
        for a in configs:
            name.append(a.name)

        return {
            'currency_precision': user_currency.decimal_places,
            'total_paid': user_currency.round(total),
            'payments': payments,
            'configs_name': name,
            'company_name': self.env.user.company_id.name,
            'taxes': list(taxes.values()),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        configs = self.env['pos.config'].browse(data['config_ids'])
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], configs))
        return data


class PosPreliminarySquad(models.Model):
    _name = 'pos.preliminary.squad.wizard'
    _description = 'Open Preliminary Squad Report'

    session = fields.Many2one('pos.session', required=True)
    start_date = fields.Datetime(required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    pos_config_ids = fields.Many2one('pos.config', required=True)

    #@api.multi
    #@api.depends('start_date', 'end_date')
    #def _compute_days_pos(self):
        #DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        #hoy = date.today()

        #hoy_date = datetime.strftime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        #self.start_date = hoy_date
        #end_date = datetime.strptime(hoy_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=+1)
        #self.end_date = end_date

    '''@api.onchange('start_date', 'end_date', 'pos_config_ids')
    def caja(self):
        if self.end_date and self.start_date and self.pos_config_ids:
            formato_fecha = "%Y-%m-%d %H:%M:%S"
            DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
            #self.end_date = end_date
            start = self.start_date
            uid = self._uid
            users = self.env['pos.session'].search([('start_at', '>=', self.start_date), ('start_at', '<=', self.end_date),
                                                    ('config_id', '=', self.pos_config_ids.id), ('user_id', '=', uid)])
            #self.session = users
            a= users'''


    @api.multi
    def generate_report_preliminary_squad(self, data):
        fecha_actual = date.today()
        data = {
                'ids': self.ids,
                'model': 'report.valcro_tpv_reports.preliminary_squad_report',
                'form': {
                    'fecha_actual': fecha_actual,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'session_name': self.session.name,
                    'session': self.session.id,
                    'pos_config_ids': self.pos_config_ids.name,
                },
                'context': self._context
        }
        return self.env.ref('valcro_tpv_reports.pos_preliminary_squad').report_action(self, data=data, config=False)


class ReportSessionDetails(models.AbstractModel):

    _name = 'report.valcro_tpv_reports.preliminary_squad_report'

    @api.model
    def get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        session = data['form']['session']
        session_name = data['form']['session_name']
        fecha_actual = data['form']['fecha_actual']
        configs_name = data['form']['pos_config_ids']
        entrada = 0
        salida = 0
        cont_entrada = 0
        cont_salida = 0
        journal = []
        unico = []
        repetido = []
        total = 0
        total_efectivo = 0

        sessions = self.env['pos.session'].search([('id', '=', session)])

        #name = []
        #for a in configs:
         #   name.append(a)

        bank_statement = self.env['account.bank.statement.line'].search([('statement_id','=', sessions.cash_register_id.id)])
        for a in bank_statement:
            if a.amount > 0:
                entrada += a.amount
                cont_entrada += 1
            else:
                b = (-1)*(a.amount)
                salida += b
                cont_salida += 1

        locale.setlocale(locale.LC_ALL, '')

        subtotal = sessions.cash_register_balance_start + entrada
        subtotal_cash1 = subtotal - salida
        entrada = locale.format_string("%f", entrada, grouping=True)[:-4]
        salida = locale.format_string("%f", salida, grouping=True)[:-4]
        subtotal = locale.format_string("%f", subtotal, grouping=True)[:-4]
        subtotal_cash = locale.format_string("%f", subtotal_cash1, grouping=True)[:-4]

        orders = self.env['pos.order'].search([('session_id', '=', session)])

        for order in orders:
            st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', '=', order.id)])
            for a in st_line_ids:
                total += a.amount
                if a.journal_id.code == 'Efect':
                    total_efectivo += a.amount
                journal.append({'journal_id': a.journal_id.name,
                                'amount': a.amount,
                                'order_id': a.pos_statement_id.pos_reference,
                                'cantidad': 1,
                                })
        total_efectivo = total_efectivo + subtotal_cash1
        total_efectivo = locale.format_string("%f", total_efectivo, grouping=True)[:-4]

        for vars in journal:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('journal_id') == vars2.get('journal_id')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)

        for payment in unico:
            for metodo in repetido:
                if (payment['journal_id'] == metodo['journal_id']):
                    payment.update({'cantidad': metodo.get('cantidad') + payment.get('cantidad'),
                                    'amount': metodo.get('amount') + payment.get('amount')})
        payment = []
        for a in unico:
            payment.append({'journal_id': a['journal_id'],
                            'amount': locale.format_string("%f", a['amount'], grouping=True)[:-4],
                            'order_id': a['order_id'],
                            'cantidad': a['cantidad'],
                            })


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'end_date': end_date,
            'start_date': start_date,
            'fecha_actual': fecha_actual,
            'session': session_name,
            'movimiento': session_name[-2::1],
            'apertura': locale.format_string("%f", sessions.cash_register_balance_start, grouping=True)[:-4],
            'entrada': entrada,
            'salida': salida,
            'cont_entrada': cont_entrada,
            'cont_salida': cont_salida,
            'subtotal': subtotal,
            'subtotal_cash': subtotal_cash,
            'payment': payment,
            'total': locale.format_string("%f", total, grouping=True)[:-4],
            'total_efectivo': total_efectivo,
            'configs_name': configs_name,

        }