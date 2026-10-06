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
pruebas de claridad aprobaron también por separado en 2,916 s. La publicación,
comprobación pública actual y extracción del ZIP final siguen pendientes de
verificación; todavía no se presentan como aprobadas.

El candidato de prepublicación tiene 30 archivos, CRC válido y bytes cotejados
con las fuentes. Desde una extracción nueva y un entorno independiente Python
3.12.14 se instalaron 40 paquetes offline desde sus requisitos; pip check aprobó.
Las **136 pruebas pasaron en 21,9598442 s** sin errores ni fallos, importando solo
fuentes extraídas y dependencias del entorno nuevo. Esta comprobación no acredita
todavía el ZIP definitivo ni el nuevo despliegue.
La app extraída respondió HTTP200 en raíz/salud y el navegador cargó controles
y simuló el caso predeterminado sin error, con progreso1000/1000 al100 %,
línea/etiqueta y CR2=50 %/percentil0 % para las cuatro cuotas iguales.

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
