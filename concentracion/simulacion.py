"""Mercados iid Dirichlet(1,...,1), uniformes sobre el simplex de cuotas.

Empresas simétricas, cuotas dependientes por su cierre y mercados independientes.
Este supuesto no describe un sector real ni implica indicadores uniformes.
Normalizar uniformes positivas no da uniformidad en el simplex; exponenciales
normalizadas equivalen a Dirichlet(1), lognormales añaden parámetros de tamaños
 y multinomiales una escala discreta. Densidad y algoritmo oficiales:
https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.dirichlet.html

Precisión float64: validar cada fila con atol=1e-10, rtol=0 y cuotas en [0,1].
No reparar ni redondear. Reducciones NumPy/math.fsum pueden diferir unos ulps.
Reproducibilidad: default_rng(semilla) directo, sin spawn; misma versión NumPy.
Caso aleatorio: generador propio en un espacio de semillas distinto, sin consumir
la secuencia de Monte Carlo. Configuración registra semilla efectiva y versión.

API completa simular_mercados: ResultadoSimulacion con cuotas y seis indicadores.
API UI simular_mercados_compactos: ResultadoSimulacionCompacto, IHH en puntos.
Solo la API completa conserva la matriz; no debe guardarse en la sesión de UI.
Motor compacto: 1000 iteraciones por defecto, máximo 100000; lotes de hasta
4096 filas y una matriz de trabajo reutilizada. Sus series ocupan 32*M bytes.
Mediciones de la etapa anterior y referencia experimental: medir_rendimiento.py;
resultados y método en rendimiento.json y COMPROBACIONES.md; no se repitieron
en esta revisión de compatibilidad. No se prometen
latencias públicas ni memoria total del proceso a partir de tracemalloc.
"""

from dataclasses import dataclass
from numbers import Integral, Real
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .indices import (
    TOLERANCIA_SUMA,
    crk,
    entropia_shannon,
    ihh,
    indice_dominancia,
)


MAX_ITERACIONES = 100_000
TAMANO_LOTE = 4096
INDICADORES = ("crk", "ihh", "id", "ie")
ADVERTENCIA_RECURSOS = (
    "El tiempo de respuesta y el procesamiento crecen con N e iteraciones; "
    "el rendimiento depende del equipo y su carga. Se permiten hasta 100000 "
    "iteraciones por llamada. Los cuatro arrays ocupan 32*iteraciones bytes "
    "(3.05 MiB al máximo), más un lote de cuotas y una matriz de trabajo "
    "de hasta 4096 filas, y la memoria del entorno. No se guarda la matriz "
    "completa de cuotas en la interfaz. "
    "Las llamadas son síncronas. Conservar resultados de muchas llamadas "
    "acumula memoria en el código que los recibe."
)


class ResultadoSimulacion(dict):
    """Resultado completo con cuotas float64 (M,N) en proporciones.

    Construcción interna: series es un dict con crk, ihh, id, ie y configuracion;
    cuotas es la matriz validada de la misma simulación. Conserva esas cinco
    claves locales y recupera atributos públicos: crk e ihh_decimal en proporciones,
    ihh_puntos en puntos, id_garcia_alba adimensional, entropia en nats y
    entropia_normalizada adimensional. ihh_puntos y entropia_normalizada se
    calculan al acceder, sin repetir fórmulas. n e iteraciones son enteros.
    Comparación por identidad para evitar igualdad ambigua de arrays NumPy.
    """

    def __init__(self, series, cuotas):
        super().__init__(series)
        self.cuotas = cuotas

    def __eq__(self, otro):
        return self is otro

    def __ne__(self, otro):
        return self is not otro

    @property
    def configuracion(self):
        return self["configuracion"]

    @property
    def n(self):
        return int(self.cuotas.shape[1])

    @property
    def iteraciones(self):
        return int(self.cuotas.shape[0])

    @property
    def crk(self):
        return self["crk"]

    @property
    def ihh_decimal(self):
        return self["ihh"]

    @property
    def ihh_puntos(self):
        """Array float64 (M,) nuevo, en puntos; no queda almacenado en el objeto."""
        return self.ihh_decimal * 10000.0

    @property
    def id_garcia_alba(self):
        return self["id"]

    @property
    def entropia(self):
        return self["ie"]

    @property
    def entropia_normalizada(self):
        """Array float64 (M,) nuevo: IE/ln(N), incluyendo empresas con cuota cero."""
        return self.entropia / np.log(self.n)


