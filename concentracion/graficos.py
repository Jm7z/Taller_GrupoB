"""Gráficos Plotly sin estado de Streamlit ni llamadas al motor de simulación."""

from typing import Optional

import numpy as np
import plotly.graph_objects as go

from .indices import validar_cuotas


AZUL = "#2563A6"
PETROLEO = "#087F83"
INDICADORES = {
    "crk": ("CRk", "% de ventas", 100.0),
    "ihh": ("IHH", "puntos (0–10000)", 10000.0),
    "id": ("ID de García Alba", "adimensional", 1.0),
    "ie": ("Entropía de Shannon", "nats", 1.0),
}


def _estilo(figura: go.Figure, titulo: str, eje_x: str, eje_y: str) -> go.Figure:
    figura.update_layout(
        template="plotly_white", title=dict(text=titulo, font=dict(size=19)),
        xaxis_title=eje_x, yaxis_title=eje_y,
        font=dict(family="Arial, sans-serif", size=13, color="#18364B"),
        paper_bgcolor="white", plot_bgcolor="white", height=400,
        margin=dict(l=55, r=20, t=65, b=105),
        legend=dict(title="Series", orientation="h", y=-0.28, x=0),
        showlegend=True, hovermode="closest", autosize=True,
    )
    figura.update_xaxes(gridcolor="#EDF2F6", automargin=True)
    figura.update_yaxes(gridcolor="#EDF2F6", automargin=True)
    return figura


def grafico_cuotas(cuotas) -> go.Figure:
    """Cuotas en proporciones validadas por indices.py; eje vertical en %.

    No modifica ni redondea los datos. Propaga TypeError/ValueError si no son
    cuotas válidas. Devuelve una figura con título, leyenda y unidades.
    """
    valores = np.asarray(validar_cuotas(cuotas), dtype=np.float64) * 100
    figura = go.Figure(go.Bar(
        x=np.arange(1, len(valores) + 1), y=valores,
        name="Caso particular", marker_color=PETROLEO,
        hovertemplate="Empresa %{x}<br>Cuota: %{y:.6g} %<extra>Caso particular</extra>",
    ))
    figura.update_yaxes(range=[0, max(5.0, float(valores.max()) * 1.12)])
    figura.update_xaxes(dtick=1 if len(valores) <= 15 else None)
    return _estilo(figura, "Reparto de ventas del caso", "Empresa (número)", "Cuota de ventas (%)")


