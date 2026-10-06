"""Interfaz Streamlit. Ejecutar: python -m streamlit run app.py.

La única llamada al motor compacto está protegida por el botón de simulación.
La sesión conserva una muestra; los cambios de configuración la invalidan
hasta una nueva simulación. La evaluación didáctica usa siempre el IHH.
"""

import math
from time import perf_counter
from numbers import Integral, Real

import numpy as np
import pandas as pd
import streamlit as st

from concentracion import indices
from concentracion.evaluacion import (
    ALCANCE_DIDACTICO, CONVENCION_FRONTERAS, FUENTE_FNE,
    INTERVALOS, OPCIONES, PREGUNTA_IHH, evaluar_ihh, clasificar_ihh,
    PREGUNTAS_COMPLEMENTARIAS, evaluar_complementaria,
    PREGUNTA_CRK_NUMERICA, evaluar_crk_numerico,
)
from concentracion.graficos import grafico_cuotas, histograma_indicador
from concentracion.simulacion import (
    ADVERTENCIA_RECURSOS, MAX_ITERACIONES,
    ResultadoSimulacionCompacto, generar_caso_aleatorio,
    compactar_resultado, percentil_empirico, simular_mercados_compactos,
)


AYUDAS_INDICADORES = {
    "CRk": "CRk muestra qué porcentaje del mercado reúnen las k empresas con mayores cuotas.",
    "IHH": "El IHH suma los cuadrados de las cuotas. Un valor mayor indica mayor concentración.",
    "ID": "El ID de García Alba mide qué tan concentrados están los aportes de las empresas al IHH.",
    "IE": ("La entropía mide qué tan repartidas están las cuotas. Para el mismo N, "
           "un valor mayor indica mayor diversidad y alcanza su máximo con cuotas iguales."),
}


ESTILO = """
<style>
.stMainBlockContainer { max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #174B73; letter-spacing: -0.02em; }
h1 { font-size: clamp(1.8rem, 4vw, 2.7rem) !important; }
[data-testid="stMetricValue"] { color: #087F83; font-size: clamp(1.4rem, 2vw, 1.85rem); }
@media (max-width: 650px) {
  .stMainBlockContainer { padding: 1rem .8rem 2rem; }
  [data-testid="stHorizontalBlock"] { flex-direction: column; gap: .6rem; }
  [data-testid="stColumn"] { width: 100% !important; flex: 1 1 100% !important; min-width: 0; }
  [data-testid="stMetricValue"] { font-size: 1.7rem; }
}
</style>
"""


def validar_porcentajes(porcentajes, n):
    """Valida N porcentajes reales en [0, 100] y convierte sin normalizar.

    Propaga TypeError por valores no reales y ValueError por cantidad, rango,
    finitud o suma inválidos. El cierre conserva la tolerancia de indices.py.
    """
    n = indices.validar_numero_empresas(n)
    valores = list(porcentajes)
    if len(valores) != n:
        raise ValueError(f"Introduce exactamente {n} cuotas.")
    for valor in valores:
        if isinstance(valor, (bool, np.bool_)) or not isinstance(valor, Real):
            raise TypeError("Completa cada cuota con un número real.")
        if not 0 <= valor <= 100 or not math.isfinite(valor):
            raise ValueError("Cada cuota debe ser finita y estar entre 0 y 100 %.")
    return indices.validar_cuotas((valor / 100 for valor in valores), n=n)


def _tabla(porcentajes):
    return pd.DataFrame({
        "Empresa": [f"Empresa {i + 1}" for i in range(len(porcentajes))],
        "Cuota (%)": np.asarray(porcentajes, dtype=np.float64),
    })


def _reemplazar_caso(porcentajes):
    anterior = f"editor_caso_{st.session_state.get('editor_revision', 0)}"
    st.session_state.pop(anterior, None)
    st.session_state.editor_revision = st.session_state.get("editor_revision", 0) + 1
    st.session_state.caso_base = _tabla(porcentajes)


