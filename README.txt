TALLER GRUPO B — APLICACIÓN EDUCATIVA DE CONCENTRACIÓN
====================================================

Proyecto Python con Streamlit y Plotly para generar mercados hipotéticos,
comparar un caso y practicar sus indicadores. No determina automáticamente una
conducta anticompetitiva.

Repositorio: https://github.com/Jm7z/Taller_GrupoB
Aplicación existente: https://taller-grupob.streamlit.app/
Entrega: Taller_GrupoB.zip, con fuentes, dependencias, configuración y pruebas.

La publicación anterior fue comprobada el 5 de octubre de 2026. La corrección
local de CRk cuando k=N está implementada y verificada. El cierre actual añade
ayudas, explicación del percentil, resumen del IHH para muchas empresas y
advertencia breve de recursos. Las comprobaciones de esa actualización, su
publicación y el ZIP final se registran por separado en COMPROBACIONES.md;
no se atribuyen a ella las pruebas del despliegue anterior.

INSTALACIÓN LOCAL EN WINDOWS
----------------------------
1. Instalar Python 3.12 de 64 bits con pip y el lanzador py. La versión utilizada
   para las pruebas locales es Python 3.12.14. En los logs del despliegue se
   observó Python 3.12.15 en Linux, también en el nuevo arranque del
   2026-10-06 a las 00:19:22.304 UTC. La suite no se ejecutó en Community
   Cloud; no se deben equiparar las pruebas locales con el arranque remoto.
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

Corrección local de CRN: 128 pruebas aprobadas en 26,212 s, con Python 3.12.14.
Incluye las 116 anteriores y 12 regresiones específicas. La comparación contra
el estado anterior realizó 135 verificaciones de cuotas, indicadores y
percentiles: para k<N se conservaron los resultados; para k=N solo cambió CRN.
N=100, k=100, M=1000, semilla 42 y cien cuotas de 1 %: antes, percentil 67,2 % y
CR simulado entre 0,9999999999999989 y 1,0000000000000009; después, cada CRN es
1,0 exacto y el percentil 100,0 %. No se modificó el percentil general.

Estos resultados corresponden al parche local anterior a las nuevas ayudas.
Después de incorporarlas, la suite actual aprobó 136 de 136 pruebas en
21,542 s; test_claridad.py aprobó 8 de 8 en 2,916 s. El entorno local fue
Python 3.12.14 con NumPy 2.3.5. La publicación y las comprobaciones públicas
actuales se describen más abajo. El paquete de cierre también se verificó desde
una extracción nueva; el resultado se registra a continuación. Una extracción de la publicación
anterior aprobó 116 pruebas en 20,011 s, instalación offline y pip check en un
entorno independiente, y arranque HTTP 200; no acredita la nueva versión.

El candidato actual de prepublicación contiene 30 archivos, con CRC válido y
bytes idénticos a las fuentes. Se extrajo en una carpeta nueva y se creó otro
entorno Python 3.12.14, sin paquetes del sistema ni del usuario. Se instalaron
40 paquetes offline desde wheels existentes y el requirements.txt extraído;
los pins se conservaron y pip check informó "No broken requirements found".
Con imports aislados (modo -I), la extracción aprobó 136 de 136 pruebas en
21,9598442 s, sin errores ni fallos. Las fuentes se importaron únicamente desde
esa extracción y las dependencias desde su entorno nuevo. Esto verifica el
candidato de prepublicación, no el ZIP definitivo ni el despliegue actualizado.
El servidor iniciado desde esa extracción respondió HTTP 200 en raíz y salud,
y el navegador mostró los controles y simuló el caso predeterminado sin error:
N=4,k=2, M=1000,semilla 42, cuotas iguales, CR2=50 %, percentil 0 %, progreso
1000/1000 al 100 %, línea y etiqueta del caso visibles. La verificación usó
127.0.0.1:8513; la instalación normal del manual utiliza el puerto 8501.

