"""Evaluación didáctica del IHH, independiente de Streamlit y Plotly.

Referencia: FNE, Guía para el Análisis de Operaciones de Concentración
Horizontales, mayo de 2022, sección III.B, pp. 15–16, párrafos 32–36.
La guía combina IHH, ΔIHH y otros antecedentes. Esta herramienta solo adopta
una clasificación didáctica del nivel de IHH: <1500, [1500,2500), >=2500.
Convención explícita: 1500 es moderada y 2500 es alta. No se redondea antes
de comparar fronteras. El percentil de Monte Carlo no modifica la categoría.
"""

import math
from decimal import Decimal, InvalidOperation
from numbers import Real
from typing import Any, Dict, Iterable

import numpy as np
from numpy.typing import ArrayLike

from . import indices
from .simulacion import percentil_empirico


FUENTE_FNE = (
    "https://www.fne.gob.cl/wp-content/uploads/2022/05/"
    "20220531.-Guia-para-el-Analisis-de-Operaciones-de-Concentracion-"
    "Horizontales-version-final-en-castellano.pdf"
)
OPCIONES = ("Baja", "Moderada", "Alta")
INTERVALOS = {
    "Baja": "IHH < 1500 puntos",
    "Moderada": "1500 ≤ IHH < 2500 puntos",
    "Alta": "IHH ≥ 2500 puntos",
}
PREGUNTA_IHH = (
    "Según el criterio didáctico y evaluando expresamente su IHH en puntos, "
    "¿la concentración del caso es baja, moderada o alta?"
)
CONVENCION_FRONTERAS = "En las fronteras, IHH=1500 es moderada e IHH=2500 es alta."
ALCANCE_DIDACTICO = (
    "Esta clasificación es didáctica y no determina automáticamente una "
    "conducta anticompetitiva ni sustituye el análisis de una operación por la FNE."
)


def clasificar_ihh(ihh_puntos: float) -> str:
    """Clasifica un IHH en puntos, sin redondeo ni tolerancia en las fronteras.

    Args:
        ihh_puntos: Número real finito en [0, 10000], en puntos de IHH.

    Returns:
        'Baja' si IHH<1500; 'Moderada' si 1500<=IHH<2500; 'Alta' si IHH>=2500.

    Raises:
        TypeError: Por valores no reales, incluidos booleanos.
        ValueError: Por valores no finitos o fuera de [0, 10000].
    """
    if isinstance(ihh_puntos, bool) or not isinstance(ihh_puntos, Real):
        raise TypeError("El IHH debe ser un número real expresado en puntos.")
    if not 0 <= ihh_puntos <= 10000 or not math.isfinite(ihh_puntos):
        raise ValueError("El IHH debe ser finito y estar entre 0 y 10000 puntos.")
    if ihh_puntos < 1500:
        return "Baja"
    if ihh_puntos < 2500:
        return "Moderada"
    return "Alta"


def evaluar_ihh(
    cuotas: Iterable[float], respuesta: str, muestra_ihh: ArrayLike,
    *, unidad_muestra: str = "proporcion",
) -> Dict[str, Any]:
    """Comprueba una respuesta y calcula el percentil real del IHH del caso.

    Args:
        cuotas: Proporciones aceptadas por indices.validar_cuotas; no porcentajes.
        respuesta: Una de las OPCIONES, con la misma escritura.
        muestra_ihh: Vector no vacío de IHH, en las unidades indicadas. Finito en
            [0,1] para proporciones o [0,10000] para puntos. El llamador debe
            garantizar que procede de la muestra vigente
            con el mismo N; este módulo no almacena ni conoce estado de interfaz.
        unidad_muestra: 'proporcion' conserva la API anterior; 'puntos' para el
            motor compacto. Se compara en las mismas unidades sin copiar ni
            transformar todo el array ni multiplicar puntos de nuevo.

    Returns:
        Diccionario de retroalimentación con acierto, respuesta, clasificación,
        IHH en puntos, intervalo, percentil de IHH, número de simulaciones con
        IHH menor o igual, total, cuotas porcentuales y aportes de cada empresa
        al IHH en puntos. No conserva la muestra ni regenera mercados.
        El percentil compara caso y muestra en las unidades declaradas, sin redondeo:
        percentil_empirico = 100*fracción(muestra_ihh <= IHH del caso).

    Raises:
        TypeError: Por respuesta no textual o cuotas/muestra no numéricas reales.
        ValueError: Por cuotas inválidas, respuesta ausente/no reconocida o
            muestras vacías, no finitas, no unidimensionales o fuera de [0,1].
    """
    valores = indices.validar_cuotas(cuotas)
    if unidad_muestra not in ("proporcion", "puntos"):
        raise ValueError("unidad_muestra debe ser proporcion o puntos.")
    if not isinstance(respuesta, str):
        raise TypeError("Selecciona una respuesta textual: Baja, Moderada o Alta.")
    if respuesta not in OPCIONES:
        raise ValueError("La respuesta debe ser Baja, Moderada o Alta.")
    ihh_proporcional = indices.ihh(valores)
    puntos = indices.ihh_puntos(valores)
    # Esta función valida tipos, finitud, dimensión y empates con la API vigente.
    valor_comparacion = puntos if unidad_muestra == "puntos" else ihh_proporcional
    limite = 10000 if unidad_muestra == "puntos" else 1
    percentil = percentil_empirico(muestra_ihh, valor_comparacion)
    muestras = np.asarray(muestra_ihh)
    if np.any(muestras < 0) or np.any(muestras > limite):
        raise ValueError(f"La muestra debe contener IHH en {unidad_muestra} entre 0 y {limite}.")
    menores_o_iguales = int(np.count_nonzero(muestras <= valor_comparacion))
    clasificacion = clasificar_ihh(puntos)
    porcentajes = tuple(s * 100 for s in valores)
    aportes = tuple(10000 * s ** 2 for s in valores)
    terminos = " + ".join(f"({s * 100:.10g} %)²" for s in valores)
    return {
        "acierto": respuesta == clasificacion,
        "respuesta": respuesta,
        "clasificacion": clasificacion,
        "ihh_puntos": puntos,
        "intervalo": INTERVALOS[clasificacion],
        "percentil_ihh": percentil,
        "menores_o_iguales": menores_o_iguales,
        "total_simulaciones": int(muestras.size),
        "cuotas_porcentaje": porcentajes,
        "aportes_ihh": aportes,
        "justificacion": (
            f"IHH en puntos = suma de los cuadrados de las cuotas porcentuales: {terminos}. "
            "Las cuotas mayores aportan más porque se elevan al cuadrado. "
            "Los cálculos usan las proporciones originales, sin redondear ni normalizar."
        ),
        "explicacion_percentil": (
            f"{menores_o_iguales} de {muestras.size} mercados simulados "
            f"({percentil:.6g} %) tienen un IHH menor o igual al del caso; se incluyen los empates."
        ),
        "alcance": ALCANCE_DIDACTICO,
    }