def csv_muestra(muestra):
    """CSV diferido, sin redondeo: acepta API clásica o compacta, unidades explícitas."""
    config = muestra["configuracion"]
    n = config["n"]
    tabla = pd.DataFrame({
        "mercado": np.arange(1, config["iteraciones"] + 1),
        "n": n, "k": config["k"],
        "semilla": config["semilla"],
        "semilla_efectiva": str(config["entropia_semilla"]),
        "version_numpy": config["version_numpy"],
        "crk_porcentaje": muestra["crk"] * 100,
        "ihh_puntos": muestra.ihh_puntos if isinstance(muestra, ResultadoSimulacionCompacto) else muestra["ihh"] * 10000,
        "id": muestra["id"], "ie_nats": muestra["ie"],
        "ie_normalizada": muestra["ie"] / math.log(n),
    })
    return tabla.to_csv(index=False).encode("utf-8-sig")


def csv_caso(tabla):
    """Exporta empresa y cuota porcentual ORIGINAL, sin redondear ni normalizar.

    Propaga los errores de validación; se llama al pulsar la descarga, sobre
    una copia local capturada por el callback, sin leer session_state en otro hilo.
    """
    validar_porcentajes(tabla["Cuota (%)"].tolist(), len(tabla))
    return tabla[["Empresa", "Cuota (%)"]].to_csv(index=False).encode("utf-8-sig")


def _limpiar_resultado_evaluacion():
    """Callback previo al rerun al cambiar la respuesta."""
    st.session_state.resultado_evaluacion = None


def _limpiar_complementaria(indicador):
    st.session_state[f"feedback_{indicador}"] = None


def _limpiar_crk_numerico():
    st.session_state.feedback_crk_numerico = None


def _limpiar_respuestas():
    """Borra respuestas y feedback antes de construir sus widgets en el rerun."""
    st.session_state.resultado_evaluacion = None
    st.session_state.respuesta_evaluacion = None
    st.session_state.feedback_crk_numerico = None
    st.session_state.respuesta_crk_numerica = ""
    for indicador in PREGUNTAS_COMPLEMENTARIAS:
        st.session_state[f"feedback_{indicador}"] = None
        st.session_state[f"respuesta_{indicador}"] = None


def _cargar_ejemplo():
    """Callback previo al rerun: N=4, cuatro cuotas exactas y k válido.

    Conserva k entero [1,4]; valores mayores se limitan a 4 y ausentes a 2.
    No simula: conserva las cuatro series y marca incompatibilidad N/k.
    """
    anterior_k = st.session_state.get("k")
    k = min(4, max(1, int(anterior_k))) if isinstance(anterior_k, Integral) and not isinstance(anterior_k, bool) else 2
    st.session_state.n = 4
    st.session_state.k = k
    st.session_state.caso_n = 4
    _reemplazar_caso([40.0, 30.0, 20.0, 10.0])
    _limpiar_respuestas()
    st.session_state.contexto_evaluacion = None
    muestra = st.session_state.get("muestra")
    if muestra is not None:
        config = muestra["configuracion"]
        if config["n"] != 4 or config["k"] != k:
            st.session_state.muestra_desactualizada = True
    st.session_state.aviso_caso = "Ejemplo cargado: N=4 y cuotas 40–30–20–10."


def _bloquear_configuracion_incompleta(campo):
    """No convertir controles vacíos a int; invalida comparación y preguntas."""
    st.session_state.muestra_desactualizada = st.session_state.get("muestra") is not None
    _limpiar_respuestas()
    st.session_state.evaluacion_habilitada = False
    st.session_state.comparacion_habilitada = False
    st.info(f"Completa {campo} con valores válidos para continuar.")
    st.stop()


def _mostrar_complementarias(habilitada):
    with st.expander("Preguntas complementarias · interpretar CRk, ID e IE"):
        st.caption("Preguntas conceptuales sin umbrales regulatorios.")
        for indicador, pregunta in PREGUNTAS_COMPLEMENTARIAS.items():
            st.write(f"**{indicador}:** {pregunta['pregunta']}")
            respuesta = st.radio(
                f"Respuesta sobre {indicador}", pregunta["opciones"], index=None,
                key=f"respuesta_{indicador}", disabled=not habilitada,
                on_change=_limpiar_complementaria, args=(indicador,),
            )
            if st.button(f"Comprobar {indicador}", key=f"comprobar_{indicador}",
                         disabled=not habilitada or respuesta is None):
                st.session_state[f"feedback_{indicador}"] = evaluar_complementaria(indicador, respuesta)
            feedback = st.session_state.get(f"feedback_{indicador}")
            if feedback is not None:
                mensaje = "Acierto." if feedback["acierto"] else "Error en la respuesta."
                (st.success if feedback["acierto"] else st.error)(f"{mensaje} Respuesta correcta: {feedback['correcta']}.")
                st.write(feedback["justificacion"])


