# Taller_GrupoB

Aplicación educativa en Python, Streamlit y Plotly para explorar CRk, IHH,
dominancia de García Alba y entropía de Shannon en mercados hipotéticos.

- Repositorio: [Jm7z/Taller_GrupoB](https://github.com/Jm7z/Taller_GrupoB).
- Aplicación existente: [taller-grupob.streamlit.app](https://taller-grupob.streamlit.app/).
- Manual completo de Windows, fórmulas, unidades, supuestos, límites y API:
  [README.txt](README.txt).
- Evidencia real y pendientes: [COMPROBACIONES.md](COMPROBACIONES.md).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Abrir http://127.0.0.1:8501. Si PowerShell impide activar el entorno, el manual
explica cómo usar cmd o su python.exe directamente. Python local utilizado:
3.12.14 de 64 bits. Pins intactos: NumPy 2.3.5, pandas 3.0.1, Plotly 6.9.0,
Streamlit 1.65.0 y PyArrow 21.0.0.

La corrección local de CRk aplica **CRN=1,0 exacto después de validar**. Para
N=100, k=100, 1000 iteraciones, semilla 42 y cien cuotas de 1 %, el percentil pasó
de 67,2 % a **100,0 %**. No se cambió la definición del percentil: cuenta valores
menores o iguales e incluye todos los empates. CRk para k<N, cuotas generadas,
IHH, ID y entropía conservaron los resultados de la comparación antes/después.
El parche local aprobó **128 pruebas en 26,212 s**; sus regresiones comprueban
ambos motores, adaptadores, exportaciones, histogramas y Streamlit AppTest.

El cierre actual incorpora ayudas por indicador, lectura del percentil,
justificación resumida para más de 12 empresas y advertencia breve de recursos.
La suite actual aprobó **136 de 136 pruebas en 21,542 s**; las ocho nuevas
pruebas de claridad aprobaron también por separado en 2,916 s. El código está
publicado en [main, commit 9f5d425](https://github.com/Jm7z/Taller_GrupoB/commit/9f5d425a4ff793f4b18f2c33019516f48a6e1a0a), con 30 archivos cotejados contra las fuentes.
El paquete de cierre se verificó en otra extracción nueva y otro entorno
Python 3.12.14 aislado:40 paquetes instalados offline desde sus requisitos y
pip check aprobado; **136/136 pruebas sin errores/fallos en 22,8258215 s**.
Servidor extraído en 8514: raíz/salud HTTP 200, controles visibles y simulación
N=100/k=100/M=1000/semilla 42/cuotas iguales con CR100=100 % y percentil 100 %,
progreso completo, línea y etiqueta del caso. Este registro corresponde al
paquete previo a la última edición documental. El resumen final identifica
el archivo entregado, commit/cotejo de bytes y su verificación exacta, sin
atribuir a estos documentos un hash o tiempo posterior no observado.

El candidato de prepublicación tiene 30 archivos, CRC válido y bytes cotejados
con las fuentes. Desde una extracción nueva y un entorno independiente Python
3.12.14 se instalaron 40 paquetes offline desde sus requisitos; pip check aprobó.
Las **136 pruebas pasaron en 21,9598442 s** sin errores ni fallos, importando solo
fuentes extraídas y dependencias del entorno nuevo. Esta comprobación no acredita
todavía el ZIP definitivo ni el nuevo despliegue.
La app extraída respondió HTTP 200 en raíz/salud y el navegador cargó controles
y simuló el caso predeterminado sin error, con progreso 1000/1000 al 100 %,
línea/etiqueta y CR2=50 %/percentil 0 % para las cuatro cuotas iguales.

Tras la actualización automática se observó una sesión con CR100 percentil 67,2 %.
Se reinició el despliegue existente y una sesión nueva comprobó **CR100=100 % y
percentil 100 %**. Logs del arranque 2026-10-06 00:19:22.304 UTC: Python 3.12.15 y
pins intactos. CSV de 1000 simulaciones: todos los CR100 exactos 100 %; caso 100
cuotas exactas de 1 %. La comparación con extracción local dio diferencia máxima
0,0 en los indicadores. Evaluación N=100 mostró Baja/IHH 100 puntos/percentil 0 %,
resumen y detalle completo. El ejemplo volvió a N=4/k=4 y bloqueó la muestra;
con k=2 y nueva simulación confirmó CR2=70 %, IHH≈3000 y percentil IHH 17,1 %.
Otra pestaña nueva tras el reinicio revisó los cuatro indicadores y sus ayudas,
ejes, unidades, leyenda, línea y etiqueta: percentiles CRk 23,4 %, IHH 17,1 %, ID 20,5 %,
IE 82,3 %. Con IE seleccionado, evaluación Alta conservó IHH 17,1 % (171/1000)
y el desarrollo de las cuatro cuotas; cambiar indicador conservó la muestra.

Se comprobó Sharing público y HTTP 200 anónimo en raíz/iframe sin credenciales.
El usuario confirmó esta versión desde la ventana privada Edge solicitada,
sin iniciar sesión, con N=100/k=100/M=1000/semilla 42 y cuotas iguales: CR100=100,00 %,
percentil 100,00 %, sin errores visibles. Es un reporte del usuario, no observación
directa de su ventana privada por la herramienta.
El SHA interno de Cloud no está expuesto y no se ejecutó allí la suite.

El cotejo de las versiones publicadas 8a6206c y 9f5d425 confirmó cambios mínimos
en cálculos: CRN escalar devuelve 1,0 y vectorizado usa fill(1) tras validar.
evaluacion.py, graficos.py, requirements.txt y config.toml permanecieron
idénticos byte a byte. Las ayudas se implementaron en la aplicación vigente.

La publicación anterior del 5 de octubre de 2026 usó Python 3.12.15 en Cloud.
Allí se comprobó el ejemplo 40–30–20–10 con k=2: CR2=70 %, IHH≈3000 puntos y
percentil IHH 17,1 % (171/1000). El usuario confirmó acceso y simulación desde una
ventana privada sin iniciar sesión; la herramienta no observó esa ventana.
Las pruebas de esa entrega, incluida su extracción con 116 pruebas aprobadas,
no acreditan por sí solas esta actualización. El SHA interno de Cloud no
apareció en los logs y no se ejecutó la suite dentro de Linux Cloud.

Se mantiene el mismo diseño, motor compacto por lotes, controles, CSV y
evaluación. La clasificación didáctica usa IHH en puntos; su percentil siempre
usa la serie IHH aunque se elija otro histograma. La app no determina
automáticamente una conducta anticompetitiva.

La [bitácora técnica](BITACORA.md) documenta la asistencia de IA y trabajo real.
La [conversación compartida](https://chatgpt.com/s/cx_6ac32e27e5188191ae8322c88acd137a)
se abrió y mostró "Crear índices de concentración". Es una instantánea histórica
real y no necesariamente incluye los últimos turnos. La bitácora no sustituye
la conversación compartida; los enlaces se reúnen en [ENLACES.txt](ENLACES.txt).
El contenido se observó en el navegador disponible; una petición HTTP anónima
independiente recibió 403. No se presenta su acceso anónimo como comprobado.