@dataclass(frozen=True, eq=False)
class ResultadoSimulacionCompacto:
    """Cuatro arrays float64 (M,) y configuración, sin matriz de cuotas.

    crk: proporción; ihh_puntos: IHH ya multiplicado por 10000; id: adimensional;
    ie: entropía en nats. Solo se almacenan estas cuatro series. La entropía
    normalizada se calcula al mostrar/exportar. Las unidades no son intercambiables
    con el IHH proporcional de la API clásica. Los arrays son propiedad del resultado.
    """

    crk: NDArray[np.float64]
    ihh_puntos: NDArray[np.float64]
    id: NDArray[np.float64]
    ie: NDArray[np.float64]
    configuracion: Dict[str, Any]

    def __getitem__(self, clave):
        """Acceso por las claves explícitas, sin alias ambiguo 'ihh'."""
        if clave not in ("crk", "ihh_puntos", "id", "ie", "configuracion"):
            raise KeyError(clave)
        return getattr(self, clave)


def _entero_en_rango(valor: int, nombre: str, minimo: int, maximo: int) -> int:
    if isinstance(valor, (bool, np.bool_)) or not isinstance(valor, Integral):
        raise TypeError(f"{nombre} debe ser entero, sin aceptar booleanos.")
    if not minimo <= valor <= maximo:
        raise ValueError(f"{nombre} debe estar entre {minimo} y {maximo}.")
    return int(valor)


def _crear_generador(
    semilla: Optional[int], flujo: int
) -> Tuple[np.random.Generator, int]:
    if semilla is not None:
        if isinstance(semilla, (bool, np.bool_)) or not isinstance(semilla, Integral):
            raise TypeError("semilla debe ser un entero no negativo o None.")
        if semilla < 0:
            raise ValueError("semilla debe ser no negativa.")
        semilla = int(semilla)
    # Se usa directamente default_rng(semilla). Para None se guarda la entropía
    # efectiva que permite reproducir la llamada; no se crean flujos spawn.
    entropia = int(np.random.SeedSequence().entropy) if semilla is None else semilla
    # Otro espacio determinista de semillas para casos, sin consumir Monte Carlo.
    # Configuración guarda la semilla antes de derivarla: repetirla recrea el caso.
    semilla_rng = entropia if flujo == 0 else (entropia << 64) | 0x4341534F
    return np.random.default_rng(semilla_rng), entropia


def _configuracion(
    n: int, k: int, semilla: Optional[int], entropia: int,
    flujo: int, rng: np.random.Generator,
) -> Dict[str, Any]:
    return {
        "n": n,
        "k": k,
        "semilla": None if semilla is None else int(semilla),
        "entropia_semilla": entropia,
        "flujo": flujo,
        "distribucion": "Dirichlet",
        "alpha": 1.0,
        "generador": type(rng.bit_generator).__name__,
        "version_numpy": np.__version__,
        "atol": TOLERANCIA_SUMA,
        "rtol": 0.0,
        "unidades": {
            "crk": "proporcion", "ihh": "proporcional",
            "id": "adimensional", "ie": "nats",
        },
    }


def _validar_filas(cuotas: NDArray[np.float64], n: int, cantidad: int) -> None:
    """Comprueba todas las filas; falla sin reparar resultados del generador."""
    if cuotas.shape != (cantidad, n) or cantidad == 0:
        raise RuntimeError("El generador produjo dimensiones de cuotas inválidas.")
    minimo, maximo = np.min(cuotas), np.max(cuotas)
    if not np.isfinite(minimo) or not np.isfinite(maximo):
        raise RuntimeError("El generador produjo cuotas no finitas.")
    if minimo < 0 or maximo > 1:
        raise RuntimeError("El generador produjo cuotas fuera de [0, 1].")
    sumas = np.sum(cuotas, axis=1, dtype=np.float64)
    if not np.allclose(sumas, 1.0, atol=TOLERANCIA_SUMA, rtol=0.0):
        raise RuntimeError("No todas las filas suman 1 con atol=1e-10 y rtol=0.")