PREGUNTAS_COMPLEMENTARIAS = {
    "CRk": {
        "pregunta": "Si k=N, ¿qué representa CRk?",
        "opciones": ("El 100 % de las ventas, para cualquier reparto", "La cuota de la mayor empresa", "Un umbral regulatorio"),
        "correcta": "El 100 % de las ventas, para cualquier reparto",
        "justificacion": "CRk suma las k mayores cuotas. Si k=N suma todas: matemáticamente 100 %. En ese caso no distingue concentración; los valores float64 originales se conservan.",
    },
    "ID": {
        "pregunta": "¿Qué resume el índice de dominancia de García Alba?",
        "opciones": ("La concentración de los aportes de las empresas al IHH", "La entropía normalizada", "Un límite regulatorio universal"),
        "correcta": "La concentración de los aportes de las empresas al IHH",
        "justificacion": "Cada aporte relativo es s_i²/suma(s_j²); ID suma sus cuadrados. Un ID mayor refleja aportes al IHH más concentrados en pocas empresas. Aquí no se asignan umbrales regulatorios.",
    },
    "IE": {
        "pregunta": "Con N fijo, ¿qué significa una entropía de Shannon mayor?",
        "opciones": ("Cuotas más repartidas entre las empresas", "Mayor concentración en una sola empresa", "Una conducta anticompetitiva demostrada"),
        "correcta": "Cuotas más repartidas entre las empresas",
        "justificacion": "La entropía es máxima con cuotas iguales y mínima en un monopolio. Un percentil alto de IE significa mayor reparto respecto de la muestra; no es un umbral regulatorio.",
    },
}


def evaluar_complementaria(indicador: str, respuesta: str) -> Dict[str, Any]:
    """Comprueba una pregunta interpretativa sin umbrales; ValueError por opción inválida."""
    if indicador not in PREGUNTAS_COMPLEMENTARIAS:
        raise ValueError("La pregunta debe ser CRk, ID o IE.")
    pregunta = PREGUNTAS_COMPLEMENTARIAS[indicador]
    if respuesta not in pregunta["opciones"]:
        raise ValueError("Selecciona una de las opciones de la pregunta.")
    return {"acierto": respuesta == pregunta["correcta"],
            "correcta": pregunta["correcta"], "justificacion": pregunta["justificacion"]}


PREGUNTA_CRK_NUMERICA = (
    "¿Qué porcentaje de ventas concentran las k empresas mayores del caso particular?"
)
TOLERANCIA_CRK_PUNTOS_PORCENTUALES = 0.01


