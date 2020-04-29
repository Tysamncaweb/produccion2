# -*- coding: utf-8 -*-
import locale
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pytz
from datetime import timedelta

class PosSessionDetails(models.Model):
    _name = 'pos.session.details.wizard'
    _description = 'Open Session Details Report'

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['pos.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
            SELECT
            max(start_at) as start,
            config_id
            FROM pos_session
            WHERE config_id = ANY(%s)
            AND start_at > (NOW() - INTERVAL '2 DAYS')
            GROUP BY config_id
        """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Datetime(required=True, default=_default_start_date)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    pos_config_ids = fields.Many2many('pos.config', 'pos_session_detail_configs',
        default=lambda s: s.env['pos.config'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report_session(self, data):

        if (not self.env.user.company_id.logo):
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif (not self.env.user.company_id.external_report_layout):
            raise UserError(_("You have to set your reports's header and footer layout."))

        data = {
                'ids': self.ids,
                'model': 'report.valcro_tpv_reports.session_details0',
                'form': {
                    'date_start': self.start_date,
                    'date_stop': self.end_date,
                    'config_ids': self.pos_config_ids.ids,
                },
                'context': self._context
        }
        return self.env.ref('valcro_tpv_reports.pos_session_details').report_action(self, data=data, config=False)


class ReportSessionDetails(models.AbstractModel):

    _name = 'report.valcro_tpv_reports.session_details0'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_stop = data['form']['date_stop']
        configs = data['form']['config_ids']

        if not configs:
            configs = self.env['pos.config'].search([])

        name = []
        for a in configs:
            configs_name = self.env['pos.config'].search([('id', '=', a)])
            name.append(configs_name.name)

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
            ('state', 'in', ['paid','invoiced','done']),
            ('config_id', 'in', configs)])

        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        sesion = []
        cont_session = []
        journal = []
        cont_journal = []
        session_id = []


        cont2 = 0
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id
            session_id.append({'session': order.session_id.name,
                               'amount_total': order.amount_total,
                               'pedido': order.pos_reference,
                               'caja': order.name,
                               })

            locale.setlocale(locale.LC_ALL, '')



            st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', '=', order.id)])
            cont1 = 0
            for a in st_line_ids:
                journal.append({'journal_id': a.journal_id.name,
                                'amount': a.amount,
                                'order_id': a.pos_statement_id.pos_reference,})


            for line in order.lines:
                sesion.append({
                    'product_id': line.product_id.name,
                    'price_unit': line.price_unit,
                    'price_total': line.price_subtotal_incl,
                    'qty': line.qty,
                    'discount': line.discount,
                    'tax': line.tax_ids_after_fiscal_position.tax_group_id.name,
                    'impuesto': line.order_id.amount_tax,
                    'order_id': line.order_id.pos_reference,
                    'sesion': line.order_id.session_id.name,
                })
        a = []
        c = []
        d = []
        for b in session_id:
            a.append({'session': b['session'],
                      'amount_total': locale.format_string("%f", b['amount_total'], grouping=True)[:-4],
                      'pedido': b['pedido'],
                      'caja': b['caja'],
            })
        for h in journal:
            c.append({'journal_id': h['journal_id'],
                      'amount': locale.format_string("%f", h['amount'], grouping=True)[:-4],
                      'order_id': h['order_id'],
                      })
        for j in sesion:
            d.append({
                'product_id': j['product_id'],
                'price_unit': locale.format_string("%f", j['price_unit'], grouping=True)[:-4],
                'price_total': locale.format_string("%f", j['price_total'], grouping=True)[:-4],
                'qty': str('%.f'% j['qty']).replace('.', ''),
                'discount': locale.format_string("%f", j['discount'], grouping=True)[:-4],
                'tax': j['tax'],
                'impuesto': locale.format_string("%f", j['impuesto'], grouping=True)[:-4],
                'order_id': j['order_id'],
                'sesion': j['sesion'],
            })


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_stop': date_stop,
            'session_id': a,
            'journal_id': c,
            'sesion': d,
            'configs_name': name,

        }