def histograma_indicador(
    muestras, indicador: str, caso: Optional[float] = None,
    percentil: Optional[float] = None, k: Optional[int] = None,
    *, ihh_en_puntos: bool = False,
) -> go.Figure:
    """Histograma agregado y línea del caso, incluyendo casos fuera de rango.

    Args:
        muestras: Vector finito no vacío en las unidades originales del motor.
        indicador: crk, ihh, id o ie. CRk se presenta en %, IHH en puntos.
        caso: Valor opcional en las mismas unidades originales que las muestras.
        percentil: Percentil empírico ya calculado, en [0, 100], para la leyenda
            y la etiqueta visible. No se calcula ni modifica aquí.
        k: Número de empresas opcional para el título CRk.
        ihh_en_puntos: True para la muestra compacta: muestra/caso de IHH ya
            están en puntos. False conserva el contrato proporcional anterior.

    Returns:
        Figura Plotly. Se envían al navegador hasta 45 barras de frecuencias,
        no todas las muestras. Para distribuciones constantes, o con variación
        de pocas ulps, se usa una barra. Esto solo afecta a la representación;
        no altera los datos ni el percentil. layout.meta informa constante y
        fuera_de_rango; este último usa comparaciones estrictas de los valores.
        Si hay caso y percentil válidos, añade una etiqueta de dos líneas con
        valor, unidad y percentil, sin cambiar trazas ni datos. Solo redondea
        el texto: valor con el formato vigente y percentil hasta tres decimales.

    Raises:
        ValueError: Por indicador, dimensiones, valores o percentil inválidos.
    """
    if indicador not in INDICADORES:
        raise ValueError("El indicador debe ser crk, ihh, id o ie.")
    valores = np.asarray(muestras, dtype=np.float64)
    if valores.ndim != 1 or valores.size == 0 or not np.all(np.isfinite(valores)):
        raise ValueError("Las muestras deben ser un vector finito no vacío.")
    if caso is not None and not np.isfinite(caso):
        raise ValueError("El caso debe ser finito.")
    if percentil is not None and (not np.isfinite(percentil) or not 0 <= percentil <= 100):
        raise ValueError("El percentil debe estar en [0, 100].")

    nombre, unidad, factor = INDICADORES[indicador]
    if indicador == "ihh" and ihh_en_puntos:
        factor = 1.0
    nombre = f"CR{k}" if indicador == "crk" and k is not None else nombre
    mostrados = valores * factor
    minimo, maximo = float(mostrados.min()), float(mostrados.max())
    constante = maximo - minimo <= 64 * np.finfo(np.float64).eps * max(1.0, abs(maximo))
    if constante:
        centro = (minimo + maximo) / 2
        ancho = max(1.0, abs(centro)) * 0.02
        conteos, bordes = np.histogram(mostrados, bins=1, range=(centro - ancho / 2, centro + ancho / 2))
    else:
        conteos, bordes = np.histogram(mostrados, bins=min(45, max(5, int(np.sqrt(valores.size)))))
    centros = (bordes[:-1] + bordes[1:]) / 2
    figura = go.Figure(go.Bar(
        x=centros, y=conteos, width=np.diff(bordes) * 0.96,
        marker_color=AZUL, name="Mercados simulados",
        customdata=np.column_stack((bordes[:-1], bordes[1:])),
        hovertemplate="Intervalo: %{customdata[0]:.6g}–%{customdata[1]:.6g}<br>Mercados: %{y}<extra>Simulación</extra>",
    ))
    limite_izquierdo, limite_derecho = float(bordes[0]), float(bordes[-1])
    fuera = False
    if caso is not None:
        caso_mostrado = float(caso) * factor
        fuera = bool(caso < valores.min() or caso > valores.max())
        etiqueta = f"Caso: {caso_mostrado:.6g}"
        if percentil is not None:
            etiqueta += f" · percentil {percentil:.2f}"
        figura.add_trace(go.Scatter(
            x=[caso_mostrado, caso_mostrado], y=[0, int(conteos.max()) * 1.12],
            mode="lines", line=dict(color=PETROLEO, width=4, dash="dash"),
            name=etiqueta,
            hovertemplate=f"Caso: {caso_mostrado:.8g} {unidad}<extra>{etiqueta}</extra>",
        ))
        limite_izquierdo = min(limite_izquierdo, caso_mostrado)
        limite_derecho = max(limite_derecho, caso_mostrado)
    margen = max(limite_derecho - limite_izquierdo, 1e-12) * 0.07
    figura.update_xaxes(range=[limite_izquierdo - margen, limite_derecho + margen])
    figura.update_yaxes(rangemode="tozero", tickformat=",d")
    figura.update_layout(meta={"constante": bool(constante), "fuera_de_rango": fuera}, bargap=0.04)
    if caso is not None and percentil is not None:
        # La conversión y precisión de presentación ya existen; la localización
        # afecta exclusivamente al texto, nunca a las muestras o al percentil.
        texto_valor = formatear_valor_indicador(indicador, float(caso), ihh_en_puntos=ihh_en_puntos)
        numero, _, unidad_etiqueta = texto_valor.partition(" ")
        entero, _, decimales = numero.partition(".")
        numero_es = f"{int(entero):,}".replace(",", ".")
        decimales = decimales.rstrip("0")
        if decimales:
            numero_es += "," + decimales
        percentil_es = f"{percentil:.3f}".rstrip("0").rstrip(".").replace(".", ",")

        # Referencia al área del gráfico: la caja permanece dentro del eje
        # también cuando este se amplía para un caso fuera de la muestra.
        # Tres posiciones mantienen la caja sobre la línea o a su lado, sin
        # depender de un ancho fijo de escritorio. Dos líneas caben en móvil.
        posicion = (caso_mostrado - (limite_izquierdo - margen)) / (
            limite_derecho - limite_izquierdo + 2 * margen
        )
        if posicion < 1 / 3:
            x, ancla, alineacion = min(posicion, 0.2), "left", "left"
        elif posicion > 2 / 3:
            x, ancla, alineacion = max(posicion, 0.8), "right", "right"
        else:
            x, ancla, alineacion = min(0.6, max(0.4, posicion)), "center", "center"
        figura.add_annotation(
            x=x, xref="paper", xanchor=ancla,
            y=0.98, yref="paper", yanchor="top", showarrow=False,
            text=f"Caso: {numero_es} {unidad_etiqueta}<br>Percentil: {percentil_es} %",
            align=alineacion, font=dict(size=11, color=PETROLEO),
            bgcolor="white", bordercolor=PETROLEO, borderwidth=1, borderpad=4,
        )
        # Espacio separado de título/leyenda, y de la punta de la línea.
        figura.update_yaxes(range=[0, int(conteos.max()) * 1.4])
    titulo_corto = nombre if indicador == "crk" else indicador.upper()
    return _estilo(figura, f"Distribución de {titulo_corto}", f"{nombre} ({unidad})", "Frecuencia (mercados)")