CIERRE: PAQUETE EXTRAÍDO Y ENTORNO NUEVO
---------------------------------------
El ZIP de cierre comprobado antes de esta última actualización documental tenía
30 archivos, CRC válido y bytes idénticos a las fuentes. Se extrajo en otra
carpeta nueva, extraido_cierre_actual, y se creó un nuevo entorno .venv_final
Python 3.12.14 aislado, sin paquetes del sistema ni del usuario. Se instalaron
40 paquetes offline utilizando su requirements.txt EXTRAÍDO, pins intactos;
pip check aprobó. La suite completa aprobó 136/136, cero errores/fallos, en
22,8258215 s. Las fuentes procedieron solo de esa nueva extracción y las
dependencias solo de su nuevo entorno.

El servidor propio de esa extracción, en 127.0.0.1:8514, respondió HTTP 200 en
raíz y salud/ok. El navegador real renderizó controles y simuló N=100/k=100,
1000 iteraciones, semilla 42 y cuotas iguales: CR100=100 %, percentil 100 %,
progreso 1000/1000, línea y etiqueta visibles, sin error. Código, pruebas,
dependencias y configuración no cambian por esta última edición documental.

El resumen final de entrega identifica el archivo definitivo, su commit y
cotejo de bytes, CRC/manifiesto y la comprobación de su extracción exacta.
Estos documentos no inventan el hash, el tiempo ni el resultado de una
verificación posterior a su propia publicación y no incorporan un SHA
autorreferencial. Se distingue ese cierre externo del paquete aquí comprobado.

DEPENDENCIAS FIJADAS
-------------------
NumPy 2.3.5, pandas 3.0.1, Plotly 6.9.0, Streamlit 1.65.0 y PyArrow 21.0.0.
requirements.txt contiene exactamente los pins vigentes. pip instala también
sus dependencias transitivas. Los pins no cambian. El único ajuste matemático
de este cierre es aplicar la identidad exacta CRN=1 a cuotas ya validadas.
La configuración de tema está en .streamlit/config.toml.

USO
---
Configurar N (2 a 100), k (1 a N), iteraciones (inicialmente 1000) y semilla.
Pulsar Simular mercados para ejecutar Monte Carlo; el progreso muestra lotes
completados/total. Se confirma el 100 % tras recibir un resultado válido y se
limpia la barra ante errores.

Introducir N porcentajes, usar cuotas iguales, generar un caso aleatorio o
cargar Ejemplo 40–30–20–10. Este último establece N=4 y limita k a 4. Se muestran
la suma y la diferencia con 100 %. Cuotas inválidas bloquean comparación y
evaluación; no se normalizan silenciosamente. Cambiar N actualiza la tabla.

Las tarjetas presentan CRk, IHH, ID e IE. La ayuda del selector explica el
indicador elegido. El gráfico de cuotas usa porcentajes.
El histograma elegido conserva línea, leyenda y hover del caso e incluye una
etiqueta de dos líneas con valor, unidad y percentil real. Se amplía el rango
si el caso queda fuera; una distribución constante se representa sin fallar.
La etiqueta no se muestra para casos inválidos.

La lectura del percentil indica qué porcentaje de la muestra tiene un valor
menor o igual al del caso e incluye empates. Compara mercados con el mismo N
bajo Dirichlet(1,...,1), no un umbral normativo. Para IE, un percentil alto
indica mayor entropía respecto de la muestra, no mayor concentración.
Cuando k=N, CRk es 100 % en todos los mercados: no distingue concentración,
todos los valores empatan y el percentil inclusivo es exactamente 100 %.

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

Para N<=12 se muestra el desarrollo de la suma de cuadrados. Para N>12, el
resumen muestra N, las cinco cuotas mayores y el IHH calculado con TODAS las
cuotas. El desarrollo íntegro y la tabla de aportes siguen disponibles en un
desplegable. El resumen es presentación: no recalcula el IHH ni cambia el
contrato del evaluador. El percentil de evaluación usa siempre la muestra de
IHH, aunque el histograma seleccionado represente otro indicador.

