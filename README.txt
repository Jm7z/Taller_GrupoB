TALLER GRUPO B
Simulador de concentración de mercado

Instrucciones de ejecución local

REQUISITOS
----------
- Python 3.12 de 64 bits con pip.
- Internet para instalar las dependencias de requirements.txt.
- Navegador web.

PREPARACIÓN
-----------
Extraer todo Taller_GrupoB.zip y abrir una terminal en la carpeta que
contiene app.py y requirements.txt.

INSTALACIÓN Y EJECUCIÓN EN WINDOWS
---------------------------------
Ejecutar en PowerShell o Símbolo del sistema:

    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m streamlit run app.py

INSTALACIÓN Y EJECUCIÓN EN macOS O LINUX
-------------------------------------
Con Python 3.12 instalado, ejecutar:

    python3.12 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -m streamlit run app.py

ABRIR Y CERRAR LA APLICACIÓN
---------------------------
Abrir en el navegador la dirección indicada por Streamlit, normalmente:

    http://localhost:8501

Mantener la terminal abierta durante el uso.
Para detener la aplicación, pulsar Ctrl+C en la terminal.

PRUEBAS
-------
Desde la misma carpeta, ejecutar:

Windows:
    .\.venv\Scripts\python.exe -m unittest discover -s tests

macOS o Linux:
    .venv/bin/python -m unittest discover -s tests

Los enlaces de la aplicación y de la conversación con IA están en ENLACES.txt.
