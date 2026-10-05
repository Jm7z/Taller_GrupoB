# Comprobaciones de Taller_GrupoB — publicación en preparación

Actualización del 5 de octubre de 2026. Los resultados de la entrega local
anterior se conservan identificados más abajo; no acreditan el funcionamiento
en Linux o Streamlit Community Cloud.

| Etapa actual | Evidencia comprobada | Pendiente |
| --- | --- | --- |
| Fuentes limpias | Extraídas del ZIP anterior, CRC válido, 24 archivos idénticos a las fuentes vigentes; añadidos .gitignore y README.md, sin modificar código ni dependencias. Carpeta Taller_GrupoB con 26 archivos publicables. | Revisión del paquete final y extracción de cierre. |
| Configuración Cloud | TOML válida, sin address, port ni certificados locales. Streamlit local reconoce configuración desde la carpeta limpia. | No se presenta como una lectura de configuración en Cloud. |
| Exclusiones Git | git check-ignore --no-index prueba 11 rutas de entornos, caché, temporales, logs, ZIP y secretos; seis archivos necesarios no están ignorados. | Git no debe usarse para subir logs de despliegue, secretos o CSV de pruebas. |
| Pruebas locales actuales | 116 pruebas, OK, 17,685 s, desde Taller_GrupoB. app y paquete importados de esa carpeta. Python 3.12.14 del entorno existente. | Esta ejecución no es una instalación nueva ni un despliegue. |
| GitHub | Conector reconoce Jm7z; repositorio real https://github.com/Jm7z/Taller_GrupoB, visibilidad public, rama main, permiso admin/push. Usuario creó README inicial; commit 321f7a561146f037bfaa8c83ebf52e48c5ef7018 comprobado. | Publicación de las fuentes y cotejo de sus bytes. |
| Cuenta Cloud | Usuario completó el acceso oficial; navegador muestra workspace jm7z's apps en share.streamlit.io. | Creación de aplicación, Python 3.12, instalación y registros. |
| URL/versión/acceso público | Todavía sin URL de aplicación comprobada ni parche Python o commit servido observado. | Despliegue, logs, sesión privada/anónima y pruebas remotas solicitadas. |

No se cambia ningún pin sin incompatibilidad concreta demostrada. La documentación
oficial de Cloud se consultó el 5 de octubre: Linux, versiones por Advanced settings,
acceso Sharing, recursos variables e hibernación tras 12 horas sin tráfico.

## Evidencia de la entrega local anterior

Entrega local del 5 de octubre de 2026. Se separan resultados ejecutados de
procedimientos o verificaciones pendientes. No se ha enviado un correo ni
desplegado la aplicación en un servidor público.

| Requisito | Evidencia real | Pendiente o límite |
| --- | --- | --- |
| Selección de archivos vigentes | Inspección de imports y accesos a archivos de app.py, concentracion/ y tests/. La app no necesita imágenes ni datos externos. Los cuatro adaptadores de raíz y medir_rendimiento.py son usados por pruebas. Lista explícita de 24 archivos en README.txt. | Los resultados generados y capturas históricas no se entregan. El entorno de desarrollo se conserva fuera de la carpeta de entrega. |
| Feedback IHH solicitado | 34 pruebas de app pasan (14,925 s). Se prueban las seis selecciones incorrectas, ambas fronteras y valores float64 inmediatamente adyacentes; se comprueba selección, valor, intervalo, motivo y categoría correcta. AppTest conserva ausencia de preselección y flujo de acierto/error. | Las comprobaciones de texto/estado son de código; no se presentan como una revisión visual nueva en dispositivos físicos. |
| Fórmulas, generador y dependencias preservados | SHA-256 de concentracion/indices.py, simulacion.py, evaluacion.py, requirements.txt y config.toml idénticos al inicio de esta revisión. El cambio de feedback es de presentación en app.py, con dos regresiones nuevas y una ampliada en tests/test_app.py. | Solo se redondea presentación, no clasificación, cuotas, simulaciones ni percentiles. |
| Suite en desarrollo | 116 pruebas, OK, 17,250 s. Cálculos, validaciones, APIs, motor completo/compacto, CSV, progreso, gráficos, evaluación y estado de UI. | Las advertencias ScriptRunContext de AppTest no son fallos de pruebas. |
| Instalación desde extracción nueva | Entorno .venv nuevo con Python 3.12.14; al inicio solo tenía pip y include-system-site-packages=false. Instalación real con pip --no-index --find-links wheelhouse -r requirements.txt de los wheels recuperados de la caché local de pip. Los cinco pins coinciden. pip check: No broken requirements found. | El intento de descarga directa de PyPI falló con WinError 10013 por permisos de red; no se presenta como aprobado. El ZIP no contiene caché, wheels ni el entorno de verificación. No se instaló Python mediante su instalador de Windows ni se probó py/activación manual en otro equipo. |
| Pruebas desde extracción | 116 pruebas, OK, 17,244 s. Proceso python -I -B, sin user site ni PYTHONPATH; solo se añadió la raíz extraída para imports locales. Rutas de app, paquete, adaptadores y referencia verificadas dentro de la extracción; bibliotecas dentro de su .venv. Se revisaron las rutas tras la suite, sin fuentes ni paquetes de desarrollo. | Mismo equipo Windows y runtime base Python disponible, con paquetes instalados en un entorno independiente. No es una comprobación en otro sistema. |
| Arranque desde extracción | Ejecutable del entorno nuevo: python -I -B -m streamlit run app.py en la raíz extraída, dirección 127.0.0.1 y puerto de prueba 8510. Servidor iniciado; / y /_stcore/health responden HTTP 200. Apertura real en el navegador: título, controles Configurar/Simular/Comparar/Evaluar, tarjetas y bloqueos iniciales visibles, sin excepción. | Se verificó el arranque y DOM inicial, no una revisión visual nueva completa de todos los gráficos ni nuevas descargas en navegador. El puerto 8510 evita interferir con servidores existentes; README usa el puerto local habitual 8501. |
| Integridad y contenido del ZIP | CRC comprobado con ZipFile.testzip, lista exacta de 24 entradas sin duplicados y bytes cotejados con las fuentes y extracción. README enumera cada archivo. Fuentes y dependencias verificadas desde la extracción permanecen idénticas; solo se actualizan documentos con estos resultados al cerrar el paquete. | Carpeta entrega: únicamente Taller_GrupoB.zip. Sin .venv, .git, cachés, secretos, resultados generados ni ZIP anteriores. |
| Despliegue, acceso público y correo | No realizados. README incluye instalación local y pasos para un despliegue futuro y comprobación en ventana privada. | No existe una URL pública de la aplicación verificada. |

