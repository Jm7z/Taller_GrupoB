# Bitácora técnica de Taller_GrupoB

Registro público de trabajo y verificaciones reales. COMPROBACIONES.md
separa pruebas de código, observación de navegador y reportes del usuario.
La bitácora registra asistencia de IA; no sustituye la conversación compartida.

## Versión de partida y publicación anterior

La aplicación conserva cálculos en proporciones, cierre atol=1e-10/rtol=0,
API completa y adaptadores, interfaz con cuatro series compactas por lotes,
generador independiente para el caso, progreso mediante callback, CSV
diferidos, tarjetas y cuatro histogramas con línea/etiqueta/hover.

La evaluación didáctica del IHH mantiene clasificación sin redondear fronteras,
preguntas conceptuales y numérica CRk, bloqueos y limpieza de respuestas.
La retroalimentación errónea indica selección, intervalo, valor calculado,
motivo de exclusión y categoría correcta. Se conservan precisión, aportes por
empresa y percentil IHH aunque se visualice otro indicador.

El 5 de octubre de 2026 se publicó el repositorio
https://github.com/Jm7z/Taller_GrupoB, main. Commit de código
0868937507fa00a2c7effe9dc4dabbc86514d4a6; cierre documental
8a6206c77be2f8935587748f5e457c626ccff896. Se cotejaron 26 archivos del ZIP anterior
con lo publicado. Se conservó la configuración y los cinco pins.

La aplicación recibió la URL real https://taller-grupob.streamlit.app/.
Los logs mostraron Python 3.12.15 en Linux; Python 3.12 fue seleccionado
explícitamente. Sharing confirmó visibilidad pública. No se ejecutó la suite
dentro de Cloud y los logs no expusieron el SHA exacto de su proceso.

Un usuario reportó error de callback_progreso. Firma local/remota y llamadas
admitían el callback; después de un reinicio de Cloud una sesión nueva simuló.
El usuario confirmó lo mismo desde una ventana privada sin iniciar sesión.
La causa exacta del incidente no quedó demostrada; no se cambió código para
atribuirle una solución causal. Evidencia y límites en COMPROBACIONES.md.

Aquella publicación comprobó los cuatro indicadores, N=2/N=100, ejemplo,
edición inválida, aleatorio, estado, progreso final, respuestas y CSV reales.
El ejemplo N=4/k=2/M=1000/semilla 42 produjo CR2=70 %, IHH≈3000 y percentil IHH 17,1 %.
Se revisaron escritorio 960×900 y móvil emulado 390×844, sin teléfono físico.
El ZIP final de aquella entrega aprobó 116 pruebas aisladas en 20,011 s desde
una extracción nueva, reinstalación offline, pip check y arranque HTTP 200.
Estos resultados no acreditan automáticamente las correcciones siguientes.

## Corrección puntual de CRN: trabajo local verificado

Se reprodujo el defecto en N=100,k=100, M=1000,semilla 42 y cuotas iguales:
CR simulado entre 0,9999999999999989 y 1,0000000000000009, percentil 67,2 %.
La comparación inclusiva del percentil era correcta; diferencias flotantes
de las sumas separaban observaciones matemáticamente empatadas.

Se aplicó exclusivamente la identidad CRN=1 después de validar:
crk escalar devuelve 1,0 con k=N; _calcular_indicadores llena la serie con 1,0.
Los motores completo/compacto y adaptadores reutilizan esas rutas.
El percentil pasó a 100,0 % por la comparación ordinaria<=; no se introdujo
tolerancia general, normalización, redondeo ni cambio en las cuotas.

Se añadieron regresiones para N=2/4/100, cuotas iguales/desiguales, ambos motores,
adaptadores, invalidación, histograma, CSV y AppTest. Una expectativa previa
que exigía CRN distinto de 1 describía el defecto y se actualizó solamente en
ese punto. Las 116 pruebas previas y 12 regresiones aprobaron: 128 en 26,212 s,
Python 3.12.14. La comparación de 135 resultados antes/después confirmó que
k<N, cuotas, IHH, ID, entropía y sus percentiles se conservaron.
No se publicó ni desplegó ese parche durante la tarea puntual.

## Cierre actual autorizado