def _clave_indicador(indicador):
    if not isinstance(indicador, str) or indicador.lower() not in INDICADORES:
        raise ValueError("El indicador debe ser CRk, IHH, ID o IE (sin distinguir mayúsculas).")
    return indicador.lower()


def convertir_valor_presentacion(indicador, valor, *, ihh_en_puntos=False) -> float:
    """Indicador y valor escalar interno -> float en unidades de presentación.

    CRk proporcional -> %; IHH proporcional -> puntos (×10000 una sola vez).
    ihh_en_puntos=True mantiene puntos; ID/IE mantienen adimensional/nats.
    TypeError por valor no real/bool; ValueError por indicador o no finitud.
    """
    from numbers import Real

    clave = _clave_indicador(indicador)
    if isinstance(valor, (bool, np.bool_)) or not isinstance(valor, Real):
        raise TypeError("valor debe ser real, sin booleanos.")
    try:
        convertido = float(valor) * (1.0 if clave == "ihh" and ihh_en_puntos else INDICADORES[clave][2])
    except OverflowError as error:
        raise ValueError("valor debe ser finito.") from error
    if not np.isfinite(convertido):
        raise ValueError("valor debe ser finito.")
    return convertido


def obtener_valores_simulados(resultado, indicador):
    """Resultado completo/compacto/dict local -> array float64 (M,) para mostrar.

    CRk en %, IHH en puntos, ID adimensional, IE en nats. Lee explícitamente
    las unidades del resultado: el compacto NO se vuelve a multiplicar por
    10000. Puede devolver la propia serie cuando no cambia unidades; no se
    modifica. TypeError por tipo no admitido; ValueError por indicador.
    """
    from .simulacion import ResultadoSimulacionCompacto

    clave = _clave_indicador(indicador)
    if isinstance(resultado, ResultadoSimulacionCompacto):
        if clave == "ihh":
            return resultado.ihh_puntos
        valores = resultado[clave]
    elif isinstance(resultado, dict):
        if clave == "ihh" and "ihh_puntos" in resultado:
            return np.asarray(resultado["ihh_puntos"], dtype=np.float64)
        valores = np.asarray(resultado[clave], dtype=np.float64)
        if clave == "ihh" and resultado.get("configuracion", {}).get("unidades", {}).get("ihh") == "puntos":
            return valores
    else:
        raise TypeError("Se requiere un resultado completo, compacto o dict local.")
    return valores * INDICADORES[clave][2] if clave in ("crk", "ihh") else valores


