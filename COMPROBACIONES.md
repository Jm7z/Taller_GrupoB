# Comprobaciones de Taller_GrupoB

Fecha del cierre: 5 de octubre de 2026, America/Santiago (UTC−3).
Se distinguen pruebas automatizadas, observaciones del navegador y resultados
reportados por el usuario. No se envió correo. Capturas, logs, entornos y CSV
de verificación quedan fuera del ZIP.

- Repositorio: https://github.com/Jm7z/Taller_GrupoB
- Aplicación existente: https://taller-grupob.streamlit.app/
- Rama y entrada vigentes: main, app.py.
- Publicación anterior: commit final 8a6206c77be2f8935587748f5e457c626ccff896;
  código publicado en 0868937507fa00a2c7effe9dc4dabbc86514d4a6.
- Recuperación previa al cierre actual: commit local
  61d769c03ad507ae417b7a5c9892299618100cd6. No se presenta como desplegado.
- Nuevo commit final, nuevo despliegue y ZIP final: pendientes de verificación.
- El SHA exacto del proceso Cloud no se observó en los logs anteriores.

## Corrección local ya ejecutada: identidad CRN

| Requisito | Evidencia real | Pendiente o límite |
| --- | --- | --- |
| Causa reproducida | N=100,k=100,M=1000,semilla 42, cien cuotas de 1 %. Antes: CR simulado entre 0,9999999999999989 y 1,0000000000000009; percentil 67,2 %. Residuos float64 separaban empates matemáticos. | El porcentaje defectuoso puede variar por entorno. |
| CRN escalar/vectorizado | crk devuelve 1,0 tras validar cuotas y k. _calcular_indicadores llena CR con 1,0 cuando k=N. Resultado posterior: CRN exacto 1,0 y percentil 100,0 %. | No se introdujeron tolerancias en el comparador del percentil. |
| Rutas públicas y motores | Regresiones en N=2,4,100, repartos iguales/desiguales, ambos motores, adaptadores y caso reproducible. Histograma y CSV consumen las series corregidas. | Prueba de código/AppTest; parche todavía no acreditado en el despliegue actual. |
| Validaciones | Entradas inválidas se rechazan aun con k=N; identidad aplicada después de validar. | No se normalizan ni modifican cuotas originales. |
| Conservación matemática |135 comparaciones antes/después: k<N, cuotas generadas, IHH, ID, IE y sus percentiles conservaron resultados. Ejemplo 40–30–20–10,k=2: CR2=70 %. | No es una garantía entre distintas versiones de NumPy. |
| Suite del parche |128 pruebas aprobadas en 26,212 s, Python Windows 3.12.14: 116 anteriores y 12 regresiones nuevas. | Se modificó únicamente la expectativa que exigía CRN distinto de 1: describía el defecto. Suite no ejecutada en Linux Cloud. |
| Fórmulas y aleatoriedad | IHH/ID/IE, percentil inclusivo, semillas, Dirichlet, secuencia, lotes, límites y firmas públicas conservados. | La excepción CRN=1 es la identidad matemática, no un ajuste de percentil en pantalla. |

## Cierre actual: implementación y comprobaciones

Estas tareas pertenecen a la actualización actual. La evidencia de la entrega
anterior que figura más abajo no se reutiliza como aprobación de estos cambios.

