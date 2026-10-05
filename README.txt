TALLER GRUPO B — APLICACIÓN EDUCATIVA DE CONCENTRACIÓN
====================================================

Entrega local: Taller_GrupoB.zip. Proyecto Python con Streamlit y Plotly para
generar mercados hipotéticos, comparar un caso y practicar sus indicadores.
No determina automáticamente una conducta anticompetitiva. La aplicación no
está publicada ni tiene una URL pública verificada.

INSTALACIÓN LOCAL EN WINDOWS
----------------------------
1. Instalar Python 3.12 de 64 bits con pip y el lanzador py. La versión utilizada
   para comprobar esta entrega es Python 3.12.14. No se ha comprobado esta
   entrega con otras versiones de Python ni en otros sistemas operativos.
2. Extraer TODO Taller_GrupoB.zip en una carpeta nueva. No ejecutar dentro del
   ZIP. Abrir PowerShell en esa carpeta, donde se encuentran app.py y
   requirements.txt. Si es necesario, entrar con:

       cd "C:\ruta\a\Taller_GrupoB"

3. Comprobar Python, crear un entorno virtual propio y activarlo:

       py -3.12 --version
       py -3.12 -m venv .venv
       .\.venv\Scripts\Activate.ps1

   En Símbolo del sistema (cmd), la activación es:

       .venv\Scripts\activate.bat

   Si PowerShell bloquea Activate.ps1, no es necesario cambiar la política del
   equipo: utilizar cmd o invocar directamente .\.venv\Scripts\python.exe
   en lugar de python en los comandos siguientes. Si no se dispone de py,
   sustituir py -3.12 por la ruta al python.exe de Python 3.12 instalado.

4. Con el entorno activado, instalar las dependencias de este proyecto:

       python -m pip install -r requirements.txt
       python -m pip check

   El primer comando es la instalación con pip install -r requirements.txt
   asociada al Python del entorno. Se necesita acceso a PyPI o una caché local
   con los paquetes. El ZIP no incluye Python, paquetes ni entorno virtual.
   No se requieren credenciales ni archivos de secretos.

5. Iniciar la aplicación desde la carpeta extraída:

       python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501

   Abrir en el navegador: http://127.0.0.1:8501
   Dirección equivalente: http://localhost:8501
   Mantener la terminal abierta. Ctrl+C detiene el servidor. Si el puerto 8501
   está ocupado, detener el otro servidor o elegir, por ejemplo, --server.port
   8503 y abrir http://127.0.0.1:8503. La dirección es local, no pública.

PRUEBAS
-------
Desde la carpeta extraída y con el mismo entorno activado:

    python -m unittest discover -s tests -v

No es necesario instalar pytest. La suite usa unittest y Streamlit AppTest.
Comprueba cálculos, validaciones, reproducibilidad, motor por lotes, API pública,
gráficos, CSV, estado de la interfaz, bloqueos y evaluación. Las advertencias de
AppTest sobre ScriptRunContext pueden aparecer al probar sin servidor.
COMPROBACIONES.md distingue las pruebas ejecutadas de lo pendiente. BITACORA.md
registra etapas reales; las referencias históricas no son pruebas repetidas ni
sustituyen un enlace compartido de la conversación.

DEPENDENCIAS FIJADAS
-------------------
NumPy 2.3.5, pandas 3.0.1, Plotly 6.9.0, Streamlit 1.65.0 y PyArrow 21.0.0.
requirements.txt contiene exactamente los pins vigentes. pip instala también
sus dependencias transitivas. No se cambiaron fórmulas ni dependencias para
preparar este paquete. La configuración de tema está en .streamlit/config.toml.

USO
---
Configurar N (2 a 100), k (1 a N), iteraciones (inicialmente 1000) y semilla.
Pulsar Simular mercados para ejecutar Monte Carlo; el progreso muestra lotes
completados/total. Se confirma el 100% tras recibir un resultado válido y se
limpia la barra ante errores.

Introducir N porcentajes, usar cuotas iguales, generar un caso aleatorio o
cargar Ejemplo 40–30–20–10. Este último establece N=4 y limita k a 4. Se muestran
la suma y la diferencia con 100%. Cuotas inválidas bloquean comparación y
evaluación; no se normalizan silenciosamente. Cambiar N actualiza la tabla.

Las tarjetas presentan CRk, IHH, ID e IE. El gráfico de cuotas usa porcentajes.
El histograma elegido conserva línea, leyenda y hover del caso e incluye una
etiqueta de dos líneas con valor, unidad y percentil real. Se amplía el rango
si el caso queda fuera; una distribución constante se representa sin fallar.
La etiqueta no se muestra para casos inválidos.