def _calcular_indicadores(
    cuotas: NDArray[np.float64], k: int, trabajo=None, salidas=None,
) -> Dict[str, NDArray[np.float64]]:
    """Fórmulas vectorizadas de indices.py para filas ya validadas.

    Reutiliza una matriz temporal sin modificar las cuotas recibidas.
    """
    if trabajo is None:
        trabajo = np.empty_like(cuotas)
    if salidas is None:
        salidas = {nombre: np.empty(cuotas.shape[0], dtype=np.float64) for nombre in INDICADORES}
    np.square(cuotas, out=trabajo)
    ihh_valores = salidas["ihh"]
    np.sum(trabajo, axis=1, dtype=np.float64, out=ihh_valores)
    np.square(trabajo, out=trabajo)
    np.sum(trabajo, axis=1, dtype=np.float64, out=salidas["id"])
    np.divide(salidas["id"], ihh_valores ** 2, out=salidas["id"])

    trabajo.fill(0.0)
    np.log(cuotas, out=trabajo, where=cuotas > 0)
    np.multiply(cuotas, trabajo, out=trabajo)
    np.sum(trabajo, axis=1, dtype=np.float64, out=salidas["ie"])
    np.negative(salidas["ie"], out=salidas["ie"])

    n = cuotas.shape[1]
    if k == n:
        salidas["crk"].fill(1.0)
    else:
        trabajo[:] = cuotas
        trabajo.partition(n - k, axis=1)
        np.sum(trabajo[:, n - k:], axis=1, dtype=np.float64, out=salidas["crk"])
    return salidas


def _simular_por_lotes(
    n, k, iteraciones, semilla, tamano_lote, puntos, conservar_cuotas=False,
    callback_progreso=None,
):
    n = _entero_en_rango(n, "n", 2, 100)
    k = _entero_en_rango(k, "k", 1, n)
    iteraciones = _entero_en_rango(iteraciones, "iteraciones", 1, MAX_ITERACIONES)
    tamano_lote = _entero_en_rango(tamano_lote, "tamano_lote", 1, TAMANO_LOTE)
    if callback_progreso is not None and not callable(callback_progreso):
        raise TypeError("callback_progreso debe ser callable o None.")
    rng, entropia = _crear_generador(semilla, flujo=0)
    configuracion = _configuracion(n, k, semilla, entropia, 0, rng)
    configuracion.update(iteraciones=iteraciones, tamano_lote=tamano_lote,
                         esquema="compacto" if puntos else "clasico")
    if puntos:
        configuracion["unidades"]["ihh"] = "puntos"
    resultado = {nombre: np.empty(iteraciones, dtype=np.float64) for nombre in INDICADORES}
    completas = np.empty((iteraciones, n), dtype=np.float64) if conservar_cuotas else None
    alpha = np.ones(n, dtype=np.float64)
    trabajo = np.empty((min(tamano_lote, iteraciones), n), dtype=np.float64)
    if callback_progreso is not None:
        callback_progreso(0, iteraciones)
    for inicio in range(0, iteraciones, tamano_lote):
        fin = min(inicio + tamano_lote, iteraciones)
        cuotas = rng.dirichlet(alpha, size=fin - inicio)
        _validar_filas(cuotas, n, fin - inicio)
        if conservar_cuotas:
            completas[inicio:fin] = cuotas
        salidas = {nombre: resultado[nombre][inicio:fin] for nombre in INDICADORES}
        _calcular_indicadores(cuotas, k, trabajo[:fin - inicio], salidas)
        if puntos:
            np.multiply(salidas["ihh"], 10000.0, out=salidas["ihh"])
        del cuotas, salidas
        # El último aviso se emite en la API pública, una vez construido su
        # resultado. Una validación o construcción fallida nunca anuncia 100 %.
        if callback_progreso is not None and fin < iteraciones:
            callback_progreso(fin, iteraciones)
    resultado["configuracion"] = configuracion
    return ResultadoSimulacion(resultado, completas) if conservar_cuotas else resultado