| Requisito | Estado de implementación/evidencia | Pendiente real |
| --- | --- | --- |
| Ayudas por indicador | AppTest verifica una ayuda por selector, los cuatro indicadores, valores/percentiles reales y una sola llamada al motor. | Revisión visual de la versión pública actual. |
| Lectura del percentil | AppTest verifica mensaje, menor o igual, empates, mismo N/Dirichlet, aclaración exclusiva de IE y ausencia con caso inválido/muestra desactualizada. Con IE seleccionado, evaluación usa IHH 17,1 %. | Comprobación pública actual; AppTest no sustituye revisión visual. |
| Caso k=N | AppTest N=100/k=100/M=1000/semilla 42: series exactas de unos, percentil 100 %, aviso único y etiqueta 100 %. Aviso de dispersión artificial retirado. | Verificar este caso públicamente y revisar histograma constante/marcador/etiqueta. |
| Justificación IHH | Pruebas N=2/4/12 conservan texto completo. N=13/100: resumen visible, texto IHH conservado, todas las filas/cuotas/aportes en desplegable y percentil IHH propio; cambiar a ID conserva resultado/muestra. | Revisión pública actual; no se recalcula ni cambia el contrato del evaluador. |
| Recursos | AppTest verifica advertencia breve con máximo, detalles técnicos completos en desplegable y aviso desde 50000 sin ejecutar Monte Carlo. | Revisión visual pública actual; no es medición nueva de rendimiento. |
| Estructura y limpieza | Tras respaldo Git: 23 duplicados de raíz byte a byte iguales a los conservados, dos ZIP antiguos inspeccionados, empaquetar.py/registro_pruebas.txt/rendimiento.json regenerables y cachés/carpetas duplicadas vacías retirados. Tres documentos históricos trasladados, no destruidos. Candidato de 30 archivos sin residuos; adaptadores y medir_rendimiento.py útiles conservados. | Git, entorno de desarrollo, evidencia y herramientas permanecen fuera de la carpeta canónica/entrega. No se borró historial ni datos externos. |
| Dependencias/configuración | Pins conservados. Nueva extracción de prepublicación: 40 paquetes instalados offline en otro entorno Python 3.12.14; pip check: No broken requirements found. TOML vigente, tema claro/headless, sin dirección/puerto/certificados locales. | La instalación del ZIP definitivo y el nuevo despliegue se verifican por separado. |
| Pruebas actuales | Suite completa 136/136 OK en 21,542 s, Python Windows 3.12.14/NumPy 2.3.5. test_claridad.py: 8/8 OK en 2,916 s por separado. | Suite no ejecutada en Linux Cloud; comprobación visual pública actual y extracción final aún pendientes. |
| Publicación | Se actualiza el repositorio existente y su aplicación, sin crear otra app. | Revisar diff, registrar commit final, confirmar main remoto, logs y versión efectiva del despliegue. |
| Comprobación pública | URL real conservada; no se inventa otro enlace. | Acceso anónimo de esta versión; simulación predeterminada, ejemplo, N=100/k=100, cuatro indicadores, marcador/etiqueta y evaluación sin errores. |
| ZIP definitivo | Se prepara un único Taller_GrupoB.zip con fuentes, pins, documentación, configuración y pruebas. | CRC/nombres/manifiesto/bytes contra commit publicado; extracción nueva, instalación, suite y arranque desde allí. |
| Extracción de prepublicación | Nuevo candidato de 30 archivos, CRC válido y bytes iguales a fuentes; extraido_prepublicacion nuevo dentro de _verificacion_cierre_20261005. Otro venv Python 3.12.14, include-system-site-packages=false, sin paquetes de usuario/modo -I. Instalación offline 40 paquetes y pip check aprobados. Suite 136/136, cero errores/fallos en 21,9598442 s; imports del proyecto solo desde extracción y bibliotecas solo desde su nuevo venv. | Corresponde al candidato previo a publicar. No acredita todavía el ZIP definitivo ni el despliegue actualizado. |
| Arranque extraído de prepublicación | Servidor desde la extracción en 127.0.0.1:8513: raíz/salud HTTP200/ok. Navegador renderizó controles y simuló N4/k2/M1000/semilla42, cuotas iguales: CR2=50 %, percentil0 %, progreso1000/1000 al100 %, línea/etiqueta visibles y ausencia de error. | Ejecución local real del candidato; puerto normal del README8501. No acredita el ZIP definitivo ni Cloud. |
| Transparencia IA | Enlace real del historial: https://chatgpt.com/s/cx_6ac32e27e5188191ae8322c88acd137a. Navegador disponible abrió contenido "Crear índices de concentración", página SharedCodexchat con mensajes previos. | Instantánea histórica; no necesariamente incluye últimos turnos. HTTP anónimo independiente devolvió 403: acceso anónimo no acreditado. BITACORA no sustituye conversación. |

## Evidencia histórica de la publicación anterior

Los resultados siguientes pertenecen a la versión anterior al parche de CRN
y a las nuevas ayudas. Se conservan para distinguir trabajo ya realizado de
las comprobaciones necesarias de la actualización.