def evaluar_crk_numerico(cuotas, k, respuesta: str) -> Dict[str, Any]:
    """N proporciones, k [1,N] y respuesta textual en % -> dict de feedback.

    Acepta coma o punto decimal. Valida respuesta finita en [0,100] y cuotas
    con indices.py. Tolerancia inclusiva de 0,01 puntos porcentuales respecto
    de 100*CRk SIN redondearlo. Decimal interpreta la respuesta y el límite
    textual explícito para que 70,01 no falle por representación binaria.
    No altera las cuotas ni los indicadores float64. Devuelve acierto (bool),
    porcentaje_correcto/respuesta (float), cuotas_mayores_porcentaje (tuple),
    suma_proporciones, tolerancia_pp y justificacion (str). No conoce estado
    de UI; el llamador debe bloquear casos/muestras incompatibles.
    TypeError por respuesta no textual o tipos inválidos; ValueError por
    cuotas/k inválidos, respuesta vacía/no numérica/no finita/fuera de [0,100].
    """
    valores = indices.validar_cuotas(cuotas)
    suma = indices.crk(valores, k)
    if not isinstance(respuesta, str):
        raise TypeError("Introduce la respuesta como texto decimal.")
    texto = respuesta.strip().replace(",", ".")
    try:
        numero = Decimal(texto)
    except InvalidOperation as error:
        raise ValueError("Introduce un porcentaje con coma o punto decimal.") from error
    if not numero.is_finite() or not Decimal(0) <= numero <= Decimal(100):
        raise ValueError("La respuesta debe ser finita y estar entre 0 y 100 %.")
    correcto = suma * 100
    mayores = tuple(s * 100 for s in sorted(valores, reverse=True)[:k])
    tolerancia = Decimal(str(TOLERANCIA_CRK_PUNTOS_PORCENTUALES))
    centro = Decimal(str(correcto))
    # Comparar límites conserva todos los dígitos de respuestas textuales largas;
    # restar la respuesta con el contexto Decimal podría redondear su diferencia.
    acierto = centro - tolerancia <= numero <= centro + tolerancia
    terminos = " + ".join(f"{valor:.12g} %" for valor in mayores)
    return {
        "acierto": acierto, "respuesta": float(numero),
        "porcentaje_correcto": correcto, "cuotas_mayores_porcentaje": mayores,
        "suma_proporciones": suma,
        "tolerancia_pp": TOLERANCIA_CRK_PUNTOS_PORCENTUALES,
        "justificacion": f"Las {k} cuotas mayores suman {terminos} = {correcto:.12g} %.",
    }


def intervalo_ihh(ihh_puntos) -> str:
    """IHH real en puntos [0,10000], o categoría Baja/Moderada/Alta -> str intervalo.

    Adopta 1500 moderada y 2500 alta. TypeError/ValueError por argumento inválido.
    """
    if isinstance(ihh_puntos, str):
        if ihh_puntos not in INTERVALOS:
            raise ValueError("Categoría no reconocida.")
        return INTERVALOS[ihh_puntos]
    return INTERVALOS[clasificar_ihh(ihh_puntos)]


def huella_cuotas(cuotas, n=None):
    """Cuotas en proporciones y N opcional exacto -> tuple[float,...] comparable.

    Valida sin redondeo ni normalización. Una tupla evita igualdad ambigua de
    arrays en session_state; no es un hash criptográfico. TypeError/ValueError
    por entradas inválidas. Los cambios originales de cuota cambian la huella.
    """
    return indices.validar_cuotas(cuotas, n)


def evaluar_respuesta_ihh(cuotas, respuesta, muestra_ihh, *, unidad_muestra=None, n=None):
    """Adaptador de evaluar_ihh: cuotas proporcionales, respuesta y muestra -> dict.

    n opcional exige cantidad exacta. muestra_ihh puede ser vector (proporciones
    por defecto), ResultadoSimulacion completo o compacto/dict local; en resultados
    se infieren las unidades y solo se usa IHH. unidad_muestra explícita permite
    'proporcion' o 'puntos' para un vector. Devuelve el feedback documentado en
    evaluar_ihh, con IHH en puntos y percentil inclusivo; propaga sus errores.
    """
    from .simulacion import ResultadoSimulacionCompacto

    cuotas = indices.validar_cuotas(cuotas, n)
    if isinstance(muestra_ihh, ResultadoSimulacionCompacto):
        muestra, unidad = muestra_ihh.ihh_puntos, "puntos"
    elif isinstance(muestra_ihh, dict):
        if "ihh_puntos" in muestra_ihh:
            muestra, unidad = muestra_ihh["ihh_puntos"], "puntos"
        else:
            muestra = muestra_ihh["ihh"]
            unidad = "puntos" if muestra_ihh["configuracion"].get("unidades", {}).get("ihh") == "puntos" else "proporcion"
    else:
        muestra, unidad = muestra_ihh, unidad_muestra or "proporcion"
    if isinstance(muestra_ihh, (dict, ResultadoSimulacionCompacto)):
        if muestra_ihh["configuracion"]["n"] != len(cuotas):
            raise ValueError("La muestra de IHH tiene otro N.")
        if unidad_muestra is not None and unidad_muestra != unidad:
            raise ValueError("La unidad declarada no coincide con el resultado.")
    return evaluar_ihh(cuotas, respuesta, muestra, unidad_muestra=unidad)