def simular_mercados(
    n: int, k: int, iteraciones: int = 1000, semilla: Optional[int] = None,
    *, callback_progreso: Optional[Callable[[int, int], None]] = None,
) -> ResultadoSimulacion:
    """Genera mercados iid y devuelve el resultado completo, incluidas cuotas.

    Args:
        n: Número entero de empresas, entre 2 y 100.
        k: Entero entre 1 y n para CRk.
        iteraciones: Entero entre 1 y MAX_ITERACIONES (100000), por defecto 1000.
            El límite se controla aquí, independientemente de cualquier interfaz.
        semilla: Entero no negativo o None (entropía nueva del sistema operativo).
            No se admiten generadores externos ni booleanos. Usa default_rng directo.
        callback_progreso: Callable opcional, solo por nombre; recibe dos enteros
            (iteraciones_completadas, total). Se llama inicialmente con (0,total),
            tras cada lote calculado y validado y, para el último lote, una vez
            construido el resultado. Su retorno se ignora. No recibe cuotas ni
            consume números aleatorios; no depende de ninguna interfaz.

    Returns:
        ResultadoSimulacion: cuotas (iteraciones,n), los seis atributos de
        indicadores documentados en la clase y propiedades n e iteraciones.
        También mantiene las claves locales crk, ihh (proporcional), id, ie
        y configuracion, con n, k, iteraciones, semilla, entropía efectiva, flujo,
        distribución, unidades, lote, tolerancias, generador y versión de NumPy.
        La entropía efectiva permite repetir incluso una llamada con semilla=None:
        pásela luego como semilla. La repetición exige el mismo entorno NumPy;
        Generator no garantiza compatibilidad de secuencias entre versiones.

    Raises:
        TypeError: Por parámetros no enteros (incluidos bool) o semilla inválida.
        ValueError: Por n, k, iteraciones o semilla fuera de los rangos permitidos.
        RuntimeError: Si cualquier fila generada viola dimensiones, rango,
            finitud o cierre. No se devuelven resultados parciales.
        Las excepciones del callback se propagan; un fallo previo a la construcción
        del resultado no emite (total,total). La interfaz gestiona su limpieza.

    Recursos:
        Retiene 8*N*M bytes de cuotas más 32*M bytes de series base y temporales.
        Los atributos derivados generan un array adicional al acceder. Para UI
        y grandes muestras, usar simular_mercados_compactos, sin matriz completa.
    """
    resultado = _simular_por_lotes(
        n, k, iteraciones, semilla, TAMANO_LOTE,
        puntos=False, conservar_cuotas=True, callback_progreso=callback_progreso,
    )
    if callback_progreso is not None:
        callback_progreso(resultado.iteraciones, resultado.iteraciones)
    return resultado


def simular_mercados_compactos(
    n: int, k: int, iteraciones: int = 1000, semilla: Optional[int] = None,
    tamano_lote: int = TAMANO_LOTE,
    *, callback_progreso: Optional[Callable[[int, int], None]] = None,
) -> ResultadoSimulacionCompacto:
    """Monte Carlo para la UI: cuatro series, IHH en puntos, sin cuotas completas.

    n: entero [2,100]; k: entero [1,n]; iteraciones: entero [1,100000] (1000
    por defecto); semilla: entero no negativo o None; tamano_lote: entero
    [1,4096]. Rechaza booleanos. No normaliza ni redondea ninguna fila.
    Devuelve ResultadoSimulacionCompacto con arrays (iteraciones,) y configuración.
    Propaga TypeError/ValueError por parámetros inválidos y RuntimeError si cualquier
    fila no cumple finitud, [0,1] o suma 1 con atol=1e-10, rtol=0.
    Conserva exactamente las mismas cuotas reproducibles que default_rng(semilla)
    con una sola llamada Dirichlet. El cálculo escalar/vectorizado puede diferir
    unos pocos ulps; el lote no modifica las fórmulas ni fuerza percentiles.
    callback_progreso: callable opcional, solo por nombre, recibe (completadas,total)
    enteros; aviso inicial (0,total), uno por lote validado/calculado y último
    (total,total) después de construir ResultadoSimulacionCompacto. Retorno ignorado
    y excepciones propagadas. No modifica la secuencia aleatoria ni las unidades.
    Un callback no callable causa TypeError antes de generar mercados.
    """
    resultado = _simular_por_lotes(
        n, k, iteraciones, semilla, tamano_lote, puntos=True,
        callback_progreso=callback_progreso,
    )
    compacto = ResultadoSimulacionCompacto(
        resultado["crk"], resultado["ihh"], resultado["id"], resultado["ie"],
        resultado["configuracion"],
    )
    if callback_progreso is not None:
        callback_progreso(compacto.configuracion["iteraciones"], compacto.configuracion["iteraciones"])
    return compacto