def nombre_eje_indicador(indicador, k=None) -> str:
    """Nombre CRk/IHH/ID/IE y k opcional -> str con nombre y unidad del eje."""
    clave = _clave_indicador(indicador)
    nombre, unidad, _ = INDICADORES[clave]
    if clave == "crk" and k is not None:
        nombre = f"CR{k}"
    return f"{nombre} ({unidad})"


def formatear_numero_indicador(indicador, valor, *, ihh_en_puntos=False) -> str:
    """Indicador y escalar interno -> str sin sufijo; 2 decimales CRk/IHH, 6 ID/IE.

    Convierte unidades con convertir_valor_presentacion. Solo redondea el texto;
    propaga sus TypeError/ValueError. No usar este texto para calcular o evaluar.
    """
    clave = _clave_indicador(indicador)
    numero = convertir_valor_presentacion(clave, valor, ihh_en_puntos=ihh_en_puntos)
    return f"{numero:.2f}" if clave in ("crk", "ihh") else f"{numero:.6f}"


def formatear_valor_indicador(indicador, valor, *, ihh_en_puntos=False) -> str:
    """Indicador y escalar interno -> str de número y unidad, sin cambiar cálculos."""
    clave = _clave_indicador(indicador)
    numero = formatear_numero_indicador(clave, valor, ihh_en_puntos=ihh_en_puntos)
    unidad = {"crk": "%", "ihh": "puntos", "id": "adimensional", "ie": "nats"}[clave]
    return f"{numero} {unidad}"


def crear_grafico_cuotas(cuotas, n=None) -> go.Figure:
    """N proporciones válidas (N opcional exacto) -> Figure Plotly con eje en %.

    Adaptador de grafico_cuotas; propaga TypeError/ValueError de validación.
    """
    return grafico_cuotas(validar_cuotas(cuotas, n))


def crear_histograma_comparativo(
    muestras, indicador, caso=None, percentil=None, k=None, *, ihh_en_puntos=False,
) -> go.Figure:
    """Vector interno o resultado completo/compacto -> histograma Plotly.

    indicador acepta CRk/IHH/ID/IE. caso escalar está en proporciones para CRk
    e IHH, adimensional para ID y nats para IE; ihh_en_puntos=True declara un
    caso de IHH ya en puntos. Para vector, esa misma bandera declara también
    sus unidades. Para resultado, las unidades de sus series se leen de él.
    percentil opcional [0,100]; si falta y hay caso se calcula incluyendo empates.
    k opcional se infiere de la configuración del resultado. Devuelve Figure
    con línea visible, leyenda, unidades y soporte para constantes/fuera de rango.
    Propaga errores de validación de histograma_indicador/percentil_empirico.
    """
    from .simulacion import ResultadoSimulacionCompacto, percentil_empirico

    clave = _clave_indicador(indicador)
    es_resultado = isinstance(muestras, (dict, ResultadoSimulacionCompacto))
    if es_resultado:
        valores = obtener_valores_simulados(muestras, clave)
        if k is None:
            k = muestras["configuracion"]["k"]
        caso_presentado = None if caso is None else convertir_valor_presentacion(
            clave, caso, ihh_en_puntos=ihh_en_puntos,
        )
        # El núcleo convierte CRk proporcional a %; devolverle proporciones.
        if clave == "crk":
            valores = muestras["crk"]
            caso_presentado = caso
        puntos = clave == "ihh"
    else:
        valores, caso_presentado, puntos = muestras, caso, ihh_en_puntos
    if percentil is None and caso_presentado is not None:
        percentil = percentil_empirico(valores, caso_presentado)
    return histograma_indicador(valores, clave, caso_presentado, percentil, k,
                               ihh_en_puntos=puntos)