FÓRMULAS, VALIDACIÓN Y UNIDADES
------------------------------
Se calculan con proporciones s_i=porcentaje_i/100, conservando los originales.
N y k deben ser enteros, sin booleanos; cada cuota debe ser finita en [0,1].
El cierre exige abs(suma-1)<=1e-10 (tolerancia absoluta), con rtol=0. Se valida
cada fila simulada. La tolerancia contempla representación float64; no repara,
normaliza ni redondea entradas. NumPy y math.fsum pueden diferir unos pocos ulps.

CRk = suma de las k cuotas mayores. Interno: proporción; pantalla/CSV: %.
Tras validar cuotas y k, si k=N se aplica CRN=1,0 exacto en escalar/vectorizado.
Esta identidad no modifica las cuotas originales ni el cierre tolerado.
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
secuencia entre versiones distintas de NumPy. CRN usa la identidad exacta de
mercado completo: todos sus valores son 1,0 y el percentil resulta 100,0 % por la
misma comparación <=, sin excepciones ni tolerancias en la función de percentil.
Para k<N se conservan las sumas originales sin redondear. No se corrigen de
forma general los residuos de representación de otros indicadores.

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
[0,1] que suman el 100 % del mercado. Supone empresas simétricas y uniformidad
en el simplex de cuotas, no uniformidad de sus indicadores. No reproduce
automáticamente un sector real. Normalizar uniformes no da la misma distribución;
exponenciales normalizadas sí equivalen a Dirichlet(1). Lognormales y multinomiales
añaden supuestos sobre tamaños o una escala discreta.

Máximo controlado por el motor: 100000 iteraciones; lotes de hasta 4096 filas.
La interfaz retiene cuatro arrays float64: 32*M bytes, aproximadamente 3,05 MiB
al máximo, además de lotes temporales, bibliotecas, gráficos y CSV. Tiempo, CPU
y memoria dependen de N, iteraciones, equipo y concurrencia. La llamada es síncrona.
No son garantías de rendimiento de un servidor público.

La advertencia principal resume tiempo, memoria y procesamiento y el máximo
permitido. "Detalles de rendimiento" conserva el aviso técnico completo.
El aviso adicional a partir de 50000 iteraciones permanece disponible.

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

La identidad CRN llega a calcular_crk mediante crk y a ambos motores mediante
_calcular_indicadores. calcular_indicadores_vectorizados y los adaptadores de
raíz reutilizan esas rutas. Histograma y CSV consumen los resultados; no tienen
otra fórmula especial para calcular el percentil ni para producir CRN.

ESTRUCTURA DE FUENTES NECESARIAS
-------------------------------
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
tests/test_crn.py
tests/test_crn_interfaz.py
tests/test_claridad.py
ENLACES.txt

Esta estructura tiene 30 archivos, cotejados en los paquetes de prepublicación
y cierre. El resumen final identifica el manifiesto del archivo entregado y
su correspondencia comprobada con el repositorio; la lista por sí sola no es
una prueba de integridad ni de publicación.

No hacen falta imágenes ni recursos externos para el arranque. Se excluyen
ZIP anteriores, .venv, .git, cachés, temporales, resultados generados de pruebas,
rendimiento.json, capturas históricas y el empaquetador de versiones anteriores.

Después del punto de recuperación Git se retiraron 23 duplicados de raíz,
cotejados byte a byte con las fuentes conservadas, dos ZIP antiguos inspeccionados
y tres archivos regenerables: empaquetar.py, registro_pruebas.txt y
rendimiento.json. Se retiraron cachés y carpetas duplicadas vacías. Tres documentos
históricos se trasladaron a un archivo local fuera de entrega; no se destruyeron.
Se conservan historial Git, entorno de desarrollo, evidencia y herramientas fuera
de la carpeta canónica. Los adaptadores y el helper de rendimiento permanecen
porque tienen usos comprobados. El candidato no contiene esos residuos.

