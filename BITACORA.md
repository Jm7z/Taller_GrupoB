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
El ejemplo N=4/k=2/M=1000/semilla 42 produjo CR2=70 %,IHH≈3000 y percentil IHH 17,1 %.
Se revisaron escritorio 960×900 y móvil emulado 390×844, sin teléfono físico.
El ZIP final de aquella entrega aprobó 116 pruebas aisladas en 20,011 s desde
una extracción nueva, reinstalación offline, pip check y arranque HTTP 200.
Estos resultados no acreditan automáticamente las correcciones siguientes.

## Corrección puntual de CRN: trabajo local verificado

Se reprodujo el defecto en N=100,k=100,M=1000,semilla 42 y cuotas iguales:
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
COMPROBACIONES.md deja pendientes publicación/commit final, comprobación pública,
acceso anónimo e integridad/instalación/pruebas/arranque desde el nuevo ZIP.
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
del ZIP definitivo ni del despliegue aún pendiente. El servidor extraído en
127.0.0.1:8513 respondió HTTP200 en raíz/salud; el navegador cargó controles y
simuló el caso predeterminado N4/k2/M1000/semilla42 con cuotas iguales, CR2=50 %
y percentil0 %, progreso1000/1000 al100 %, línea/etiqueta y sin error.

El enlace real conservado del historial de conversación es
https://chatgpt.com/s/cx_6ac32e27e5188191ae8322c88acd137a.
Se abrió su contenido, titulado "Crear índices de concentración", página
SharedCodexchat con mensajes de etapas previas. Es una instantánea histórica:
no se afirma que incluya necesariamente los turnos finales de esta tarea.
Una petición HTTP anónima independiente recibió 403. El acceso se observó en
el navegador disponible; no se afirma que se haya comprobado sin sesión.
El enlace y la bitácora cumplen funciones diferentes: la segunda no sustituye
el contenido compartido para la trazabilidad de IA.
