# encuestas
Extracción simple de encuestas UPM

## Autentificarse

- Autentifícate en ```https://servicios.upm.es/encuestas/statistics```
- Copiar cookie de PHP en ```cookie.txt``` (ver ```cookie.txt.ejemplo```)

## Proceso

- Manual:
    - Ve al listado de la web
    - Inspecciona la página y copia el contenido de ```<div id="root"></div>``` en un fichero ``ìnfo.html```
- Extraer ids, asignatura y grado:
    - ```python3 extract-ids.py info.html```
    - Genera ```data/id.csv``` con columnas: ID, ASIGNATURA, GRADO, FILE_ID
- Manual:
    - Abre pestañas con cada enlace
    - Rellena el campo ```FILE_ID```
- Descargar PDF/CSV:
    - ```python3 download.py data/id.csv```
    - Realiza:
        - Usa ```api/group/{FILE_ID}/stats?format=csv``` y ```format=pdf```
        - Genera directorios ```data/{ASIGNATURA}/``` con archivos ```{GRADO}.csv``` y ```{GRADO}.pdf```
- Agrega información:
    - ```python3 aggregate.py```
    - Genera ficheros ```agg.csv```
        - Media por titulación y media total