PUBLICACIÓN EN GITHUB Y STREAMLIT COMMUNITY CLOUD
------------------------------------------------
Comprobaciones HISTÓRICAS de la publicación anterior, 5 de octubre de 2026:
  Cuenta GitHub reconocida por el conector: Jm7z.
  Repositorio público Taller_GrupoB: fuentes publicadas; 26 archivos cotejados
  byte a byte con la carpeta limpia de fuentes antes de esta actualización.
  URL real de GitHub: https://github.com/Jm7z/Taller_GrupoB
  Rama comprobada: main; conector con permiso admin/push.
  Commit de código publicado y cotejado:
  0868937507fa00a2c7effe9dc4dabbc86514d4a6.
  Commit documental final de esa entrega:
  8a6206c77be2f8935587748f5e457c626ccff896.
  URL real de aplicación: https://taller-grupob.streamlit.app/
  Python seleccionado en Cloud: 3.12; versión exacta observada en logs: 3.12.15.
  Pins de requirements.txt instalados sin modificación; arranque registrado
  en logs el 2026-10-05 a las 17:26:22 UTC (14:26:22 America/Santiago).
  Sharing comprobado: This app is public and searchable.
  Reinicio comprobado en logs: desconexión 17:35:15 UTC y arranque del servidor
  17:35:59.355 UTC (14:35:59.355 America/Santiago), el mismo día, con Python 3.12.15.
  Tras el reinicio, una sesión nueva simuló 1000 mercados y completó el 100 %.
  Acceso InPrivate/incógnito sin sesión: el usuario informó, tras Ctrl+F5,
  "Sí, ahora simula correctamente sin iniciar sesión". No se presenta como
  observación directa de una ventana privada realizada por la herramienta.
  Suite en Linux/Community Cloud: no ejecutada.
  Documentación de aquella entrega incluida junto a las fuentes en main.
  Su ZIP de 26 archivos se cotejó con el commit documental mencionado.
  SHA exacto del proceso Cloud: pendiente; los logs disponibles no lo expusieron.
El SHA anterior identifica el código cotejado, no demuestra por sí solo el SHA
del proceso activo en Cloud. Python local 3.12.14 no coincide con el parche
observado en Cloud. No se ha enviado ningún correo.

Comprobaciones de la interfaz del despliegue ANTERIOR: N=4, k=2, 1000 iteraciones
y semilla 42;
ejemplo 40-30-20-10; CR2=70 %, IHH interno=3000.0000000000005 puntos y percentil IHH
17,1 % (171 de 1000 mercados con IHH menor o igual). Se comprobó clasificación
Moderada incorrecta, Alta correcta y respuesta numérica CR2 70,00 correcta.
El usuario informó mediante captura un error de callback inesperado, aunque
otra sesión ejecutó correctamente la simulación y el código remoto coincidía.
Después del reinicio comprobado, una sesión nueva simuló correctamente y el
usuario confirmó lo mismo sin sesión. No se modificaron las fuentes por este
incidente: la firma del callback y el código publicado se cotejaron. La causa
exacta del error no quedó demostrada; la recuperación observada no la demuestra.