## Qué cubren las pruebas incluidas

| Archivo | Casos |
| --- | ---: |
| tests/test_indices.py | 10 |
| tests/test_simulacion.py | 16 |
| tests/test_compacto.py | 5 |
| tests/test_graficos.py | 12 |
| tests/test_evaluacion.py | 8 |
| tests/test_app.py | 34 |
| tests/test_compatibilidad.py | 18 |
| tests/test_progreso.py | 13 |
| Total | 116 |

Los adaptadores se prueban mediante llamadas, atributos, unidades y resultados;
no solo imports. Se verifica cierre atol=1e-10/rtol=0, concordancia escalar y
vectorizada, semilla, compactación sin cuotas en la sesión y ausencia de doble
conversión del IHH a puntos. Para N=4,k=2,M=1000,semilla=42 y NumPy 2.3.5, el caso
40–30–20–10 tiene 171/1000 IHH menores o iguales (17,1%), sin forzar datos.

La pregunta numérica CRk prueba coma/punto, tolerancia inclusiva de 0,01 puntos
porcentuales, rechazo de no finitos y limpieza de estado. El ejemplo prueba
N=2 y N=100, ajuste de N/k y bloqueo de la muestra incompatible. Progreso:
resultados idénticos con/sin callback, avance por lotes y limpieza ante errores.
Gráficos: cuatro indicadores, unidades, constantes, extremos y percentiles 0/100.

Los errores de motor, memoria y callback se inyectan en tests: no se afirma haber
agotado físicamente la memoria. AppTest edita la tabla base en algunas pruebas;
no equivale a probar todas las interacciones de celdas en un navegador real.

## Alcance histórico y límites

Las revisiones anteriores incluyeron capturas de escritorio y viewports móviles,
descargas CSV y una medición del motor. No se repiten ni se presentan como nuevas
en esta entrega. BITACORA.md distingue las etapas; sus referencias a capturas,
ZIP anteriores o registros describen artefactos históricos excluidos del paquete.

La medición histórica (Windows, Python 3.12.14, NumPy 2.3.5, N=100,k=50,semilla=42)
justificó el máximo 100000 y los lotes de hasta 4096. Cinco tiempos tras
calentamiento, memoria medida por separado con tracemalloc, no RSS ni latencia
web. Se conserva aquí la información, no el archivo generado rendimiento.json:

| Motor | Iteraciones | Mediana (s) | Pico trazado (MiB) |
| --- | ---: | ---: | ---: |
| Compacto | 1000 | 0,001813 | 1,658 |
| Compacto | 10000 | 0,014942 | 6,952 |
| Compacto | 100000 | 0,141094 | 9,698 |
| Referencia experimental completa | 1000 | 0,001779 | 1,655 |
| Referencia experimental completa | 10000 | 0,015655 | 16,520 |
| Referencia experimental completa | 100000 | 0,175063 | 165,179 |

Estas cifras no garantizan recursos o respuesta en otro equipo. Para medir de
nuevo, seguir el comando opcional de README. No se han verificado Linux,
Community Cloud, carga concurrente, otros navegadores ni teléfonos físicos en
la preparación final. La reproducción entre versiones de NumPy no se garantiza.

Compatibilidad histórica delimitada: no se facilitaron firmas/retornos exactos
antiguos de gráficos/evaluación, retorno vectorizado o constructor del resultado.
Los contratos actuales están documentados y probados; no se afirma identidad
universal con detalles históricos desconocidos.

## Procedimiento ejecutado desde la extracción

Se creó _verificacion_Taller_GrupoB_20261005 fuera de entrega/. Se extrajeron
los 24 archivos del ZIP y se creó allí un entorno virtual con el runtime base
Python 3.12.14. El entorno no hereda paquetes del entorno de desarrollo.
La instalación offline utilizó las mismas versiones fijadas, sin modificarlas:

```powershell
.\.venv\Scripts\python.exe -I -m pip install --no-index --find-links wheelhouse -r requirements.txt
.\.venv\Scripts\python.exe -I -m pip check
.\.venv\Scripts\python.exe -I -B verificar_aislamiento.py
.\.venv\Scripts\python.exe -I -B -m streamlit run app.py --server.address 127.0.0.1 --server.port 8510 --server.headless true --server.fileWatcherType none
```

verificar_aislamiento.py fue una herramienta temporal para comprobar rutas y
ejecutar unittest.defaultTestLoader.discover('tests'), con todos los casos de la
suite. Las herramientas, logs, caché y entorno de verificación quedan fuera del
ZIP. El comando normal para el destinatario es el de README, unittest discover.
Después de registrar estos resultados se vuelve a comprobar CRC y concordancia
de los 24 archivos del ZIP final y de la extracción, sin cambios de código.
