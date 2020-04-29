#-*- coding:utf-8 -*-
import csv

XML_HEADER = """<?xml version="1.0" encoding="utf-8"?>"""
ODOO_TAG_OPEN = """    <odoo>"""
ODOO_TAG_CLOSE = """    </odoo>"""
DATA_TAG_OPEN = """        <data noupdate="1">"""
DATA_TAG_CLOSE = """        </data>"""
RECORD_OPEN_TAG = """            <record model="%s" id="%s">"""
RECORD_CLOSE_TAG = """            </record>"""

def add_header():
    xml_header = XML_HEADER + '\n' + ODOO_TAG_OPEN + '\n' + DATA_TAG_OPEN
    xml_body_init = """            <record model="account.account.template" id="account_activa_account_1129003">
                <field name="code">1129003</field>
                <field name="name">TRANSFERENCIAS BANCARIAS</field>
                <field name="reconcile" eval="True"/>
                <field name="user_type_id" ref="account.data_account_type_current_assets"/>
            </record>

            <record id="ve_chart_template_amd" model="account.chart.template">
                <field name="name">Venezuelan - Account</field>
                <field name="code_digits">8</field>
                <field name="currency_id" ref="base.VEF"/>
                <field name="transfer_account_id" ref="account_activa_account_1129003"/>
            </record>
            <!--
                Chart of account
            -->"""
    return xml_header + '\n' + xml_body_init + '\n'

def add_footer():
    xml_footer = DATA_TAG_CLOSE + '\n' + ODOO_TAG_CLOSE
    return xml_footer

def convert_row(row, names=None):

    xml_str = """            <record model="account.account.template" id="account_activa_account_1129003">
                <type>%s</type>
                <format>%s</format>
                <year>%s</year>
                <rating>%s</rating>
                <stars>%s</stars>
                <description>%s</description>
            </movietitle>""" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6])


    return xml_str

f = open('/home/programador4/Documentos/movies2.csv')
csv_f = csv.reader(f)
data = []

for row in csv_f:
   data.append(row)
f.close()

#print data
#print "*****"
#print data[1:]
#print "*****"
#print add_header() + '\n'.join([convert_row(row) for row in data[1:]]) + '\n' + add_footer()