Otras comprobaciones históricas de la aplicación remota, sin acreditar el nuevo
parche ni sus nuevas ayudas:
  - N=2,k=2, M=1000: distribución aparentemente constante. En esa versión CRN
    conservaba residuos flotantes: esa dispersión ya está corregida localmente.
    Cambiar a k=1
    y M=5000 marcó la muestra desactualizada; volver a simular funcionó.
  - N=100,k=100, M=5000: simulación correcta. El botón del ejemplo pasó de N=100
    a N=4, limitó k a 4 y bloqueó la comparación por muestra incompatible.
    Se volvió después a k=2 y M=1000.
  - Edición manual 40->30: suma 90 %, falta 10 %; cuotas rechazadas, sin etiqueta
    del caso y con respuestas bloqueadas. Se conservó la muestra y el tiempo
    de motor.
    Dos pulsaciones de caso aleatorio dieron cuotas diferentes, conservaron
    la referencia de simulación y limpiaron la retroalimentación.
  - CSV descargados desde el navegador: muestra 1000 filas x 11 columnas y caso
    4 filas x 2 columnas. Lectura posterior con pandas y float_precision="round_trip":
    diferencia máxima 0,0 respecto del motor local en CRk (%), IHH (puntos), ID,
    IE e IE/ln(N). Metadatos N=4,k=2,semilla=42,NumPy=2.3.5; cuotas del caso
    exactamente 40,30,20,10. Esto no supone ejecutar la suite completa en Linux.
  - Los cuatro histogramas se revisaron en escritorio 960x900 y viewport móvil
    390x844: etiquetas dentro del gráfico en dos líneas, leyenda y ejes visibles,
    sin desbordamiento horizontal a 390 px. Se emuló el ancho; no se usó teléfono
    físico. La barra de herramientas Plotly activa puede cubrir parte del título
    en móvil; se registra esta limitación sin modificar el código.
  - Hover del histograma IHH observado: Simulación, intervalo 2938,57-3152,53,
    109 mercados. Hover de la línea verificado en navegador: Caso: 3000 puntos
    (0-10000), con percentil 17,10 mostrado en su información emergente.
  - Progreso final observado: 5000/5000, 100 %. No se capturaron visualmente estados
    intermedios; el avance por lotes, callback y limpieza ante errores tienen
    cobertura en las 13 pruebas de tests/test_progreso.py incluidas en la suite.
El SHA exacto del proceso Cloud no fue expuesto en los logs históricos.
La actualización actual del código está publicada y comprobada en Cloud.
La extracción del paquete de cierre se verificó como se describe en PRUEBAS.
El resumen final identifica el archivo definitivo y su cotejo. El usuario confirmó la
prueba interactiva actual desde la ventana privada solicitada, sin iniciar sesión.

Antes de actualizar el proyecto se preservó el estado inicial pertinente en
Git, commit 61d769c03ad507ae417b7a5c9892299618100cd6. Este es un punto local de
recuperación; no se presenta como commit desplegado. El commit final y la
correspondencia del nuevo ZIP con GitHub se registran después de verificarlos.

ACTUALIZACIÓN PÚBLICA COMPROBADA
-------------------------------
Código publicado en main mediante avance normal, sin force push:
9f5d425a4ff793f4b18f2c33019516f48a6e1a0a, padre 8a6206c77be2f8935587748f5e457c626ccff896.
Los 30 archivos remotos se recuperaron y cotejaron: idénticos a las fuentes.
Árbol completo, sin truncar: ad354e723090cf39d6493cb2ad2b4bc4baaebd21.
Un commit posterior de cierre documental se identifica en el resumen de entrega;
no se incorpora una supuesta referencia autorreferencial en estos documentos.

Cloud notificó actualización a las00:15:49 UTC del 6 de octubre (21:15:49 del 5
en America/Santiago). La interfaz mostraba las ayudas nuevas, pero una sesión
aún produjo el percentil CR100 defectuoso 67,2 %. No se consideró aprobado.
Tras reiniciar el servicio existente, logs: desconexión 00:19:04 UTC y nuevo
arranque Uvicorn 2026-10-06 00:19:22.304 UTC (21:19:22.304 del 5 local).
La instalación mediante uv registró37 paquetes más 4 de rich gestionados por
Cloud; Python 3.12.15 y los cinco pins del proyecto permanecieron intactos.
No se afirma la causa exacta del estado anterior ni un SHA interno del servidor:
los logs no expusieron ese SHA. La suite completa no se ejecutó dentro de Cloud.

Una sesión nueva simuló el caso predeterminado. Para N=100/k=100/M=1000/semilla 42,
cien cuotas de 1 %, mostró CR100=100 % y percentil 100 %, histograma constante,
línea y etiqueta 100 %; se revisó escritorio 960×900 y móvil emulado 390×844.
Los CSV descargados tuvieron 1000×11 y 100×2: todos los CR porcentuales fueron
exactamente 100 y todas las cuotas del caso 1 %. La lectura round_trip comparada
con la extracción local tuvo diferencia máxima 0,0 en CR, IHH, ID, IE e IE/lnN;
metadatos N=100/k=100/semilla 42/NumPy 2.3.5.

