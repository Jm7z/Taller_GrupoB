# Taller_GrupoB

Aplicación educativa en Python, Streamlit y Plotly para explorar CRk, IHH,
dominancia de García Alba y entropía de Shannon en mercados hipotéticos.

Repositorio público: [Jm7z/Taller_GrupoB](https://github.com/Jm7z/Taller_GrupoB).
Aplicación desplegada: [taller-grupob.streamlit.app](https://taller-grupob.streamlit.app/).
El ajuste público, el arranque y la simulación tras reiniciar Cloud se
comprobaron el 5 de octubre de 2026. El usuario confirmó, tras Ctrl+F5 en una
ventana privada: «Sí, ahora simula correctamente sin iniciar sesión». El acceso
anónimo fue reportado por el usuario; la herramienta no observó esa ventana.
La causa exacta del incidente de callback no quedó demostrada y no se cambió
el código para resolverlo.

El manual completo de instalación en Windows, ejecución local, fórmulas,
supuestos, límites, APIs y publicación está en [README.txt](README.txt).
La evidencia real y lo pendiente se registran en
[COMPROBACIONES.md](COMPROBACIONES.md).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Abrir http://127.0.0.1:8501. Desde una extracción nueva del ZIP candidato se
reinstalaron los pins offline y pip check aprobó en un entorno independiente
Python 3.12.14; sus 116 pruebas aisladas pasaron en 20,166 segundos. El servidor
respondió HTTP 200 y el navegador real simuló el ejemplo sin excepción.
En Cloud se observaron Python 3.12.15, los pins
instalados y el arranque, sin ejecutar allí la suite. El ejemplo 40–30–20–10,
con k=2, 1000 iteraciones y semilla 42, mostró CR2=70 %, IHH≈3000 puntos y
percentil IHH=17,1 % (171/1000). Se probaron también N=2 y N=100, cambios de
configuración, cuotas inválidas, casos aleatorios, respuestas y descarga de
ambos CSV. Los cuatro histogramas se revisaron en escritorio y viewport móvil
390x844, sin teléfono físico. La barra activa de Plotly puede cubrir parte del
título en móvil. El hover de la línea del IHH se comprobó en el navegador;
el avance intermedio del progreso tiene cobertura de código, sin captura visual.

La documentación final se publica y reempaqueta conservando el mismo código,
configuración y pruebas. En una segunda extracción nueva se reinstalaron los
pins, pip check aprobó y las 116 pruebas aisladas pasaron en 19,300 s; servidor
extraído con raíz y salud HTTP 200. El resumen de entrega identifica el commit
publicado, el ZIP definitivo cotejado y su comprobación adicional.
El SHA exacto del proceso Cloud sigue sin comprobarse
porque los logs no lo expusieron. Consultar el estado detallado en README.txt y
COMPROBACIONES.md; las pruebas locales no sustituyen las del despliegue.
