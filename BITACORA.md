# Bitácora técnica de Taller_GrupoB

Registro público de cambios y verificaciones del proyecto. Las comprobaciones
locales no acreditan funcionamiento en un despliegue remoto. Los detalles
vigentes y pendientes están en COMPROBACIONES.md.

## Funcionalidades de la versión de partida

- Cálculos en proporciones: CRk, IHH, dominancia de García Alba y Shannon.
  Validación sin normalización, cierre atol=1e-10 y rtol=0.
- Resultado completo disponible para la API; interfaz con cuatro series
  compactas, ejecución por lotes, semilla opcional y generador independiente
  para casos particulares. Progreso mediante callback opcional.
- CSV diferidos, tarjetas, cuatro histogramas, línea y etiqueta del caso con
  unidades y percentil que incluye empates.
- Evaluación didáctica del IHH sin redondear fronteras; preguntas conceptuales
  y numérica CRk. Bloqueos y limpieza por cambios de caso/configuración.
- Feedback IHH con selección, intervalo, valor, motivo de exclusión y categoría
  correcta; precisión suficiente junto a 1500/2500. Se prueban las seis
  selecciones incorrectas y los valores adyacentes a ambas fronteras.

## Preparación para publicación — 5 de octubre de 2026

Se preparó una carpeta limpia a partir de la entrega local vigente. Fuentes
idénticas a la entrega de partida; se conservaron módulos, pruebas y los cinco
pins de requirements.txt. No se modificaron fórmulas, unidades, generadores,
límites ni lotes. La API y la interfaz siguen usando sus contratos actuales.

Se amplió .gitignore para entornos, cachés, temporales, resultados generados,
ZIP y secretos. git check-ignore verificó 11 rutas excluidas y seis archivos
necesarios publicables. La configuración TOML conserva el tema y headless,
sin fijar address, port ni certificados locales. Streamlit local la reconoce.

Se añadió README.md para la portada de GitHub y se conservaron en README.txt
las instrucciones completas de Windows. Se documentaron autenticación oficial,
despliegue con Python 3.12, registros, acceso público, límites e hibernación.
Los enlaces y versiones remotos solo se registran cuando se comprueban.

Pruebas desde la carpeta preparada: 116 aprobadas en 17,685 s con Python
3.12.14 del entorno local existente. Se comprobaron las rutas de importación
de app y paquete. No fue una instalación nueva ni una ejecución en Cloud.

Se publicaron y cotejaron los 26 archivos en el repositorio público
https://github.com/Jm7z/Taller_GrupoB, rama main. Commit del código:
0868937507fa00a2c7effe9dc4dabbc86514d4a6. La aplicación recibió la URL real
https://taller-grupob.streamlit.app/. Python 3.12 se seleccionó explícitamente;
los logs confirmaron Python 3.12.15, los cinco pins y el arranque en Linux.
Sharing confirmó visibilidad pública. No se ejecutó la suite dentro de Cloud.

Un usuario reportó error del parámetro callback_progreso. La firma y los archivos
publicados se cotejaron; el motor vigente admitía el callback y sus llamadas
pasaban. Se reinició Cloud y comprobó una sesión nueva. El usuario confirmó
simulación correcta sin sesión en ventana privada tras recargar. La causa exacta
del proceso anterior no quedó demostrada; no se modificó el código ni los pins.

En Cloud se comprobaron los cuatro indicadores, N=2/N=100, cambios de k/M,
progreso final, ejemplo, edición manual inválida, aleatorio independiente,
CSV y feedback correcto/incorrecto. El ejemplo N4/k2/M1000/semilla42 produjo
CR2=70 %, IHH≈3000 puntos y percentil IHH=17.1 % (171/1000). Se revisaron
histogramas a 960×900 y 390×844; no se usó un teléfono físico. Límites y
pendientes, incluido el SHA no expuesto por los logs, en COMPROBACIONES.md.

Se verificó un paquete de26 archivos mediante CRC, lista sin duplicados y
cotejo de bytes. Desde una extracción nueva se reinstalaron los pins con
paquetes cacheados y pip check aprobó. Entorno independiente Python3.12.14:
116 pruebas aisladas aprobadas en20.166 s. Servidor extraído: HTTP200/healthok;
el navegador ejecutó ejemplo y simulación1000. El cierre documental conserva
las fuentes ejecutables y pruebas verificadas; el ZIP de cierre se vuelve a
comprobar antes de entregar. No se incluyen entornos, cachés ni evidencia generada.

Otra extracción nueva del paquete de cierre repitió la reinstalación de sus
requisitos y pip check, y aprobó 116 pruebas aisladas en19.300 s. Servidor
extraído: raíz y salud HTTP200. Solo documentación cambió respecto del candidato.
La entrega definitiva coteja nuevamente esos archivos con el repositorio y
excluye ZIP anteriores, entornos, cachés, temporales, secretos y carpetas Git.

Esta bitácora pública incluye únicamente información técnica del proyecto.
No reproduce conversaciones, enlaces de conversación ni registros internos.
