# coding: utf-8
from odoo import models, fields, api, _

class hr_employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee Studies"


    active_studies = fields.Boolean("Estudia Actualmente")
    career_id = fields.Many2one('hr.career', 'Carrera')
    institution_id = fields.Char("Institución", size=100)
    #lang_id = fields.Many2one('res.lang', 'Idiomas')
    languages = fields.Boolean(string="Languages")
    languages_id = fields.One2many('hr.languages', 'employee_id', 'Idiomas')
    courses = fields.Boolean(string="Cursos")
    courses_ids = fields.One2many('hr.course', 'employee_id', 'Cursos')
    stadies = fields.Boolean(string="Estudios")
    studies_ids = fields.One2many('hr.stadies', 'employee_id', 'Estudios')


class hr_carrera(models.Model):

    @api.multi
    def _get_carrera_position(self):
        res = []
        for employee in self:
            if employee.carrera_id:
                res.append(employee.carrera_id.id)
        return res

    _name = "hr.career"
    _description = "Carrera Description"

    name = fields.Char('Carrera Name', size=128, required=True, select=True)
    #employee_ids = fields.One2many('hr.employee', 'career_id', 'Employees')



class hr_curso(models.Model):
    _name = "hr.course"

    name_instituto = fields.Char(string="Institucion", size=256)
    name_curso = fields.Char(string="Nombre del Curso", size=256)
    name_titulo = fields.Char(string="Titulo o Certificado", size=256)
    duracion = fields.Char(string="Duracion", size=60)
    graduado = fields.Boolean(string="Graduado", defaults=False)
    date_culminacion = fields.Date(string="Fecha de Culminacion")
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")


   # _defaults = {
    #    'graduado': False,
    #}

class hr_estudio (models.Model):

    _name = "hr.stadies"

    name_nivel = fields.Selection([('educacion_basica', 'Educación Basica'),
             ('bachiller', 'Bachiller'),
             ('tecnico_medio', 'Tecnico Medio'),
             ('tsu','T.S.U.'),
             ('universitario', 'Universitario'),
             ('licenciado', 'Licenciado'),
             ('maestria', 'Maestria'),
             ('doctorado', 'Doctorado'),
             ('postdoctorado', 'Postdoctorado')
                                   ],
                                  'Nivel Educativo')
    name_institute = fields.Char(string="Colegio/Institucion", size=256)
    anos_aprobado = fields.Integer(string="Años Aprobados", size=256)
    si_graduado = fields.Boolean(string="Graduado")
    fecha_culminacion = fields.Date(string="Fecha de Culminacion")
    nombre_titulo = fields.Char('Titulo o Certificado Obtenido')
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")

class hr_languages(models.Model):
    _name = "hr.languages"
    _description = "Employee Languages"

    LEVELS = [('basic','Basic'),('intermediate', 'Intermediate'),('advance','Advance')]
    lang_id = fields.Many2one('res.lang', 'Idiomas')
    writing = fields.Selection(LEVELS,string='Writing')
    reading = fields.Selection(LEVELS, string='Reading')
    pronunciation = fields.Selection(LEVELS, string='Pronunciation')
    listening = fields.Selection(LEVELS, string='Listening')
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")