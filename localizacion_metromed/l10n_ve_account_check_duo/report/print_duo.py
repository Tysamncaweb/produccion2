from odoo import models, fields, api



class account_issued_check(models.Model):
    _inherit = 'account.issued.check'

    literal_numb = fields.Char()
    literal_numb_1 = fields.Char()
    literal_numb_2 = fields.Char()
    day_month = fields.Char()
    years = fields.Char()

    @api.onchange('date_check_emi')
    def dates(self):
        # Calculos de Fecha
        if self.date_check_emi:
            date = self.date_check_emi.split('-')
            day = date[2]
            # Mes
            month = date[1]
            months = month.split('0')
            if months[0] == '':
                month = int(months[1])
            else:
                month = int(date[1])

            year = date[0]
            # Calculo de Mes en letras
            months = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                      9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
            month_nuc = months.get(month)
            if self.journal_id.company_id.city:
                city = self.journal_id.company_id.city
            else:
                city = 'Caracas'

            # Dia y Mes
            day_month =  str(city) + ', ' + str(day) + ' de ' + month_nuc

            return {'value': {'years': year,'day_month': day_month}}

    @api.onchange('amount')
    def literal_conversions(self):
        res = []
        cont = 0
        amount = str(self.amount)
        if amount.find('.') != -1:
            liter_amount = amount.split('.')
            for liter_amounts in liter_amount:
                cont += 1
                number_liter = self.code_literal_conversions(liter_amounts)
                number_liter = " ".join(number_liter)
                number_liter = number_liter.strip()
                if number_liter != "":
                    res.append(number_liter)
                if cont == 1:
                    con = 'con'
                    res.append(con)
                elif cont == 2:
                    if int(liter_amounts) == 0:
                        cero = 'cero'
                        res.append(cero)
                    centimos = 'centimos'
                    res.append(centimos)
            liter_amount = " ".join(res)

        if len(liter_amount) > 108:
            literal_numb_1 = []
            literal_numb_2 = []
            cont_1 = 0
            cont_2 = 0
            lis = liter_amount.split()
            for liss in lis:
                if cont_1 == 0:
                    literal_numb_1.append(liss)
                else:
                    prue = " ".join(literal_numb_1) + " " + liss
                    if len(prue) <= 108:
                        #literal_numb_1.append(" ")
                        literal_numb_1.append(liss)
                    else:
                        if cont_2 == 0:
                            literal_numb_2.append(liss)
                        else:
                            #literal_numb_2.append(" ")
                            literal_numb_2.append(liss)
                        cont_2 += 1

                cont_1 += 1

            literal_numb_1 = (" ".join(literal_numb_1)).capitalize()
            literal_numb_2 = " ".join(literal_numb_2)
        else:
            literal_numb_1 = liter_amount
            literal_numb_2 = 0
        return {'value': {'literal_numb': liter_amount,
                          'literal_numb_1':literal_numb_1,
                          'literal_numb_2':literal_numb_2}}

    def code_literal_conversions(self,num):
        """ Limite entre Numero entre 1 al 999.999.999"""

        lista = list(str(num))
        inverse, new, con, = lista[::-1], ['', '', '', '', '', '', '', '', ''], 0
        for i in inverse:
            new[con] = int(i)           # Arreglar el . ya que este codigo no agarra decimales
            con += 1
        a, b, c, d, e, f, g, h, i = new[::-1]
        if len(str(new[3])) > 0:
            new.insert(3, '.')
        if len(str(new[7])) > 0:
            new.insert(7, '.')
        numero = new[::-1]
        print('\n' + 'Resultado para: ', end='')
        for i in numero:
            print(str(i), end='')
        print()
        unidad = {1: 'un', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve',
                  0: '', '': ''}
        unidadi = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve',
                   0: '', '': ''}
        unidad2 = {10: 'diez', 11: 'once', 12: 'doce', 13: 'trece', 14: 'catorce', 15: 'quince', 16: 'diez y seis',
                   17: 'diez y siete', 18: 'diez y ocho', 19: 'diez y nueve'}
        decena = {1: 'diez', 2: 'veinte', 3: 'treinta', 4: 'cuarenta', 5: 'cincuenta', 6: 'sesenta', 7: 'setenta',
                  8: 'ochenta', 9: 'noventa', '': '', 0: ''}
        centena = {1: 'ciento', 2: 'dos cientos', 3: 'tres cientos', 4: 'cuatro cientos', 5: 'quinientos',
                   6: 'seis cientos', 7: 'setecientos', 8: 'ocho cientos', 9: 'novecientos', '': '', 0: ''}

        a = centena[a]
        if b == 1 and c < 6:
            b, c = unidad2[int(str(b) + str(c))], 'millones'
        elif c == 1:
            c, b = 'un millon', decena[b]
        elif b == 0:
            b, c = '', (unidad[c] + len(str(c)) * ' millones')
        else:
            b = (decena[b] + len(str(b)) * ' y')
            c = (unidad[c] + len(str(c)) * ' millones')
        d = centena[d]
        if e == 1 and f < 6:
            e, f = unidad2[int(str(e) + str(f))], 'mil'
        elif f == 0:
            e, f = decena[e], 'mil'
        elif e == 0:
            e, f = '', (unidad[f] + len(str(f)) * ' mil')
        else:
            e = (decena[e] + len(str(e)) * ' y')
            f = (unidad[f] + len(str(f)) * ' mil')
        g = centena[g]
        if h == 1 and i < 6:
            h, i = unidad2[int(str(h) + str(i))], ''
        elif h == 0:
            h, i = '', unidadi[i]
        else:
            if i == 0:
                i, h = '', decena[h]
            else:
                i, h = unidadi[i], decena[h] + len(str(h)) * ' y'
        orden = [a, b, c, d, e, f, g, h, i]
        return orden
"""
    @api.multi
    def print_check(self, data):

        data = {
            'id': self.id,
            'model': 'report.l10n_ve_account_check_duo.print_check_duo',
            'context': self._context
        }

        return self.env.ref('l10n_ve_account_check_duo.print_check_duo').report_action(self, data=data, config=False)"""

class PrintCheck(models.AbstractModel):

    _name = 'report.l10n_ve_account_check_duo.report_issued_check'

    @api.model
    def get_report_values(self, docids, data=None):

        data = {'form': self.env['account.issued.check'].browse(docids)}
        #id_check = docids[0]
        check = self.env['account.issued.check'].search([('id', '=', docids)])

        if check.check_endorsed == True:
            camp_endosable = 'NO ENDOSABLE'
        else:
            camp_endosable= ''


        if check.amount:
            amount = str(check.amount).split('.')
            amount = ",".join(amount)

        if check.literal_numb_2 != '0':
            fila1 = check.literal_numb_1
            fila2 = check.literal_numb_2
        else:
            fila1 = check.literal_numb_1
            fila2 = ""

        return {
            'data': data['form'],
            'model': self.env['report.l10n_ve_account_check_duo.report_issued_check'],
            'amount': amount,
            'cliente': check.receiving_partner_id.name,
            'fila1' : fila1,
            'fila2' : fila2,
            'day_month' : check.day_month,
            'year': check.years,
            'camp_endosable':camp_endosable,
        }