La evaluación del caso N=100 aceptó Baja: IHH 100 puntos y percentil IHH 0 %.
El resumen mostró N y las cinco mayores cuotas; el desplegable conservó el
desarrollo y la tabla completa de 100 empresas. Ejemplo desde N=100 estableció
N=4/k=4, bloqueó la muestra incompatible y limpió feedback. Al pasar a k=2 y
simular de nuevo, CR2=70 %, IHH interno 3000.0000000000005 puntos, percentiles
CRk 23,4 % e IHH 17,1 %. La selección Moderada se rechazó con su intervalo y el
desarrollo íntegro de las cuatro cuotas.

Otra pestaña nueva después del reinicio comprobó los cuatro indicadores del
ejemplo: CRk 23,4 %, IHH 17,1 %, ID 20,5 % e IE 82,3 %; sus ayudas, unidades,
ejes, leyenda, línea y etiqueta se mostraron sin error. La etiqueta ID presentó
0,393333 adimensional e IE 1,279854 nats. Cambiar el gráfico conservó el tiempo
del motor 0,001709 s. Con IE visualizado, Alta fue correcta y mantuvo IHH
3000.0000000000005 puntos, percentil 17,1 % (171/1000) y las cuatro cuotas.

Settings General confirmó Python 3.12 y Sharing confirmó This app is public
and searchable. El2026-10-06T00:22:05 UTC, una petición HTTP independiente a
la raíz e iframe de la app respondió200 con jar vacía, sin credenciales.
Esto comprueba carga HTTP anónima. Además, el usuario probó esta actualización
en la ventana privada Edge solicitada, sin iniciar sesión, N=100/k=100/M=1000,
semilla 42 y cuotas iguales, y respondió: "Sí: la aplicación publicada mostró
CR100 = 100,00 % y percentil = 100,00 %, sin errores visibles en esta prueba."
Esta comprobación interactiva fue reportada por el usuario; la herramienta
no observó directamente su ventana privada.

La carpeta de fuentes preparada contiene únicamente archivos vigentes. Los
módulos, generadores, cuatro series compactas, CSV y evaluación se conservan;
CRN aplica la identidad exacta explicada anteriormente. requirements.txt no
cambió. .gitignore se comprobó históricamente con git check-ignore:
entornos, cachés, temporales, logs, ZIP y secretos quedan excluidos; app.py,
README.txt, requirements.txt, configuración y pruebas permanecen publicables.
.streamlit/config.toml no fija dirección, puerto ni certificados: Cloud gestiona
el servidor y HTTPS. Se comprobó su lectura local; el despliegue con el archivo
publicado arrancó. Esto no demuestra que Cloud respete ajustes que sobrescribe.

A. Repositorio existente y reproducción de la publicación
El repositorio público indicado ya existe y sus fuentes fueron comprobadas.
No es necesario crear otro para continuar. Si se reproduce el procedimiento
en otra cuenta, los pasos oficiales son:
1. En el navegador de Windows, iniciar sesión personalmente en https://github.com.
2. Abrir https://github.com/new; Owner: Jm7z; Repository name: Taller_GrupoB;
   visibilidad Public. Marcar Add a README file para disponer de una rama inicial.
   No activar generación automática de código. Pulsar Create repository.
3. Si se utiliza el conector de Codex, habilitar el nuevo repositorio en el acceso
   de su integración de GitHub cuando sea necesario. No pegar contraseñas o
   tokens en conversaciones ni archivos. Tras la creación comprobar el nombre,
   visibilidad pública y rama real. En este proyecto se comprobó main.

B. Subir desde PowerShell si debe hacerlo el usuario
Instalar Git for Windows desde https://git-scm.com/download/win, con Git Credential
Manager. La autenticación HTTPS se completa en su ventana oficial de navegador.
Si se usa GitHub CLI, instalarlo desde https://cli.github.com y ejecutar:

    gh auth login --hostname github.com --git-protocol https --web
    gh auth setup-git

