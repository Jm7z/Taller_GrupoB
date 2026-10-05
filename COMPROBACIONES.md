# Comprobaciones de Taller_GrupoB

Fecha: 5 de octubre de 2026, America/Santiago (UTC−3). Se distinguen pruebas
automatizadas, observaciones del navegador y comprobaciones reportadas por el
usuario. No se envió correo. Capturas, logs y CSV de pruebas quedan fuera del ZIP.

- Repositorio público: https://github.com/Jm7z/Taller_GrupoB
- Aplicación: https://taller-grupob.streamlit.app/
- Rama y entrada: main, app.py.
- Commit que publicó el código probado: 0868937507fa00a2c7effe9dc4dabbc86514d4a6.
  El cierre es documental; Cloud no expone el SHA exacto del checkout en sus logs.
  Ese dato no se presenta como observado en el servidor.

| Requisito | Evidencia real | Pendiente o límite |
| --- | --- | --- |
| Fuentes y estructura | 26 archivos: scripts de raíz, paquete concentracion, configuración, ocho archivos de pruebas y documentación. Imports revisados; no necesita imágenes ni datos externos. Adaptadores de raíz y medir_rendimiento.py usados por pruebas. | Entornos y evidencia generada fuera de entrega. |
| Código y APIs | Código conservado; no se modifican fórmulas, generador, secuencia, unidades, límites, lotes, CSV ni evaluación durante publicación. Cotejado con entrega anterior y archivos GitHub. | APIs recuperadas probadas con llamadas y atributos; no se afirma reconstruir contratos históricos desconocidos. |
| Dependencias | Pins intactos: numpy 2.3.5, pandas 3.0.1, plotly 6.9.0, streamlit 1.65.0, pyarrow 21.0.0. Cloud Linux instaló requirements.txt con uv, registrado a las 17:26:19 UTC y tras reinicio. | Dependencias transitivas no fijadas. No se cambia pin sin incompatibilidad demostrada. |
| Configuración | TOML válida; tema claro/headless, sin port/address/certificados locales. Streamlit local reconoce ajustes; Cloud presenta tema esperado. | Cloud puede sobrescribir gatherUsageStats; no se afirma controlar su telemetría. |
| Exclusiones Git | .gitignore para entornos, cachés, temporales, ZIP, logs, resultados y secretos. git check-ignore comprobó 11 rutas excluidas y seis necesarias no ignoradas. | No publicar secretos, CSV/logs de prueba ni enlaces privados de conversación. |
| GitHub | Repo public, main, permiso de publicación. Los 26 archivos del commit de código recuperados y cotejados byte a byte y por SHA de blob. | No equivale a observar el SHA del proceso Cloud. |
| Despliegue | URL real taller-grupob.streamlit.app. Advanced settings/General: Python 3.12. Logs: Using Python 3.12.15 environment at /home/adminuser/venv. Arranque 2026-10-05 17:26:22.943 Uvicorn server started on :::8501. | Python local 3.12.14. Suite no ejecutada dentro de Linux Cloud. |
| Visibilidad y acceso | Settings > Sharing: This app is public and searchable. Tras reinicio, usuario confirmó que URL carga y simula sin iniciar sesión en ventana privada Windows. | Prueba privada realizada/reportada por usuario; herramientas usan sesión administrativa. No se inspeccionaron cookies de su ventana. |
| Incidente callback | Usuario mostró unexpected keyword argument callback_progreso. Firma local/publicada admite parámetro; llamadas reales pasan. Reinicio: desconexión 17:35:15 UTC, nuevo arranque 17:35:59.355 UTC. Sesión nueva simula correctamente; usuario confirma recuperación tras recargar. | Causa exacta del proceso fallido no demostrada. No se atribuye a caché concreta ni se modifica motor para ocultarlo. |
| Caso remoto de referencia | N=4,k=2,M=1000,semilla=42,40–30–20–10: CR2=70 %, IHH interno=3000.0000000000005 puntos, ID≈0.393333, IE≈1.279854 nats. Percentiles observados CRk=23.4 %, IHH=17.1 %, ID=20.5 %, IE=82.3 %. IHH: 171/1000 menores o iguales. | No se fuerzan datos. IHH convertido a puntos una sola vez. Percentil depende de muestra. |
| Gráficos | Cuatro selectores/histogramas probados; unidades, línea, leyenda y etiqueta. Cambio de indicador conserva tiempo de motor y muestra. Hover histograma IHH: intervalo 2938.57–3152.53, frecuencia 109. Hover real de línea: Caso:3000 puntos (0–10000), percentil17.10. | Revisión visual efectuada en navegador, sin modificar cálculos. |
| Evaluación | Alta correcta, Baja/Moderada incorrectas para ejemplo: selección, valor, intervalos, motivo y correcta. Visualizando IE, evaluación mantiene IHH 171/1000=17.1 %. CR2: 70,00 acepta; 60 rechaza y explica 40 %+30 %=70 %. | Seis combinaciones incorrectas y fronteras completas verificadas en código, no todas en navegador remoto. |
| Estado | Cambiar N/k/iteraciones deja muestra desactualizada y bloquea comparación/evaluación. Cambiar respuesta limpia error previo; caso nuevo limpia respuesta y feedback. Sin preselección. | Evidencia visible y AppTest; no inspección privada del estado frontend. |
| Entrada manual | Tabla web: 40→30 deja suma 90 %, falta 10 %, rechazo sin normalizar, radios bloqueados y cero etiquetas. Restaurar ejemplo revalida. | No se probaron todas combinaciones de pegado de celdas. |
| Aleatorio/iguales | Dos pulsaciones producen cuotas distintas, cierre100 %; conserva tiempo de motor0.082373 s y muestra vigente. Limpia respuestas. Cuotas iguales CR2: etiqueta percentil0 %. | Tiempo de motor no mide latencia total ni capacidad concurrente. |
| N/k extremos | N=2,k=2,M=1000 termina y se identifica constante a precisión numérica. Cambio k=1/M=5000 exige resimular. N=100,k=100,M=5000 termina. Ejemplo desde N100 establece N4/k4 y bloquea muestra incompatible. | Para k=N, float64 puede hacer percentil inclusivo inferior a100 %, aunque visualmente CRk sea100 %. No se alteran valores ni comparador <=. |
| Progreso | Cloud:1000/1000 y5000/5000, aria-valuenow100, tras resultado válido. Tests comprueban eventos por lotes, equivalencia con/sin callback y limpieza ante errores. | No se capturaron visualmente todos pasos intermedios ni se agotó físicamente memoria. |
| CSV | Descargas reales: muestra1000×11 y caso4×2; N4/k2/semilla42/NumPy2.3.5. Lectura round_trip: máximo error0.0 contra motor local en CRk%,IHHpuntos,ID,IE,IE/lnN. Cuotas exactas40/30/20/10, conteoIHH171. | Primer intento comparador usó atributo inexistente; corregido a atributos compactos públicos, ejecución efectiva código0. CSV de prueba excluidos. |
| Visual | Cuatro histogramas revisados en escritorio960×900 y viewport390×844. Etiquetas dentro, dos líneas; ejes/leyendas legibles. Tarjetas apiladas; DOM móvil clientWidth=scrollWidth=390. | Emulación, no teléfono físico. Barra activa Plotly puede cubrir parte del título en móvil; módulo gráfico conservado. |
| Suite desde fuentes preparadas |116 pruebas OK en17.685 s, Python Windows3.12.14; app/paquete importados de Taller_GrupoB. | Entorno existente; extracción final se verifica aparte. |
| Entorno independiente | Python3.12.14 nuevo; include-system-site-packages=false, usuario deshabilitado. Instalación offline wheels cacheadas código0; pip check sin conflictos; cinco imports desde su propio site-packages. | PyPI local bloqueado WinError10013; no incompatibilidad de pins. Cloud sí instaló por red en Linux. |
| Extracción independiente | ZIP candidato de26 archivos: CRC correcto, nombres únicos y bytes idénticos a fuentes. Extracción nueva; reinstalación real --force-reinstall offline desde su requirements.txt y pip check aprobado. Suite -I -B:116 pruebas OK en20.166 s; imports de fuentes dentro extracción y bibliotecas en entorno nuevo. | Cierre documental conserva exactamente código/configuración/pruebas de ese paquete; se repite la verificación del ZIP de cierre al entregarlo. Registro de este candidato no se presenta como su hash final. |
| Arranque extraído | Proceso Hidden desde la extracción: / y /_stcore/health HTTP200, health=ok. Navegador real abrió app, cargó ejemplo y simuló1000: CR2=70 %, IHH3000.00, etiqueta CRk23.4 %, muestra vigente, sin excepción. | Puerto de verificación8510; README usa8501. Windows mismo equipo, entorno independiente; no instalador Python ni ejecución en otro equipo. |
| Segunda extracción de cierre | Paquete26 nombres únicos/CRC/bytes correcto; extraido_cierre nuevo. Reinstalación desde requirements extraído/pip check aprobados; 116 pruebas -I -B en19.300 s, código0, imports aislados. Servidor en8511: raíz/salud HTTP200. | Ejecutables/configuración/pins/tests idénticos al candidato; actualización final solo documental. El resumen de entrega registra el commit definitivo, su ZIP y la comprobación adicional tras publicar. |