def _mostrar_crk_numerico(cuotas, k, habilitada):
    st.write(f"**CR{k} · pregunta numérica:** {PREGUNTA_CRK_NUMERICA}")
    st.caption(f"Para este caso, k={k}. Responde en %, con coma o punto decimal. Tolerancia: 0,01 puntos porcentuales, inclusive.")
    respuesta = st.text_input(
        "Porcentaje concentrado por las k empresas mayores", value="",
        key="respuesta_crk_numerica", disabled=not habilitada,
        on_change=_limpiar_crk_numerico,
    )
    if st.button("Comprobar porcentaje CRk", key="comprobar_crk_numerico",
                 disabled=not habilitada or not respuesta.strip()):
        try:
            st.session_state.feedback_crk_numerico = evaluar_crk_numerico(cuotas, k, respuesta)
        except (TypeError, ValueError) as error:
            st.session_state.feedback_crk_numerico = {"error_entrada": str(error)}
    feedback = st.session_state.get("feedback_crk_numerico")
    if feedback is not None:
        if "error_entrada" in feedback:
            st.error(feedback["error_entrada"])
        else:
            mensaje = "Acierto." if feedback["acierto"] else "Error en la respuesta."
            (st.success if feedback["acierto"] else st.error)(
                f"{mensaje} Porcentaje correcto: {feedback['porcentaje_correcto']:.12g} %."
            )
            st.write(feedback["justificacion"])


def _formatear_ihh_evaluacion(puntos):
    """IHH válido en puntos -> texto español, preciso al lado de una frontera.

    Solo cambia presentación: la clasificación siempre utiliza el valor original.
    Si 12 cifras significativas ocultan el lado de 1500/2500, usa repr del float.
    Propaga la validación de clasificar_ihh; no calcula otro IHH ni percentil.
    """
    categoria = clasificar_ihh(puntos)
    valor = float(puntos)
    texto = f"{valor:.12g}"
    mostrado = float(texto)
    if (clasificar_ihh(mostrado) != categoria
            or (mostrado in (1500, 2500) and mostrado != valor)):
        texto = repr(valor)
    if "e" in texto.lower():
        return texto.replace(".", ",")
    entero, _, decimales = texto.partition(".")
    resultado = f"{int(entero):,}".replace(",", ".")
    decimales = decimales.rstrip("0")
    return resultado + ("," + decimales if decimales else "")


def _intervalo_ihh_presentado(categoria):
    """Categoría vigente -> su intervalo en puntos con millares legibles."""
    return INTERVALOS[categoria].replace("1500", "1.500").replace("2500", "2.500")


def _mensaje_error_ihh(resultado):
    """Feedback vigente de evaluar_ihh -> explicación de una selección errónea.

    Usa respuesta, categoría e IHH originales, sin recalcular cuotas o percentil.
    Las razones describen los intervalos existentes y sus extremos excluidos.
    """
    seleccion = resultado["respuesta"]
    correcta = resultado["clasificacion"]
    puntos = _formatear_ihh_evaluacion(resultado["ihh_puntos"])
    if seleccion == "Baja":
        razon = "alcanza o supera 1.500 puntos, límite que la categoría baja excluye"
    elif seleccion == "Alta":
        razon = "es menor que 2.500 puntos, el mínimo incluido de la categoría alta"
    elif correcta == "Baja":
        razon = "es menor que 1.500 puntos, el mínimo incluido de la categoría moderada"
    else:
        razon = "alcanza o supera 2.500 puntos, el límite superior excluido de la categoría moderada"
    return (
        f"Error en la respuesta. Seleccionaste {seleccion.lower()}, cuyo intervalo es "
        f"{_intervalo_ihh_presentado(seleccion)}. El caso tiene {puntos} puntos: {razon}, "
        "por lo que no pertenece a ese intervalo. "
        f"La categoría correcta es concentración {correcta.lower()}, cuyo intervalo es "
        f"{_intervalo_ihh_presentado(correcta)}."
    )