Editar el caso o cambiar el gráfico no ejecuta Monte Carlo. La sesión conserva
solo la última muestra compacta. Cambiar N, k, iteraciones o semilla invalida
su uso y bloquea comparación/evaluación hasta volver a simular. Generar casos
aleatorios usa un generador independiente y no consume la muestra guardada.
Los CSV de muestra y caso se preparan al solicitarlos, con las unidades visibles;
no se acumula un historial de muestras ni de exportaciones.

La clasificación del IHH no tiene respuesta preseleccionada. El feedback indica
acierto/error, IHH, categoría e intervalo; al fallar explica también la selección
y por qué el valor no pertenece a ella. Conserva fórmula, aportes por empresa
y percentil IHH aunque se muestre otro gráfico. Clasifica sin redondear y presenta
suficiente precisión cerca de 1500 y 2500. Cambiar caso, k, simulación o respuesta
limpia los resultados que corresponden. La pregunta numérica CRk admite coma o
punto decimal, rechaza no finitos y usa tolerancia inclusiva de 0,01 puntos
porcentuales; explica la suma de las k mayores cuotas.

FÓRMULAS, VALIDACIÓN Y UNIDADES
------------------------------
Se calculan con proporciones s_i=porcentaje_i/100, conservando los originales.
N y k deben ser enteros, sin booleanos; cada cuota debe ser finita en [0,1].
El cierre exige abs(suma-1)<=1e-10 (tolerancia absoluta), con rtol=0. Se valida
cada fila simulada. La tolerancia contempla representación float64; no repara,
normaliza ni redondea entradas. NumPy y math.fsum pueden diferir unos pocos ulps.

CRk = suma de las k cuotas mayores. Interno: proporción; pantalla/CSV: %.
IHH decimal = suma(s_i**2). IHH en puntos = 10000*IHH decimal.
ID de García Alba = suma(s_i**4)/(suma(s_i**2))**2, adimensional.
IE de Shannon = -suma(s_i*ln(s_i)), en nats; aporte cero si s_i=0.
IE normalizada = IE/ln(N), adimensional. N incluye empresas con cuota nula.
Mayor entropía significa cuotas más repartidas, para N fijo.

Percentil empírico = 100*cantidad(indicador_simulado <= indicador_caso)/M.
Incluye todos los empates exactos, sin interpolación ni tolerancia artificial.
Depende de la muestra. Más iteraciones reducen su variabilidad estadística;
no garantizan que el valor cambie monótonamente. Repetir caso, configuración y
semilla en el mismo entorno permite reproducirlo. No se garantiza la misma
secuencia entre versiones distintas de NumPy. CRk con k=N es matemáticamente
100%; se conservan los residuos float64, sin forzar empates o percentiles.

Evaluación didáctica del IHH en puntos, basada en la guía FNE de mayo de 2022:
  Baja: IHH < 1500.
  Moderada: 1500 <= IHH < 2500.
  Alta: IHH >= 2500.
Convención de fronteras: 1500 es moderada y 2500 es alta. Los cortes clasifican
el nivel; el percentil describe una posición en mercados hipotéticos. No son
lo mismo. La guía también considera variación del IHH y otros antecedentes;
aquí no se reproduce un análisis regulatorio completo. No se inventan umbrales
regulatorios para CRk, ID o IE.

SUPUESTO DE SIMULACIÓN Y LÍMITES
------------------------------
Mercados independientes Dirichlet(1,...,1) con default_rng(semilla): cuotas en
[0,1] que suman el 100% del mercado. Supone empresas simétricas y uniformidad
en el simplex de cuotas, no uniformidad de sus indicadores. No reproduce
automáticamente un sector real. Normalizar uniformes no da la misma distribución;
exponenciales normalizadas sí equivalen a Dirichlet(1). Lognormales y multinomiales
añaden supuestos sobre tamaños o una escala discreta.

Máximo controlado por el motor: 100000 iteraciones; lotes de hasta 4096 filas.
La interfaz retiene cuatro arrays float64: 32*M bytes, aproximadamente 3,05 MiB
al máximo, además de lotes temporales, bibliotecas, gráficos y CSV. Tiempo, CPU
y memoria dependen de N, iteraciones, equipo y concurrencia. La llamada es síncrona.
No son garantías de rendimiento de un servidor público.

medir_rendimiento.py se incluye porque tests/test_compacto.py utiliza su función
de referencia. Su benchmark es opcional, no se ejecuta al iniciar la app:

    python medir_rendimiento.py --salida rendimiento.json