| Comprobación histórica | Resultado observado | Límite |
| --- | --- | --- |
| GitHub y entrega anterior | Repo público/main;26 archivos de aquel ZIP cotejados byte a byte y por blob con 8a6206c77be2f8935587748f5e457c626ccff896. | No acredita el nuevo commit/ZIP ni el SHA interno de Cloud. |
| Dependencias Cloud | Python seleccionado 3.12; log Using Python 3.12.15 environment at /home/adminuser/venv. NumPy 2.3.5,pandas 3.0.1,Plotly 6.9.0,Streamlit 1.65.0,PyArrow 21.0.0 instalados mediante uv. Arranque 17:26:22.943 UTC. | Local 3.12.14; dependencias transitivas no fijadas; suite no ejecutada en Linux Cloud. |
| Configuración y Git | TOML reconocido y tema esperado. git check-ignore:11 rutas excluidas y 6 necesarias no ignoradas. | Cloud puede sobrescribir gatherUsageStats; no prueba control de su telemetría. |
| Acceso | Settings>Sharing: This app is public and searchable. Usuario confirmó simulación sin sesión en ventana privada después de Ctrl+F5. | Privada realizada/reportada por usuario; navegador de herramienta usó sesión administrativa. |
| Incidente callback | Firma y fuentes publicadas admitían callback_progreso. Reinicio observado:17:35:15 UTC desconexión;17:35:59.355 UTC nuevo arranque. Sesión nueva y usuario simularon sin error. | La causa exacta del proceso fallido no quedó demostrada; no se atribuye a caché concreta. |
| Referencia 40–30–20–10 | N=4,k=2,M=1000,semilla 42: CR2=70 %, IHH interno 3000.0000000000005 puntos, ID≈0.393333, IE≈1.279854 nats. Percentiles CRk23,4 %,IHH 17,1 %,ID 20,5 %,IE 82,3 %. IHH 171/1000 menores o iguales. | Los percentiles dependen de la muestra; no se fuerzan datos. IHH pasa a puntos una sola vez. |
| UI/estado | Cuatro indicadores, N=2/N=100, cambios de k/iteraciones, muestra desactualizada, caso aleatorio independiente y limpieza de respuestas comprobados. Edición40→30: suma 90 %, falta 10 %, bloqueo sin normalizar ni etiqueta. | La versión histórica permitía percentil CRN inferior a 100 % por residuos flotantes; esa expectativa era incorrecta y se corrigió localmente. |
| Evaluación | Alta correcta; Baja/Moderada incorrectas explicaron intervalos. Con IE visualizado, evaluador mantuvo IHH 17,1 %. CR2 numérico70,00 aceptó,60 rechazó con suma 40+30=70. | Seis selecciones erróneas y fronteras completas probadas en código, no todas remotamente. |
| Progreso/gráficos | Cloud mostró 1000/1000 y 5000/5000,100 %. Cuatro histogramas con línea/leyenda/etiqueta. Hover IHH: intervalo2938,57–3152,53, frecuencia 109; línea Caso3000 puntos/percentil 17,10. | Avance intermedio y limpieza ante errores probados en código, no todos capturados visualmente. |
| CSV reales | Muestra 1000×11/caso 4×2. Lectura round_trip: diferencia máxima 0,0 contra series locales; configuración N=4/k=2/semilla 42/NumPy 2.3.5, caso 40/30/20/10, conteoIHH 171. | CSV/logs de comprobación fuera del ZIP. |
| Visual | Escritorio 960×900 y viewport 390×844, cuatro histogramas, etiquetas dentro/dos líneas, tarjetas apiladas; clientWidth=scrollWidth=390. | Emulación, no teléfono físico. Barra activa de Plotly puede cubrir parte del título móvil. |
| Extracción del ZIP anterior | Entorno independiente Python 3.12.14, sin paquetes del sistema/usuario. Reinstalación offline desde requirements extraído y pip check aprobados. ZIP final: 116 pruebas en 20,011 s; raíz/salud HTTP 200 y simulación de ejemplo con IHH 17,1 %. | PyPI local bloqueado WinError10013; wheels recuperadas de caché fuera de entrega. Esta ejecución no acredita el nuevo ZIP. |

## Límites y benchmark conservado

Medición histórica, no repetida en este cierre: Windows, Python 3.12.14,
NumPy 2.3.5, N=100,k=50,semilla 42. Cinco tiempos después de calentamiento;
memoria aparte con tracemalloc, no RSS ni latencia web. Justificó el máximo
100000 y lotes 4096. Procedimiento opcional en medir_rendimiento.py y README.

| Motor | Iteraciones | Mediana(s) | Pico trazado(MiB) |
| --- | ---: | ---: | ---: |
| Compacto |1000 |0.001813 |1.658 |
| Compacto |10000 |0.014942 |6.952 |
| Compacto |100000 |0.141094 |9.698 |
| Referencia experimental completa |1000 |0.001779 |1.655 |
| Referencia experimental completa |10000 |0.015655 |16.520 |
| Referencia experimental completa |100000 |0.175063 |165.179 |

Las cuatro series ocupan 32*M bytes, aproximadamente 3,05 MiB al máximo; esto
excluye lotes, Streamlit, gráficos, CSV y bibliotecas. No se midió carga
concurrente, agotamiento físico de memoria ni disponibilidad permanente.
Cloud documenta recursos variables e hibernación tras 12 horas sin tráfico:
un visitante puede necesitar despertar la app y esperar. Las fuentes oficiales
están en README.txt. No hay garantía de latencia o capacidad para varias sesiones.