def generar_caso_aleatorio(
    n: int, k: int, semilla: Optional[int] = None
) -> Dict[str, Any]:
    """Genera un único caso Dirichlet(1) mediante un generador independiente.

    Args:
        n: Número entero de empresas entre 2 y 100.
        k: Entero entre 1 y n para CRk.
        semilla: Entero no negativo o None; mismas reglas que simular_mercados.

    Returns:
        Diccionario con 'cuotas' (array float64 de forma (n,), en proporciones),
        'indicadores' (crk, ihh, id, ie calculados con indices.py, mismas unidades
        que la API clásica) y 'configuracion'. Usa un espacio de semillas separado del 0
        incluso con la misma semilla. Crear casos no consume la secuencia de
        simulaciones ni depende de su número de iteraciones o del orden de llamadas.
        La misma semilla produce el mismo caso en el mismo entorno.

    Raises:
        TypeError: Por n, k o semilla de tipo inválido, incluidos booleanos.
        ValueError: Por n, k o semilla fuera de rango.
        RuntimeError: Si las cuotas generadas no cumplen cierre, rango o finitud.
    """
    n = _entero_en_rango(n, "n", 2, 100)
    k = _entero_en_rango(k, "k", 1, n)
    rng, entropia = _crear_generador(semilla, flujo=1)
    cuotas = rng.dirichlet(np.ones(n, dtype=np.float64), size=1)
    _validar_filas(cuotas, n, 1)
    cuotas = cuotas[0].copy()
    return {
        "cuotas": cuotas,
        "indicadores": {
            "crk": crk(cuotas, k),
            "ihh": ihh(cuotas),
            "id": indice_dominancia(cuotas),
            "ie": entropia_shannon(cuotas),
        },
        "configuracion": _configuracion(n, k, semilla, entropia, 1, rng),
    }


def calcular_indicadores_vectorizados(cuotas, n, k) -> Dict[str, NDArray[np.float64]]:
    """M filas de N proporciones -> dict de seis arrays float64 (M,).

    n entero [2,100], k entero [1,n]; cuotas numéricas reales, matriz no vacía
    (M,N), finita en [0,1], cada fila cerrada con atol=1e-10, rtol=0. No modifica,
    normaliza ni redondea entradas. Devuelve claves crk (proporción), ihh_decimal
    (proporción), ihh_puntos (puntos), id_garcia_alba (adimensional), entropia
    (nats), entropia_normalizada (IE/ln(N), adimensional). Reutiliza el mismo
    núcleo vectorizado del motor. TypeError por tipos/bool; ValueError por
    dimensiones, rangos, finitud o cierre inválidos.
    """
    n = _entero_en_rango(n, "n", 2, 100)
    k = _entero_en_rango(k, "k", 1, n)
    originales = np.asarray(cuotas)
    if originales.dtype.kind not in "iuf":
        raise TypeError("cuotas debe contener números reales, sin bool.")
    if isinstance(cuotas, (list, tuple)) and any(
        isinstance(v, (bool, np.bool_)) for fila in cuotas
        if isinstance(fila, (list, tuple)) for v in fila
    ):
        raise TypeError("cuotas no admite booleanos.")
    valores = np.asarray(originales, dtype=np.float64)
    if valores.ndim != 2 or valores.shape[1] != n or valores.shape[0] == 0:
        raise ValueError("cuotas debe ser una matriz no vacía (M,N).")
    try:
        _validar_filas(valores, n, valores.shape[0])
    except RuntimeError as error:
        raise ValueError(str(error)) from error
    series = _calcular_indicadores(valores, k)
    return {
        "crk": series["crk"], "ihh_decimal": series["ihh"],
        "ihh_puntos": series["ihh"] * 10000.0,
        "id_garcia_alba": series["id"], "entropia": series["ie"],
        "entropia_normalizada": series["ie"] / np.log(n),
    }