Ese comando genera un resultado local (excluido del ZIP). Las mediciones
históricas y sus límites están identificados en COMPROBACIONES.md; no se afirma
haber repetido el benchmark al preparar esta entrega.

API Y ARCHIVOS VIGENTES
----------------------
La implementación está en concentracion/. Los cuatro módulos homónimos de la
raíz son adaptadores de imports necesarios para usos y pruebas anteriores;
no contienen copias de fórmulas.

Índices públicos (argumentos cuotas,n; CRk añade k): calcular_crk,
calcular_ihh_decimal, calcular_ihh_puntos, calcular_id_garcia_alba,
calcular_entropia y calcular_entropia_normalizada. Devuelven float en las unidades
anteriores. validar_cuotas(cuotas,n) valida exactamente N proporciones; omitir n
es una extensión. Se propagan TypeError/ValueError ante entradas inválidas.

simular_mercados(n,k,iteraciones=1000,semilla=None,*,callback_progreso=None)
devuelve ResultadoSimulacion completo: cuotas (M,N), crk, ihh_decimal, ihh_puntos,
id_garcia_alba, entropia, entropia_normalizada (M,), propiedades n e iteraciones,
y configuracion. Los derivados se calculan al acceder. Esta API sí retiene la
matriz completa y no se utiliza para guardar muestras en la sesión web.

simular_mercados_compactos(n,k,iteraciones=1000,semilla=None,tamano_lote=4096,
                         *,callback_progreso=None)
devuelve ResultadoSimulacionCompacto: crk, ihh_puntos, id, ie y configuracion.
IHH YA está en puntos. callback_progreso(completadas,total) es opcional, recibe
enteros, no arrays, y no consume aleatoriedad. Ambas llamadas anteriores sin
callback siguen siendo válidas. El motor no depende de Streamlit.

También disponibles: calcular_indicadores_vectorizados(cuotas,n,k) -> dict de
seis arrays; calcular_percentil_empirico(valores_simulados,valor_caso) -> float
en %; compactar_resultado(resultado) -> copia compacta sin cuotas.

Gráficos: crear_grafico_cuotas, crear_histograma_comparativo -> Figure Plotly;
convertir_valor_presentacion -> float; obtener_valores_simulados -> array (M,)
en unidades de presentación; formatear_numero_indicador, formatear_valor_indicador
y nombre_eje_indicador -> str. Evaluación: evaluar_respuesta_ihh -> dict;
intervalo_ihh -> str; huella_cuotas -> tuple de proporciones validada. Los
docstrings documentan firmas, unidades y errores exactos de esta implementación.
Los resultados con arrays se comparan por identidad para evitar booleanos ambiguos.

Se prueban llamadas y resultados, no solo imports. No se afirma compatibilidad
universal con detalles históricos no facilitados: faltan firmas/retornos antiguos
exactos de adaptadores de gráficos/evaluación, retorno vectorizado y constructor
de ResultadoSimulacion para demostrar identidad de esos detalles.

CONTENIDO DEL ZIP (26 ARCHIVOS)
------------------------------
app.py
indices.py
simulacion.py
graficos.py
evaluacion.py
medir_rendimiento.py
requirements.txt
README.txt
README.md
.gitignore
COMPROBACIONES.md
BITACORA.md
.streamlit/config.toml
concentracion/__init__.py
concentracion/indices.py
concentracion/simulacion.py
concentracion/graficos.py
concentracion/evaluacion.py
tests/test_indices.py
tests/test_simulacion.py
tests/test_compacto.py
tests/test_graficos.py
tests/test_evaluacion.py
tests/test_app.py
tests/test_compatibilidad.py
tests/test_progreso.py

No hacen falta imágenes ni recursos externos para el arranque. Se excluyen
ZIP anteriores, .venv, .git, cachés, temporales, resultados generados de pruebas,
rendimiento.json, capturas históricas y el empaquetador de versiones anteriores.

PUBLICACIÓN EN GITHUB Y STREAMLIT COMMUNITY CLOUD
------------------------------------------------
Estado comprobado el 5 de octubre de 2026:
  Cuenta GitHub reconocida por el conector: Jm7z.
  Repositorio público Taller_GrupoB: creación comprobada; fuentes en preparación.
  URL real de GitHub: https://github.com/Jm7z/Taller_GrupoB
  Rama comprobada: main; conector con permiso admin/push.
  URL real de aplicación: pendiente de despliegue y comprobación.
  Python en Cloud: seleccionar 3.12; parche exacto aún no observado en logs.
  Commit servido por Cloud y acceso privado/anónimo: pendientes.
