Odoo Localizaciión Venezolana ODOO ver. 11 Enterprise
---------------

Este módulo agrega los modelos para manejar ciudades, municipios y parroquias, a saber:
.- res_state_municipal: modelo que parmite agregar los municipios relacionados por estado
   (res_country_state).
.- res_municipal_parish: modelo que permite agregar las parroquias relacionadas por municipios
.- res_country_city: modelo que permite agregar las ciudades relacionadas por estado
   (res_country_state).

También agrega los datos para los estados, cuidades, municipios y parroquias, en los archivos
que se describen a continuación:
.- country_states-xml: carga los estados asociados al país. Debido a que en la instalación básica
   nuestro país queda registrado con el id 238 los registros tiene asociado ese id. Se debe verificar,
   el id de nuestro país en la base de datos antes de instalar el módulo y verificar que es el que
   corresponde en los datos cargados.
.- insert_estados_odoo_11.sql: contienne el comando sql que agrega los estados en la tabla res_country_state,
   esto en caso de ser necesario.
.- res_country_city.sql: contiene el comando sql que agrega las ciudades a la tabla res_country_city.
   Es importante tener en cuenta que los id de los estados (campo res_country_state_id) deben ser cambiados
   de acuerdo con los ids que resulten, luego de la instalación del módulo. Los ids que están en el archivo hacen
   referencia a los ids generados durante las pruebas de los datos.
.- res_state_municipal.sql: contiene el comando sql que agrega los municipios a la tabla res_state_municipal.
   Es importante tener en cuenta que los id de los estados (campo res_country_state_id) deben ser cambiados
   de acuerdo con los ids que resulten, luego de la instalación del módulo. Los ids que están en el archivo hacen
   referencia a los ids generados durante las pruebas de los datos.
.- res_state_parish.sql: contiene el comando sql que agrega las parroquias a la tabla res_municipal_parish.
   No requiere de ajustes, pues los ids relacionados (campo res_state_municipal_id) hacen referencia a los
   ids que se generan luego de ejecutar el comando sql para la carga de los municipios (res_state_municipal.sql).