Antes de modificar o retirar archivos se dejó un punto de recuperación local
en Git: 61d769c03ad507ae417b7a5c9892299618100cd6. No se reescribe historial,
no se usa force push y no se borran servicios, repositorios ni datos externos.

Se implementan únicamente las ayudas por indicador, lectura real del percentil,
aviso CRN exacto, resumen de justificación IHH para N>12 con detalle completo,
y advertencia breve de recursos con detalles técnicos. Se conserva la app
vigente, el diseño, las fórmulas restantes, validaciones, generador, lotes,
límites, firmas, CSV, muestra compacta y evaluación. El aviso que explicaba
la dispersión artificial de CRN queda obsoleto y se retira.

README.txt y README.md separan evidencia histórica de esta actualización.
La suite posterior a las ayudas aprobó 136 de 136 pruebas en 21,542 s,
Python 3.12.14/NumPy 2.3.5; test_claridad.py aprobó 8 de 8 en 2,916 s por
separado. Tests de progreso actualizaron la ubicación esperada de la explicación
de empates (markdown) y la nueva aclaración de IE; se conservaron sus exigencias
sobre callbacks, lotes, resultados y limpieza ante errores.
COMPROBACIONES.md registra la publicación y comprobación pública posteriores.
La verificación del paquete de cierre se registra más abajo; el resumen final
identifica el archivo entregado y su cotejo exacto. La prueba interactiva privada
actual también se registra a continuación.
La limpieza conserva adaptadores y medir_rendimiento.py por sus usos;
los archivos de utilidad incierta deben conservarse e identificarse.

Después del respaldo se retiraron 23 archivos de raíz duplicados, cotejados
byte a byte con los conservados, y dos ZIP antiguos inspeccionados. Se retiraron
empaquetar.py, registro_pruebas.txt y rendimiento.json por ser regenerables,
cachés y carpetas duplicadas vacías. Tres documentos históricos se trasladaron
al archivo local, sin destruirlos. Historial Git, entorno de desarrollo, evidencia
y herramientas se conservaron fuera de la carpeta canónica y del paquete.

El candidato de prepublicación tuvo 30 archivos, CRC válido y bytes idénticos
a las fuentes canónicas. Se extrajo en una carpeta nueva y se creó otro venv
Python 3.12.14, sin paquetes de sistema/usuario. Se instalaron 40 paquetes
offline desde wheels existentes y los requisitos extraídos, manteniendo los
pins; pip check informó No broken requirements found. Las 136 pruebas pasaron
en 21,9598442 s, cero errores/fallos, con imports solo de la extracción y
dependencias solo del entorno nuevo. No se presenta esa ejecución como prueba
del ZIP definitivo ni del despliegue remoto. El servidor extraído en
127.0.0.1:8513 respondió HTTP 200 en raíz/salud; el navegador cargó controles y
simuló el caso predeterminado N=4/k=2/M=1000/semilla 42 con cuotas iguales, CR2=50 %
y percentil 0 %, progreso 1000/1000 al 100 %, línea/etiqueta y sin error.

## Publicación actual y comprobación pública

Se publicó el código en main, commit 9f5d425a4ff793f4b18f2c33019516f48a6e1a0a,
mediante avance normal desde 8a6206c77be2f8935587748f5e457c626ccff896. Se
recuperó el árbol completo ad354e723090cf39d6493cb2ad2b4bc4baaebd21 y se
cotejaron los 30 archivos remotos contra las fuentes, idénticos byte a byte.
No hubo force push ni otra aplicación pública.

Cloud notificó autoupdate 00:15:49 UTC del 6 de octubre (21:15:49 del 5 local).
Una sesión con nuevas ayudas aún produjo el percentil CR100 defectuoso 67,2 %;
se registró el fallo y no se consideró la publicación terminada. Se reinició
el servicio existente: desconexión 00:19:04 UTC y nuevo arranque Uvicorn
2026-10-06 00:19:22.304 UTC (21:19:22.304 local). Los logs registraron
Python 3.12.15,37 paquetes con uv y 4 de rich del servicio; pins intactos.
La causa exacta del estado previo no quedó demostrada y los logs no expusieron
el SHA interno. No se ejecutó la suite dentro de Linux Cloud.