def compactar_resultado(resultado) -> ResultadoSimulacionCompacto:
    """Resultado completo, compacto o dict local -> compacto independiente.

    Copia únicamente cuatro arrays float64 (M,) y configuración. CRk queda en
    proporciones, IHH en puntos, ID adimensional, IE en nats. Para dict local
    'ihh' está en proporciones salvo unidades.ihh='puntos'; la clave explícita
    ihh_puntos siempre está en puntos. Nunca retiene cuotas ni una referencia
    al resultado completo. TypeError por tipo no reconocido; ValueError por
    configuración/series inválidas. No genera mercados ni recalcula fórmulas.
    """
    from copy import deepcopy

    if isinstance(resultado, ResultadoSimulacionCompacto):
        config = deepcopy(resultado.configuracion)
        originales = (resultado.crk, resultado.ihh_puntos, resultado.id, resultado.ie)
    elif isinstance(resultado, dict):
        try:
            config = deepcopy(resultado["configuracion"])
            puntos = resultado.get("ihh_puntos")
            if puntos is None:
                factor = 1.0 if config.get("unidades", {}).get("ihh") == "puntos" else 10000.0
                puntos = np.asarray(resultado["ihh"]) * factor
            originales = (resultado["crk"], puntos, resultado["id"], resultado["ie"])
        except (KeyError, TypeError) as error:
            raise ValueError("Faltan series o configuración del resultado.") from error
    else:
        raise TypeError("Se requiere un resultado completo, compacto o dict local.")
    _entero_en_rango(config.get("n"), "n", 2, 100)
    _entero_en_rango(config.get("k"), "k", 1, config["n"])
    cantidad = _entero_en_rango(config.get("iteraciones"), "iteraciones", 1, MAX_ITERACIONES)
    arrays = []
    for original in originales:
        array = np.array(original, dtype=np.float64, copy=True)
        if array.shape != (cantidad,) or not np.all(np.isfinite(array)):
            raise ValueError("Las cuatro series deben ser finitas y tener forma (M,).")
        arrays.append(array)
    config["esquema"] = "compacto"
    config.setdefault("unidades", {})["ihh"] = "puntos"
    return ResultadoSimulacionCompacto(*arrays, config)


def percentil_empirico(simulaciones: ArrayLike, caso: float) -> float:
    """Devuelve 100 * cantidad(simulaciones <= caso) / cantidad(simulaciones).

    Args:
        simulaciones: Array o secuencia numérica real, finita, unidimensional
            y no vacía, de un indicador. No se aceptan texto, complejos ni bool.
        caso: Valor real finito del mismo indicador y en las mismas unidades.

    Returns:
        Percentil entre 0 y 100, incluyendo TODOS los empates. No interpola,
        redondea ni aplica tolerancia a las comparaciones; usa los valores
        representados en punto flotante. Para IE un percentil alto significa
        mayor diversidad/equilibrio relativo de ventas (menor concentración);
        para CRk, IHH e ID significa un valor mayor de concentración/dominancia.
        El percentil depende del supuesto Dirichlet y de n y k; no constituye
        una evaluación del mercado ni un umbral normativo.

    Raises:
        TypeError: Por muestras o caso de tipo no numérico real.
        ValueError: Por muestras vacías/no unidimensionales o valores no finitos.
    """
    if isinstance(simulaciones, (list, tuple)) and any(
        isinstance(valor, (bool, np.bool_)) for valor in simulaciones
    ):
        raise TypeError("simulaciones debe contener números reales, sin bool.")
    valores = np.asarray(simulaciones)
    if valores.ndim != 1 or valores.size == 0:
        raise ValueError("simulaciones debe ser un vector no vacío.")
    if valores.dtype.kind not in "iuf":
        raise TypeError("simulaciones debe contener números reales, sin bool.")
    if not np.all(np.isfinite(valores)):
        raise ValueError("simulaciones debe contener valores finitos.")
    if isinstance(caso, (bool, np.bool_)) or not isinstance(caso, Real):
        raise TypeError("caso debe ser un número real, sin bool.")
    try:
        caso = float(caso)
    except OverflowError as exc:
        raise ValueError("caso debe ser finito en punto flotante.") from exc
    if not np.isfinite(caso):
        raise ValueError("caso debe ser finito.")
    return 100.0 * (np.count_nonzero(valores <= caso) / valores.size)


def calcular_percentil_empirico(valores_simulados, valor_caso) -> float:
    """Vector real finito y caso en las MISMAS unidades -> float percentil [0,100].

    Incluye empates; delega validación y cómputo en percentil_empirico.
    Propaga TypeError/ValueError por vector/caso inválidos. No interpola.
    """
    return percentil_empirico(valores_simulados, valor_caso)