## Cobertura automatizada

| Archivo | Pruebas |
| --- | ---: |
| tests/test_indices.py | 10 |
| tests/test_simulacion.py | 16 |
| tests/test_compacto.py | 5 |
| tests/test_graficos.py | 12 |
| tests/test_evaluacion.py | 8 |
| tests/test_app.py | 34 |
| tests/test_compatibilidad.py | 18 |
| tests/test_progreso.py | 13 |
| Total | 116 |

Cierre atol=1e-10/rtol=0, escalar/vectorizado, reproducibilidad, resultado
completo/compacto, cuotas no guardadas en sesión, unidades, CSV, adaptadores,
pregunta numérica, seis selecciones erróneas IHH, fronteras1500/2500 y float64
adyacentes. Figuras: cuatro indicadores, constantes, extremos/fuera de rango,
empates, percentiles0/100 y etiqueta ausente con caso inválido.

## Límites de acceso y verificación

Medición histórica conservada, no repetida en esta publicación: Windows,
Python3.12.14/NumPy2.3.5, N=100,k=50,semilla42. Cinco tiempos después de
calentamiento; memoria medida aparte con tracemalloc, no RSS ni latencia web.
Sirvió para justificar máximo100000 y lotes4096. Archivo rendimiento.json
generado excluido; procedimiento opcional en README y medir_rendimiento.py.

| Motor | Iteraciones | Mediana(s) | Pico trazado(MiB) |
| --- | ---: | ---: | ---: |
| Compacto | 1000 | 0.001813 | 1.658 |
| Compacto | 10000 | 0.014942 | 6.952 |
| Compacto | 100000 | 0.141094 | 9.698 |
| Referencia experimental completa | 1000 | 0.001779 | 1.655 |
| Referencia experimental completa | 10000 | 0.015655 | 16.520 |
| Referencia experimental completa | 100000 | 0.175063 | 165.179 |

Sin prueba de carga concurrente ni garantía de disponibilidad permanente. Cloud
documenta recursos variables e hibernación tras12 horas sin tráfico; un visitante
puede necesitar despertar la app y esperar. Motor: máximo100000, lotes4096;
3.05 MiB al máximo son solo las cuatro series, no memoria total Streamlit/CSV.
Instrucciones y fuentes oficiales en README.txt. BITACORA registra trabajo
técnico; no sustituye el enlace compartido de una conversación.
