# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Report Account Payment',
    'version' : '2.0',
    'summary': 'Reporte que consolida los recibos de pagos con los descuentos de las retenciones de ISLR e IVA',
    'sequence': 30,
    'description': """
Reporte de pago para proveedor y cliente se agregaron las columnas de los montos
de retencion de ISLR y retenciones de IVA.
=========================================

Colaborador: Nathaly Partidas
    """,

    'category': 'Accounting',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['base_setup', 'product', 'analytic', 'web_planner', 'portal'],
    'data': [
        'report/account_payment_template.xml',

    ],
    'qweb': [
        "static/src/xml/account_reconciliation.xml",
        "static/src/xml/account_payment.xml",
        "static/src/xml/account_report_backend.xml",
        "static/src/xml/account_dashboard_setup_bar.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}