No sustituir estas líneas por direcciones supuestas. Python local 3.12.14 no
demuestra que Cloud instale el mismo parche. No se ha enviado ningún correo.

La carpeta de fuentes preparada contiene únicamente archivos vigentes. Los
módulos, fórmulas, generadores, cuatro series compactas, CSV y evaluación se
conservan. requirements.txt no cambió. .gitignore se comprobó con git check-ignore:
entornos, cachés, temporales, logs, ZIP y secretos quedan excluidos; app.py,
README.txt, requirements.txt, configuración y pruebas permanecen publicables.
.streamlit/config.toml no fija dirección, puerto ni certificados: Cloud gestiona
el servidor y HTTPS. Se comprobó su lectura con Streamlit local, no en Cloud.

A. Crear el repositorio (paso de cuenta)
1. En el navegador de Windows, iniciar sesión personalmente en https://github.com.
2. Abrir https://github.com/new; Owner: Jm7z; Repository name: Taller_GrupoB;
   visibilidad Public. Marcar Add a README file para disponer de una rama inicial.
   No activar generación automática de código. Pulsar Create repository.
3. Si se utiliza el conector de Codex, habilitar el nuevo repositorio en el acceso
   de su integración de GitHub cuando sea necesario. No pegar contraseñas o
   tokens en conversaciones ni archivos. Tras la creación comprobar el nombre,
   visibilidad pública y rama real; aquí se propone main.

B. Subir desde PowerShell si debe hacerlo el usuario
Instalar Git for Windows desde https://git-scm.com/download/win, con Git Credential
Manager. La autenticación HTTPS se completa en su ventana oficial de navegador.
Si se usa GitHub CLI, instalarlo desde https://cli.github.com y ejecutar:

    gh auth login --hostname github.com --git-protocol https --web
    gh auth setup-git

GitHub CLI no es una dependencia de la app y no es necesario si se usa GCM.
No utilizar una contraseña de GitHub como contraseña de Git ni introducir tokens
en la conversación. Completar personalmente 2FA, CAPTCHA o aceptación de términos.

Con el repositorio ya creado e inicializado, el siguiente procedimiento evita
conflictos con su README inicial. Ajustar únicamente las rutas locales. La URL
del comando es el destino previsto, NO prueba de que exista hasta comprobarlo:

    $fuentesTaller = "C:\ruta\a\Taller_GrupoB_extraido"
    $repoTaller = "C:\ruta\a\Taller_GrupoB_git"
    git clone https://github.com/Jm7z/Taller_GrupoB.git $repoTaller
    Get-ChildItem -LiteralPath $fuentesTaller -Force |
        Where-Object { $_.Name -notin @('.git', '.venv', '__pycache__') } |
        Copy-Item -Destination $repoTaller -Recurse -Force
    Set-Location -LiteralPath $repoTaller
    git branch --show-current
    git status --short
    git add .
    git diff --cached --stat
    git diff --cached --name-only
    git commit -m "Publicar Taller_GrupoB con fuentes y pruebas vigentes"
    git push origin main
    git rev-parse HEAD
    git ls-remote origin refs/heads/main

Usar la carpeta del ZIP recién extraído, antes de crear allí un entorno o logs.
Las rutas fuente/destino deben ser distintas y el destino no debe existir antes
de git clone. Si la rama real no es main, usar su nombre en push, ls-remote y Cloud.
Si git commit pide identidad, configurar user.name y user.email del repositorio
con los datos de tu cuenta (se puede usar el correo noreply mostrado por GitHub).
No se proporciona un correo personal ni se configura globalmente por defecto.
Comprobar que el SHA local y remoto coinciden y abrir GitHub para revisar los
26 archivos, estructura, Public y ausencia de secretos. No utilizar push --force.

C. Desplegar en Streamlit (pasos de cuenta)
1. Abrir https://share.streamlit.io e iniciar sesión personalmente. La pantalla
   de acceso vincula el inicio a sus términos: esa aceptación debe hacerla el
   usuario. Conectar GitHub en Workspaces > Connect GitHub account y autorizar
   Streamlit mediante su flujo oficial. Seleccionar el workspace Jm7z.
2. Create app > Yup, I have an app. Repositorio: Taller_GrupoB; rama: la publicada
   y comprobada; Main file path: app.py. App URL: solicitar taller-grupob.
   Si no está disponible, escoger un nombre aceptado y registrar la URL real.
3. Advanced settings > Python version > 3.12 > Save. Verificar esa elección antes
   de Deploy. No hay secretos que configurar. Cambiar Python tras desplegar
   requiere eliminar/recrear el despliegue; no hacerlo silenciosamente.
