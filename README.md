# Taller_GrupoB

Aplicación educativa en Python, Streamlit y Plotly para explorar CRk, IHH,
dominancia de García Alba y entropía de Shannon en mercados hipotéticos.

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

Abrir http://127.0.0.1:8501. La instalación y el funcionamiento en Community
Cloud requieren verificaciones independientes de las comprobaciones locales.
Consultar el estado registrado en README.txt; no se presupone una URL pública.
