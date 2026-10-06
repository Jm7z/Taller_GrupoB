# Taller Grupo B

Aplicación educativa en Python, Streamlit y Plotly para explorar la concentración
de mercados hipotéticos mediante simulaciones y gráficos interactivos.

**[Abrir la aplicación](https://taller-grupob.streamlit.app/)** ·
[Manual completo](README.txt) · [Enlaces del proyecto](ENLACES.txt)

## Funcionalidades

- Calcula CRk, IHH, dominancia de García Alba y entropía de Shannon.
- Simula mercados y compara un caso con la distribución de cada indicador.
- Muestra histogramas, percentiles y explicaciones de los resultados.
- Incluye una evaluación didáctica del IHH y exportación de datos en CSV.

## Instalación en Windows

Requiere Python 3.11 o superior. Para seguir estos comandos, usa Python 3.12
y abre PowerShell en la carpeta del proyecto.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Abre [localhost:8501](http://127.0.0.1:8501) en el navegador.
Si PowerShell bloquea la activación del entorno, consulta las alternativas
del [manual](README.txt).

## Uso

1. Configura el número de empresas, el valor de k, las iteraciones y la semilla.
2. Introduce las cuotas del caso en porcentajes; deben sumar 100 %.
3. Pulsa **Simular mercados** y selecciona el indicador que quieres analizar.
4. Compara el caso con los mercados simulados, realiza la evaluación o descarga
   los datos en CSV.

## Pruebas

Con el entorno activado, ejecuta:

```powershell
python -m pip check
python -m unittest discover -s tests -v
```

## Documentación

El [README.txt](README.txt) contiene las fórmulas, unidades, supuestos,
límites, instrucciones de instalación y referencia de la API.
El código de cálculo está en `concentracion/` y las pruebas en `tests/`.

La clasificación de concentración es didáctica y utiliza el IHH en puntos.
La aplicación no determina automáticamente una conducta anticompetitiva.