def resumir_justificacion_ihh(cuotas_validadas, texto_ihh, justificacion_completa):
    """N proporciones válidas y texto de IHH en puntos -> justificación str.

    Hasta 12 empresas conserva el desarrollo recibido. Para más empresas
    muestra las cinco cuotas mayores en %, sin recalcular IHH ni cambiar
    las cuotas o la clasificación; texto_ihh conserva su precisión original.
    """
    if len(cuotas_validadas) <= 12:
        return justificacion_completa
    mayores = sorted((float(cuota) * 100.0 for cuota in cuotas_validadas), reverse=True)[:5]
    lista = ", ".join(f"{valor:.10g}" for valor in mayores)
    return (
        f"El caso contiene {len(cuotas_validadas)} empresas. "
        f"Sus cinco cuotas mayores son [{lista}] %. "
        "Al sumar los cuadrados de todas las cuotas porcentuales, "
        f"el IHH es {texto_ihh} puntos."
    )


def _mostrar_evaluacion(cuotas, muestra, vigente):
    """Estado separado del gráfico; invalida feedback por caso o simulación."""
    st.subheader("4. Evaluar el IHH del caso")
    habilitada = vigente and cuotas is not None
    st.session_state.evaluacion_habilitada = habilitada
    contexto = (
        cuotas, st.session_state.editor_revision,
        st.session_state.revision_muestra,
        st.session_state.configuracion_actual, vigente,
    )
    if st.session_state.get("contexto_evaluacion") != contexto:
        _limpiar_respuestas()
        st.session_state.contexto_evaluacion = contexto

    st.write(PREGUNTA_IHH)
    st.caption("Esta pregunta usa el IHH en puntos, cualquiera que sea el indicador del histograma.")
    with st.expander("Criterio didáctico y fuente"):
        for opcion in OPCIONES:
            st.write(f"**{opcion}:** {INTERVALOS[opcion]}.")
        st.write(CONVENCION_FRONTERAS)
        st.markdown(f"Fuente: [Guía FNE de mayo de 2022, sección III.B, pp. 15–16, párrafos 32–36]({FUENTE_FNE}).")
        st.caption("La guía considera también ΔIHH y otros antecedentes; aquí se practica solo la clasificación del nivel de IHH.")
    st.caption(ALCANCE_DIDACTICO)
    if not habilitada:
        st.info("Para evaluar, necesitas cuotas válidas y una muestra vigente. Corrige el caso o simula nuevamente.")
    respuesta = st.radio(
        "Tu clasificación del IHH en puntos", OPCIONES, index=None,
        key="respuesta_evaluacion", disabled=not habilitada,
        on_change=_limpiar_resultado_evaluacion,
    )
    if st.button("Comprobar respuesta", key="comprobar_evaluacion", type="primary",
                 disabled=not habilitada or respuesta is None):
        st.session_state.resultado_evaluacion = evaluar_ihh(
            cuotas, respuesta, muestra.ihh_puntos, unidad_muestra="puntos",
        )

    _mostrar_complementarias(habilitada)
    _mostrar_crk_numerico(cuotas, st.session_state.configuracion_actual[1], habilitada)

    resultado = st.session_state.get("resultado_evaluacion")
    if resultado is None:
        return
    if resultado["acierto"]:
        st.success(f"Acierto. La clasificación correcta es {resultado['clasificacion'].lower()}.")
    else:
        st.error(_mensaje_error_ihh(resultado))
    st.write(f"**IHH calculado:** {_formatear_ihh_evaluacion(resultado['ihh_puntos'])} puntos. "
             f"**Intervalo:** {_intervalo_ihh_presentado(resultado['clasificacion'])}.")
    st.caption(f"Valor interno sin redondear: {resultado['ihh_puntos']!r} puntos. {CONVENCION_FRONTERAS}")
    st.write(resumir_justificacion_ihh(
        cuotas, _formatear_ihh_evaluacion(resultado["ihh_puntos"]), resultado["justificacion"],
    ))
    tabla_aportes = pd.DataFrame({
        "Empresa": [f"Empresa {i + 1}" for i in range(len(cuotas))],
        "Cuota (%)": resultado["cuotas_porcentaje"],
        "Aporte al IHH (puntos)": resultado["aportes_ihh"],
    })
    if len(cuotas) > 12:
        with st.expander("Desarrollo completo y aportes al IHH"):
            st.write(resultado["justificacion"])
            st.dataframe(tabla_aportes, hide_index=True, width="stretch")
    else:
        st.dataframe(tabla_aportes, hide_index=True, width="stretch")
    st.metric("Percentil real del IHH en la muestra vigente", f"{resultado['percentil_ihh']:.6g} %")
    st.write(resultado["explicacion_percentil"])
    st.info(
        "Los cortes de 1500 y 2500 puntos determinan la clasificación didáctica. "
        "El percentil describe la posición relativa del caso en la muestra de Monte Carlo: "
        "puede cambiar entre simulaciones sin cambiar la clasificación por IHH."
    )