Una sesión nueva simuló el predeterminado y N=100/k=100/M=1000/semilla 42 con
cien cuotas de 1 %: CR100=100 % y percentil 100 %, histograma constante,
línea/etiqueta 100 %, escritorio 960×900 y móvil emulado 390×844. Los CSV
descargados tuvieron 1000×11/100×2: CR porcentuales 100 exactos y cuotas 1 %.
La lectura round_trip frente a la extracción local dio diferencia máxima 0,0
en CR, IHH, ID, IE, IE/lnN y metadatos correctos. N=100: Baja correcta, IHH 100 puntos,
percentil 0 %, resumen y desplegable íntegro de 100 empresas.

Ejemplo desde N=100 pasó a N=4/k=4, bloqueó muestra y limpió feedback. Con k=2 y
nueva simulación mostró CR2=70 %, IHH 3000.0000000000005 puntos/percentil 17,1 %;
Moderada fue incorrecta con intervalo y cuatro cuadrados. Otra pestaña nueva
revisó los cuatro histogramas/ayudas/unidades/ejes/leyenda/línea/etiqueta y
percentiles CRk 23,4 %, IHH 17,1 %, ID 20,5 %, IE 82,3 %. Con IE seleccionado, Alta
correcta conservó IHH 17,1 % (171/1000) y la muestra vigente.

Settings confirmó Python 3.12 y Sharing público/searchable. El 6 de octubre
a 00:22:05 UTC, raíz e iframe respondieron HTTP 200 a una petición independiente
con jar vacía y sin credenciales. Esta carga HTTP anónima no se presenta como
prueba interactiva en ventana privada. El usuario realizó la prueba solicitada
en Edge privado sin iniciar sesión, N=100/k=100/M=1000/semilla 42/cuotas iguales,
y respondió: "Sí: la aplicación publicada mostró CR100 = 100,00 % y percentil
= 100,00 %, sin errores visibles en esta prueba." Se registra como reporte del
usuario, no observación directa de esa ventana por la herramienta.
El archivo definitivo y el commit documental se identifican en el resumen final,
sin incorporar un SHA autorreferencial en estos documentos.

## Paquete de cierre comprobado antes de esta última edición documental

Otra extracción nueva, extraido_cierre_actual, comprobó un ZIP de 30 archivos
con CRC válido y bytes idénticos a las fuentes. Se creó otro entorno .venv_final
Python 3.12.14 aislado sin paquetes del sistema/usuario. Se instalaron40 paquetes
offline desde requirements EXTRAÍDO, pins intactos, y pip check aprobó.
Las 136 pruebas pasaron, cero errores/fallos, en 22,8258215 s; fuentes importadas
solo desde esa extracción y dependencias solo desde su nuevo venv.

El servidor propio extraído en 127.0.0.1:8514 respondió HTTP 200 raíz/salud/ok.
El navegador renderizó controles y simuló N=100/k=100/M=1000/semilla 42/cuotas
iguales: CR100=100 %,percentil 100 %,progreso 1000/1000,línea y etiqueta visibles.
Se cotejaron las versiones publicadas 8a6206c y 9f5d425: índices solo añade
identidad CRN escalar y simulación solo cambia suma CRN por fill(1).
Evaluación/gráficos/requirements/config permanecen idénticos byte a byte.

Esta última actualización registra esos resultados reales; no atribuye al
archivo definitivo un hash, commit o tiempo de una verificación posterior
todavía no observada. El resumen final identifica el ZIP entregado y su cotejo
y ejecución exactos. Código, pruebas, dependencias y configuración no cambian
por esta edición documental. Se mantienen explícitos los límites de Linux,
SHA interno Cloud, móvil emulado y HTTP anónimo403 del enlace de conversación.

El enlace real conservado del historial de conversación es
https://chatgpt.com/s/cx_6ac32e27e5188191ae8322c88acd137a.
Se abrió su contenido, titulado "Crear índices de concentración", página
SharedCodexchat con mensajes de etapas previas. Es una instantánea histórica:
no se afirma que incluya necesariamente los turnos finales de esta tarea.
Una petición HTTP anónima independiente recibió 403. El acceso se observó en
el navegador disponible; no se afirma que se haya comprobado sin sesión.
El enlace y la bitácora cumplen funciones diferentes: la segunda no sustituye
el contenido compartido para la trazabilidad de IA.
