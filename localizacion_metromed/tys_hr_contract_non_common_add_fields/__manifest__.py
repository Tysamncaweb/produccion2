# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 23/07/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_contract_add_fields

{
    'name': 'Contract Non Common Aditional data',
    'description': '''\
Adds non common aditional fields to hr_contract module
============================

V1.1.1.
Agrega campos adicionales que pueden ser diferentes para cada tipo de empresa:\n
    ASIGNACIONES:\n
    * Ajuste de utilidades              * Ajuste de Cestatickets            * Ajuste de Fideicomiso\n
    * Bono Especial                     * Días Pendientes por disfrutar     * Transporte/Alimentación de Pasantes\n
    * Bono de Producción                * Anticipo de Utilidades            * Anticipo de Prestaciones Sociales\n
    * Reintegro por descuento indebido  * Reintegro por gastos varios       * Anticipo de Vacaciones\n
    * Descuento Horas                   * Reintegro gastos médicos          * Adicional por Zona\n
    * Examen pre/post Vacacional        * Accidente Profesional             * Accidente No Profesional\n
    * Pre/post Vacacional               * Reposo 100%                       * Reposo 33%\n
    * Permiso por Nacimiento o Examen   * Reposo Pre/pos                    * Anticipo Salario\n
    * Comisiones                        * Anticipo Comisiones               * Retroactivo Salario\n
    * Reintegro por inasistencia desc.  * Reintegrpo por descuento indebido * Reintegro por descuento de uniforme\n
    * Conmplemento de Comision          * Asignaciones Especiales           * Otras Asignaciones\n
    * Días faltantes                    * Ayuda Escolar                     * Clausula Mínima\n
\n
    DEDUCCIONES:\n
    * Prestamo                          * Cuota del prestamo                * Descuento indebido de salario\n
    * Descuento fotocopias              * Descuento por llamadas            * Trimestre de Vehiculo\n
    * Descuento por pagi de factura     * Descuento pago de comisión        * Descuento póliza HC\n
    * Descuento ant. gtos. moto         * Descuento póliza de vehículos     * Descuento comisión por devolución de merc.\n
    * Descuento vale de caja chica      * Descuento reposición de carnet    * Descuento pago de vehículo\n
    * otras deducciones\n

''',
    'author': 'TYSAMNCA',
    'category': 'Human Resources',
    'data': [
        'views/tys_hr_contract_non_common_add_fields.xml',
        ],
    'depends': ['hr_contract_add_fields', 'hr_salary_increase'],
    'installable': True,
}