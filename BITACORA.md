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

Se comprobó que el repositorio solicitado es público y usa main. La cuenta
completó personalmente los pasos de acceso. La publicación de las fuentes,
el despliegue, logs y verificaciones remotas se registrarán en COMPROBACIONES
con sus resultados efectivos, sin dar por completada ninguna acción intentada.

Esta bitácora pública incluye únicamente información técnica del proyecto.
No reproduce conversaciones, enlaces de conversación ni registros internos.