GitHub CLI no es una dependencia de la app y no es necesario si se usa GCM.
No utilizar una contraseña de GitHub como contraseña de Git ni introducir tokens
en la conversación. Completar personalmente 2FA, CAPTCHA o aceptación de términos.

Con el repositorio existente, el siguiente procedimiento permite actualizarlo
desde una carpeta limpia extraída. Ajustar únicamente las rutas locales. La URL
del comando corresponde al repositorio público comprobado:

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
archivos del manifiesto vigente, estructura, Public y ausencia de secretos.
No utilizar push --force.

C. Desplegar en Streamlit (pasos de cuenta)
1. Para este proyecto, abrir la aplicación EXISTENTE en https://share.streamlit.io.
   Los cambios de main deben actualizar ese despliegue; no crear otra app.
   Para reproducir la instalación en otra cuenta, iniciar sesión personalmente.
   La pantalla
   de acceso vincula el inicio a sus términos: esa aceptación debe hacerla el
   usuario. Conectar GitHub en Workspaces > Connect GitHub account y autorizar
   Streamlit mediante su flujo oficial. Seleccionar el workspace Jm7z.
2. Create app > Deploy from repo. Repositorio: Taller_GrupoB; rama: main;
   Main file path: app.py. App URL: taller-grupob fue aceptado en este despliegue.
   Si no está disponible, escoger un nombre aceptado y registrar la URL real.
3. En las opciones avanzadas de despliegue, Python version > 3.12 > Save.
   Verificar esa elección antes de Deploy; en este despliegue se comprobó 3.12
   y los logs mostraron 3.12.15. No hay secretos que configurar. Cambiar Python
   tras desplegar requiere eliminar/recrear el despliegue; no hacerlo silenciosamente.
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
  - N=4,k=2, M=1000,semilla=42; cuotas 40,30,20,10: CR2=70 %, IHH≈3000 puntos.
    Anotar el percentil observado; la referencia local es 171/1000=17,1 % con
    NumPy 2.3.5, no un valor que deba forzarse en Cloud.
  - N=100,k=100, M=1000,semilla=42; cien cuotas de 1 %: CR100=100 % y percentil
    exactamente 100 %. Confirmar ayuda de identidad, histograma constante,
    marcador/etiqueta y valores originales de CSV.
  - Ayuda de cada indicador y lectura del percentil con resultados reales.
    Con IE, aclaración de mayor reparto; la evaluación conserva percentil IHH.
  - Justificación de evaluación corta para N<=12 y resumen para N>12 con las
    cinco mayores cuotas; desplegable con desarrollo y aportes completos.
  - Advertencia breve de recursos, detalles técnicos y aviso desde 50000.
  - Clasificación Alta correcta y Baja/Moderada incorrectas; explicación de intervalos,
    aportes y precisión; CR2 numérico 70 y 60. Limpiar feedback al editar respuesta/caso.
  - Cuotas inválidas (por ejemplo suma 90 %) bloquean comparación/evaluación sin
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

TRANSPARENCIA EN EL USO DE IA
-----------------------------
Esta aplicación se desarrolló con asistencia de IA para implementar y revisar
código, pruebas, documentación y publicación. BITACORA.md registra el trabajo
técnico; no sustituye la conversación compartida.
Enlace público real conservado del historial:
https://chatgpt.com/s/cx_6ac32e27e5188191ae8322c88acd137a
Se abrió el contenido compartido, titulado "Crear índices de concentración".
Es una instantánea histórica real; no se afirma que incluya los últimos turnos
ni que esta bitácora sustituya ese contenido. ENLACES.txt reúne los tres enlaces.
La herramienta abrió el contenido en el navegador disponible. Una petición HTTP
anónima independiente recibió 403; no se afirma acceso anónimo comprobado a la
conversación ni que esa petición reproduzca el comportamiento del navegador.

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