def main():
    st.set_page_config(page_title="Mercados · Concentración de ventas", page_icon="📊", layout="wide")
    st.html(ESTILO)
    st.caption("ORGANIZACIÓN INDUSTRIAL · LABORATORIO DE MERCADOS")
    st.title("Cómo se reparten las ventas")
    st.write("Configura un mercado hipotético, simula otros repartos y compara un caso particular.")

    st.subheader("1. Configurar")
    columnas = st.columns(3)
    indicador = columnas[0].selectbox(
        "Indicador del histograma", ["CRk", "IHH", "ID", "IE"], key="indicador",
        help="Cambiar el indicador reutiliza la muestra existente.",
    )
    columnas[0].caption(AYUDAS_INDICADORES[indicador])
    valor_n = columnas[1].number_input("Empresas (N)", min_value=2, max_value=100,
                                         value=None if "n" in st.session_state else 4, step=1, key="n")
    if valor_n is None:
        _bloquear_configuracion_incompleta("N")
    n = int(valor_n)
    if st.session_state.get("k") is not None and st.session_state.k > n:
        st.session_state.k = n
    valor_k = columnas[2].number_input(
        "Empresas en CRk (k)", min_value=1, max_value=n,
        value=None if "k" in st.session_state else min(2, n), step=1,
        key="k", disabled=indicador != "CRk",
        help="Se ajusta al seleccionar CRk; su valor se conserva para la tarjeta CRk.",
    )
    if valor_k is None:
        _bloquear_configuracion_incompleta("k")
    k = int(valor_k)
    columnas = st.columns(3)
    valor_iteraciones = columnas[0].number_input(
        "Iteraciones", min_value=1, max_value=MAX_ITERACIONES,
        value=None if "iteraciones" in st.session_state else 1000, step=100, key="iteraciones",
    )
    usar_semilla = columnas[1].checkbox("Usar semilla reproducible", value=True, key="usar_semilla")
    valor_semilla = columnas[2].number_input(
        "Semilla", min_value=0, max_value=2 ** 32 - 1,
        value=None if "semilla" in st.session_state else 42, step=1, key="semilla",
        disabled=not usar_semilla,
    )
    if valor_iteraciones is None or (usar_semilla and valor_semilla is None):
        _bloquear_configuracion_incompleta("iteraciones o semilla")
    iteraciones = int(valor_iteraciones)
    semilla = int(valor_semilla) if usar_semilla else None
    configuracion = (n, k, iteraciones, semilla)
    st.session_state.setdefault("muestra", None)
    st.session_state.setdefault("muestra_desactualizada", False)
    st.session_state.setdefault("revision_muestra", 0)
    st.session_state.setdefault("duracion_simulacion", None)
    st.session_state.setdefault("simulacion_en_curso", False)
    if st.session_state.muestra is not None and not isinstance(st.session_state.muestra, ResultadoSimulacionCompacto):
        # Migrar solo las cuatro series; jamás conservar cuotas completas en UI.
        try:
            st.session_state.muestra = compactar_resultado(st.session_state.muestra)
        except (TypeError, ValueError, KeyError):
            st.session_state.muestra = None
        st.session_state.muestra_desactualizada = True
    if st.session_state.get("configuracion_actual") != configuracion and st.session_state.muestra is not None:
        st.session_state.muestra_desactualizada = True
    st.session_state.configuracion_actual = configuracion

    if st.session_state.get("caso_n") != n:
        _reemplazar_caso(np.full(n, 100 / n))
        st.session_state.caso_n = n
        st.session_state.aviso_caso = f"Tabla actualizada a {n} empresas con cuotas iguales."
    st.session_state.setdefault("contador_casos", 0)
    if "semilla_casos" not in st.session_state:
        st.session_state.semilla_casos = int(np.random.SeedSequence().entropy)

    st.subheader("2. Simular")
    st.caption(
        "Dirichlet(1,…,1) genera cuotas entre 0 y 1 que representan el 100 % del mercado. "
        "Supone empresas simétricas y mercados hipotéticos independientes; "
        "no reproduce automáticamente un sector real."
    )
    maximo_texto = f"{MAX_ITERACIONES:,}".replace(",", ".")
    st.warning(
        "Aumentar el número de empresas o de iteraciones incrementa el tiempo de respuesta "
        "y el consumo de memoria y procesamiento. "
        f"Máximo permitido: {maximo_texto} iteraciones."
    )
    with st.expander("Detalles de rendimiento"):
        st.write(ADVERTENCIA_RECURSOS)
    if iteraciones >= 50000:
        st.warning("Volumen alto: más latencia, procesamiento y memoria por sesión. "
                   "Las descargas CSV añaden trabajo al exportar; usuarios concurrentes consumen recursos adicionales.")
    if st.button("Simular mercados", type="primary", key="simular", width="stretch"):
        barra = None
        completada = False
        try:
            st.session_state.simulacion_en_curso = True
            barra = st.progress(0.0, text=f"0 / {iteraciones:,} iteraciones completadas")

            def actualizar_progreso(completadas, total):
                # La interfaz confirma el 100 % al recibir y guardar la muestra.
                # El motor avisa del último lote después de construir el resultado.
                if completadas < total:
                    barra.progress(completadas / total,
                                   text=f"{completadas:,} / {total:,} iteraciones completadas")

            with st.spinner("Generando mercados y calculando indicadores…"):
                inicio = perf_counter()
                nueva_muestra = simular_mercados_compactos(
                    n, k, iteraciones, semilla, callback_progreso=actualizar_progreso,
                )
                duracion = perf_counter() - inicio
            st.session_state.muestra = nueva_muestra
            st.session_state.duracion_simulacion = duracion
            st.session_state.muestra_desactualizada = False
            st.session_state.revision_muestra += 1
            barra.progress(1.0, text=f"{iteraciones:,} / {iteraciones:,} iteraciones completadas")
            completada = True
        except Exception as error:
            st.error(f"No se pudo completar la simulación: {error}")
        finally:
            st.session_state.simulacion_en_curso = False
            if barra is not None and not completada:
                barra.empty()

    muestra = st.session_state.muestra
    vigente = muestra is not None and not st.session_state.muestra_desactualizada
    if muestra is None:
        st.info("Pulsa «Simular mercados» para obtener la primera distribución.")
    elif not vigente:
        st.warning("Muestra desactualizada: cambió la configuración. Simula nuevamente para habilitar la comparación.")
    else:
        st.success(f"Muestra vigente: {iteraciones:,} mercados de {n} empresas. Puedes editar el caso sin volver a simular.")
    if st.session_state.duracion_simulacion is not None:
        st.caption(f"Última ejecución completada · tiempo del motor: {st.session_state.duracion_simulacion:.6f} s. "
                   "No incluye renderizado, red ni descarga.")
    if muestra is not None:
        config_muestra = muestra["configuracion"]
        with st.expander("Configuración de la última muestra"):
            st.write({campo: config_muestra[campo] for campo in (
                "n", "k", "iteraciones", "semilla", "entropia_semilla", "version_numpy",
            )})
        st.download_button(
            "Descargar muestra CSV", data=lambda: csv_muestra(muestra),
            file_name="mercados_simulados.csv", mime="text/csv", on_click="ignore",
            disabled=not vigente, key="descargar_muestra",
        )

    st.subheader("3. Comparar")
    st.write("Introduce las ventas de cada empresa como porcentaje. La suma debe ser 100 %.")
    st.caption(
        "El cierre se valida en proporciones con tolerancia absoluta de 10⁻¹⁰ y relativa cero "
        "(atol=1e-10, rtol=0), por la representación numérica en punto flotante. "
        "Se conservan las cuotas originales, sin ajustarlas ni normalizarlas."
    )
    botones = st.columns(3)
    if botones[0].button("Cuotas iguales", key="iguales", width="stretch"):
        _reemplazar_caso(np.full(n, 100 / n))
        st.session_state.aviso_caso = "Caso actualizado con cuotas iguales."
    if botones[1].button("Generar caso aleatorio", key="aleatorio", width="stretch"):
        contador = st.session_state.contador_casos + 1
        raiz = semilla if semilla is not None else st.session_state.semilla_casos
        semilla_caso = int(np.random.SeedSequence([contador, raiz]).generate_state(1, dtype=np.uint64)[0])
        caso_generado = generar_caso_aleatorio(n, k, semilla=semilla_caso)
        _reemplazar_caso(caso_generado["cuotas"] * 100)
        st.session_state.contador_casos = contador
        st.session_state.aviso_caso = f"Nuevo caso aleatorio #{contador}; la muestra de mercados se conserva."
    botones[2].button("Ejemplo 40–30–20–10", key="ejemplo", width="stretch",
                      on_click=_cargar_ejemplo,
                      help="Ajusta N a 4, carga cuatro cuotas y conserva k si está entre 1 y 4.")
    if st.session_state.get("aviso_caso"):
        st.caption(st.session_state.aviso_caso)

    tabla_editada = st.data_editor(
        st.session_state.caso_base, hide_index=True, num_rows="fixed", disabled=["Empresa"],
        key=f"editor_caso_{st.session_state.editor_revision}", width="stretch",
        height=min(420, 38 + n * 35),
        column_config={"Cuota (%)": st.column_config.NumberColumn(
            "Cuota (%)", min_value=0.0, max_value=100.0, required=True,
            format="%.8f", help="Porcentaje entre 0 y 100; el formato mostrado no redondea el cálculo.",
        )},
    )
    porcentajes = tabla_editada["Cuota (%)"].tolist()
    todos_finitos = all(isinstance(valor, Real) and math.isfinite(valor) for valor in porcentajes)
    if todos_finitos:
        suma = math.fsum(porcentajes)
        diferencia = 100 - suma
        texto_suma = f"{suma:.10f}".rstrip("0").rstrip(".")
        st.metric("Suma de cuotas", f"{texto_suma} %")
        if abs(diferencia) <= indices.TOLERANCIA_SUMA * 100:
            st.caption("Cierre dentro de tolerancia: falta/sobra 0 % a la precisión admitida.")
        else:
            verbo = "Falta" if diferencia > 0 else "Sobra"
            st.warning(f"{verbo} {abs(diferencia):.10g} % para alcanzar 100 %.")
    else:
        st.warning("La suma y la diferencia no están disponibles: completa todas las cuotas con valores finitos.")

    cuotas = None
    try:
        cuotas = validar_porcentajes(porcentajes, n)
    except (TypeError, ValueError) as error:
        st.error(f"Caso inválido: {error} No se normaliza automáticamente.")

    st.session_state.comparacion_habilitada = vigente and cuotas is not None
    if cuotas is not None:
        valores_caso = {
            "crk": indices.crk(cuotas, k), "ihh": indices.ihh(cuotas),
            "id": indices.indice_dominancia(cuotas), "ie": indices.entropia_shannon(cuotas),
        }
        tarjetas = st.columns(4)
        tarjetas[0].metric(f"CR{k}", f"{valores_caso['crk'] * 100:.2f} %", border=True)
        tarjetas[1].metric("IHH (puntos)", f"{valores_caso['ihh'] * 10000:.2f}", border=True)
        tarjetas[2].metric("ID · García Alba", f"{valores_caso['id']:.6f}", border=True)
        tarjetas[3].metric("IE · Shannon (nats)", f"{valores_caso['ie']:.6f}", border=True)
        st.caption(f"IE / ln(N) = {valores_caso['ie'] / math.log(n):.6f}.")
        with st.expander("Detalle de indicadores, fórmulas y unidades"):
            st.dataframe(pd.DataFrame({
                "Indicador": [f"CR{k}", "IHH", "ID de García Alba", "IE de Shannon", "IE / ln(N)"],
                "Valor": [valores_caso["crk"] * 100, valores_caso["ihh"] * 10000,
                          valores_caso["id"], valores_caso["ie"], valores_caso["ie"] / math.log(n)],
                "Unidad": ["% de ventas", "puntos", "adimensional", "nats", "adimensional"],
            }), hide_index=True, width="stretch")
            st.latex(r"CR_k=\sum_{i=1}^{k}s_{(i)},\quad IHH_{puntos}=10000\sum_i s_i^2")
            st.latex(r"ID=\frac{\sum_i s_i^4}{(\sum_i s_i^2)^2},\quad IE=-\sum_{i:s_i>0}s_i\ln s_i")
            st.caption("Cuotas s en proporciones; CRk se muestra multiplicado por 100. "
                       "IE normalizada = IE/ln(N). Se conserva la precisión original al calcular y exportar.")
        st.plotly_chart(grafico_cuotas(cuotas), width="stretch", theme=None, key="grafico_cuotas",
                        config={"displaylogo": False, "responsive": True})
        tabla_descarga = tabla_editada.copy(deep=True)
        st.download_button("Descargar caso CSV", data=lambda: csv_caso(tabla_descarga),
                           file_name="caso_particular.csv", mime="text/csv", on_click="ignore", key="descargar_caso")
    else:
        valores_caso = None

    if vigente:
        clave = {"CRk": "crk", "IHH": "ihh", "ID": "id", "IE": "ie"}[indicador]
        serie = muestra.ihh_puntos if clave == "ihh" else muestra[clave]
        caso = valores_caso[clave] if valores_caso is not None else None
        if clave == "ihh" and caso is not None:
            caso *= 10000
        percentil = percentil_empirico(serie, caso) if caso is not None else None
        if percentil is not None:
            st.metric("Percentil empírico del caso", f"{percentil:.2f} %")
            nombre_indicador = f"CR{k}" if indicador == "CRk" else indicador
            st.markdown(
                f"**Cómo leerlo:** el **{percentil:.2f} %** de los mercados simulados "
                f"tiene un valor de **{nombre_indicador}** menor o igual al de este caso. "
                "Se incluyen los empates."
            )
            st.caption(
                "El percentil compara este caso con mercados simulados con el mismo N bajo el modelo "
                "Dirichlet(1,…,1). No es un umbral normativo de concentración. "
                "Depende de la muestra; aumentar las iteraciones reduce su variabilidad estadística. "
                "Con el mismo caso, configuración y semilla, repetir en el mismo entorno permite reproducirlo."
            )
            if clave == "ie":
                st.info("Un percentil alto de entropía indica mayor entropía respecto de la muestra; "
                        "no significa mayor concentración.")
        else:
            st.info("Corrige el caso para añadir su línea y su percentil al histograma.")
        figura = histograma_indicador(serie, clave, caso, percentil, k=k, ihh_en_puntos=True)
        if figura.layout.meta["constante"]:
            st.info("Distribución constante a precisión numérica: todas las observaciones se muestran en una barra.")
        elif figura.layout.meta["fuera_de_rango"]:
            st.info("El caso está fuera del rango observado. El eje se amplía para mostrarlo; su percentil es 0 % o 100 %.")
        if clave == "crk" and k == n and percentil is not None:
            st.caption("Cuando k=N, CRk es 100 % en todos los mercados. Por eso no distingue niveles "
                       "de concentración. Todos los valores empatan y, con la definición utilizada, "
                       "el percentil es 100 %.")
        st.plotly_chart(figura, width="stretch", theme=None, key="histograma",
                        config={"displaylogo": False, "responsive": True})

    st.divider()
    _mostrar_evaluacion(cuotas, muestra, vigente)


if __name__ == "__main__":
    main()
