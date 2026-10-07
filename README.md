# Taller Grupo B

Aplicación educativa en Python, Streamlit y Plotly para explorar la concentración
de mercados hipotéticos mediante simulaciones y gráficos interactivos.

**[Abrir la aplicación](https://taller-grupob.streamlit.app/)** ·
[Instrucciones de ejecución](README.txt) · [Enlaces del proyecto](ENLACES.txt)

## Funcionalidades

- Calcula CRk, IHH, dominancia de García Alba y entropía de Shannon.
- Simula mercados y compara un caso con la distribución de cada indicador.
- Muestra histogramas, percentiles y explicaciones de los resultados.
- Incluye una evaluación didáctica del IHH y exportación de datos en CSV.

## Instalación en Windows

Requiere Python 3.12 de 64 bits con pip. Abre PowerShell o Símbolo del sistema
en la carpeta del proyecto.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Abre [localhost:8501](http://127.0.0.1:8501) en el navegador.
Mantén la terminal abierta mientras usas la aplicación y pulsa `Ctrl+C` para detenerla.
Las instrucciones para macOS y Linux están en [README.txt](README.txt).

## Uso

1. Configura el número de empresas, el valor de k, las iteraciones y la semilla.
2. Introduce las cuotas del caso en porcentajes; deben sumar 100 %.
3. Pulsa **Simular mercados** y selecciona el indicador que quieres analizar.
4. Compara el caso con los mercados simulados, realiza la evaluación o descarga
   los datos en CSV.

## Pruebas

Desde la carpeta del proyecto, ejecuta en Windows:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Documentación

El [README.txt](README.txt) contiene las instrucciones de instalación,
ejecución y pruebas en Windows, macOS y Linux.
El código de cálculo está en `concentracion/` y las pruebas en `tests/`.

La clasificación de concentración es didáctica y utiliza el IHH en puntos.
La aplicación no determina automáticamente una conducta anticompetitiva.