4. Deploy. Revisar logs: repositorio/rama/archivo, versión Python exacta que figure,
   instalación de requirements.txt y arranque. Cloud usa Linux y puede usar uv
   con fallback pip. No cambiar pins sin un error concreto demostrado.
5. Manage app > menú > Download log. Registrar fecha, versión exacta observada,
   commit si aparece y errores. No suponer un SHA o parche si el log no lo muestra.
   Si faltan esos datos, mantenerlos como pendientes hasta obtener evidencia.
6. Settings > Sharing > Who can view this app > This app is public and searchable.
   Aunque un repo público genera una app pública por defecto, comprobar el ajuste.
7. Copiar la URL HTTPS realmente asignada. README y COMPROBACIONES deben actualizarse
   con enlaces reales, datos y resultados; publicar ese cambio con add/commit/push.
   Comprobar la actualización en Cloud y su versión. Un push aprobado no demuestra
   por sí solo el commit exacto que sirve la aplicación.

D. Verificar acceso público y funcionamiento desplegado
En Edge o Chrome, Ctrl+Shift+N abre InPrivate/incógnito. Pegar la URL HTTPS real
sin sesión iniciada. No considerar la sesión de administrador como prueba anónima.
Si pide autorización, corregir Sharing; si hiberna, pulsar Yes, get this app back up!
y esperar a que termine. No confundir esa espera con falta de acceso público.

Registrar en COMPROBACIONES fecha (America/Santiago), URL real, versión/commit
observados y cada resultado, incluyendo errores o pruebas pendientes:
  - CRk, IHH, ID e IE; unidades; histograma, línea, etiqueta, hover y percentil.
  - N=2 y N=100; cambios de k e iteraciones; progreso completadas/total.
  - Entrada manual de cuotas, iguales, ejemplo y caso aleatorio independiente.
  - N=4,k=2,M=1000,semilla=42; cuotas 40,30,20,10: CR2=70%, IHH≈3000 puntos.
    Anotar el percentil observado; la referencia local es 171/1000=17,1% con
    NumPy 2.3.5, no un valor que deba forzarse en Cloud.
  - Clasificación Alta correcta y Baja/Moderada incorrectas; explicación de intervalos,
    aportes y precisión; CR2 numérico 70 y 60. Limpiar feedback al editar respuesta/caso.
  - Cuotas inválidas (por ejemplo suma 90%) bloquean comparación/evaluación sin
    normalización; modificar configuración invalida la muestra y obliga a simular.
  - Editar caso o elegir otro gráfico conserva muestra; evaluación siempre usa IHH.
  - Descargar ambos CSV: muestra con M filas, configuración/unidades correctas;
    caso con N filas y porcentajes exactos. No publicar los CSV de pruebas.
  - Escritorio y viewport móvil; indicar si solo se emuló un ancho o se usó teléfono.

E. Recursos e hibernación
Cloud tiene límites de CPU, memoria y almacenamiento que pueden cambiar. Su
documentación ofrece cifras aproximadas con fecha de referencia anterior, no
una capacidad garantizada para esta app. Llamadas síncronas, CSV y concurrencia
pueden ralentizarla o detenerla. Mantener máximo 100000, lotes de hasta 4096 y
cuatro series; los 3,05 MiB son solo arrays, no memoria total del servidor.
Según la documentación oficial consultada, hiberna tras 12 horas sin tráfico;
un visitante autorizado puede despertarla. Puede haber espera inicial y pérdida
de estado de sesiones. El ajuste local gatherUsageStats=false puede ser sobrescrito
por Cloud y no prueba la configuración de telemetría del servicio.

FUENTES OFICIALES
-----------------
FNE, mayo de 2022, sección III.B, pp. 15–16, párrafos 32–36:
https://www.fne.gob.cl/wp-content/uploads/2022/05/20220531.-Guia-para-el-Analisis-de-Operaciones-de-Concentracion-Horizontales-version-final-en-castellano.pdf
NumPy, Dirichlet:
https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.dirichlet.html
NumPy, default_rng y reproducción:
https://numpy.org/doc/stable/reference/random/generator.html
Streamlit, descarga diferida:
https://docs.streamlit.io/develop/api-reference/widgets/st.download_button
Streamlit Community Cloud, despliegue y acceso:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
Streamlit, GitHub, archivos, dependencias, registros y límites:
https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
https://docs.streamlit.io/deploy/streamlit-community-cloud/status
GitHub, repositorios, autenticación y Git Credential Manager:
https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository
https://docs.github.com/en/get-started/git-basics/set-up-git
https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git
