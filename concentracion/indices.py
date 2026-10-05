"""Índices de concentración calculados con cuotas en proporciones.

Todas las funciones aceptan entre 2 y 100 cuotas reales, finitas, en [0, 1],
cuya suma difiera de 1 como máximo en 1e-10. No se normalizan ni redondean
las entradas. Los cálculos usan aritmética de punto flotante y ``math.fsum``.
El módulo no depende de una interfaz ni de bibliotecas externas.
"""

import math
from numbers import Integral, Real
from typing import Iterable, Tuple


TOLERANCIA_SUMA = 1e-10


def validar_numero_empresas(n: int) -> int:
    """Exige N entero entre 2 y 100; TypeError por bool/no entero, ValueError por rango."""
    if isinstance(n, bool) or not isinstance(n, Integral):
        raise TypeError("N debe ser entero, sin booleanos.")
    if not 2 <= n <= 100:
        raise ValueError("N debe estar entre 2 y 100.")
    return int(n)


def validar_cuotas(cuotas: Iterable[float], n: int = None) -> Tuple[float, ...]:
    """Valida y devuelve las cuotas como una tupla de proporciones ``float``.

    Args:
        cuotas: Iterable de 2 a 100 números reales en [0, 1]. Por ejemplo,
            40 % se expresa como 0.4. Se incluyen las empresas con cuota cero.
        n: N entero opcional entre 2 y 100. Si se proporciona exige exactamente
            N cuotas, manteniendo la llamada validar_cuotas(cuotas,n). Omitirlo
            es una extensión que infiere N; no se exige a los llamadores originales.

    Returns:
        Tupla en el orden original, sin normalización ni redondeo previo.

    Raises:
        TypeError: Si cuotas no es iterable, es texto o contiene valores que
            no son números reales (incluidos booleanos).
        ValueError: Si el número de cuotas está fuera de [2, 100], hay valores
            no finitos o fuera de [0, 1], o la suma no es 1 con tolerancia
            absoluta 1e-10 y tolerancia relativa cero.
    """
    if n is not None:
        n = validar_numero_empresas(n)
    if isinstance(cuotas, (str, bytes)):
        raise TypeError("Las cuotas deben ser un iterable de números reales.")
    try:
        valores = tuple(cuotas)
    except TypeError as exc:
        raise TypeError("Las cuotas deben ser un iterable de números reales.") from exc

    if not 2 <= len(valores) <= 100:
        raise ValueError("Se requieren entre 2 y 100 cuotas.")
    if n is not None and len(valores) != n:
        raise ValueError(f"Se requieren exactamente {n} cuotas.")

    proporciones = []
    for posicion, valor in enumerate(valores):
        if isinstance(valor, bool) or not isinstance(valor, Real):
            raise TypeError(f"La cuota en posición {posicion} debe ser un número real.")
        try:
            cuota = float(valor)
        except OverflowError as exc:
            raise ValueError(f"La cuota en posición {posicion} debe estar en [0, 1].") from exc
        if not math.isfinite(cuota):
            raise ValueError(f"La cuota en posición {posicion} debe ser finita.")
        if not 0 <= valor <= 1:
            raise ValueError(f"La cuota en posición {posicion} debe estar en [0, 1].")
        proporciones.append(cuota)

    if not math.isclose(
        math.fsum(proporciones), 1.0, rel_tol=0.0, abs_tol=TOLERANCIA_SUMA
    ):
        raise ValueError("Las cuotas deben sumar 1 con tolerancia absoluta 1e-10.")
    return tuple(proporciones)


def crk(cuotas: Iterable[float], k: int) -> float:
    """Devuelve CRk: suma de las k cuotas mayores, en proporción.

    Args:
        cuotas: Iterable de proporciones sujeto a ``validar_cuotas``.
        k: Número entero de empresas, entre 1 y N (cantidad de cuotas).

    Returns:
        Concentración en proporción; 0.7 equivale a 70 %.

    Raises:
        TypeError: Por cuotas no reales/no iterables o k no entero, incluido bool.
        ValueError: Por cuotas inválidas o k fuera de [1, N].
    """
    valores = validar_cuotas(cuotas)
    if isinstance(k, bool) or not isinstance(k, Integral):
        raise TypeError("k debe ser un entero.")
    if not 1 <= k <= len(valores):
        raise ValueError("k debe estar entre 1 y el número de cuotas.")
    return math.fsum(sorted(valores, reverse=True)[:int(k)])


def ihh(cuotas: Iterable[float]) -> float:
    """Devuelve el IHH = suma(s_i**2), adimensional en escala proporcional.

    Args:
        cuotas: Iterable de proporciones sujeto a ``validar_cuotas``.

    Returns:
        Suma de cuadrados; 0.3 equivale a 3000 puntos de IHH.

    Raises:
        TypeError: Por cuotas no reales o no iterables.
        ValueError: Por cantidad, rango, finitud o suma de cuotas inválidos.
    """
    valores = validar_cuotas(cuotas)
    return math.fsum(s ** 2 for s in valores)


def ihh_puntos(cuotas: Iterable[float]) -> float:
    """Devuelve el IHH en puntos: ``ihh(cuotas) * 10000``.

    Args:
        cuotas: Iterable de proporciones sujeto a ``validar_cuotas``.

    Returns:
        IHH en la escala de 0 a 10000 puntos, sin redondear.

    Raises:
        TypeError: Por cuotas no reales o no iterables.
        ValueError: Por cantidad, rango, finitud o suma de cuotas inválidos.
    """
    return ihh(cuotas) * 10000.0


def indice_dominancia(cuotas: Iterable[float]) -> float:
    """Devuelve el ID de García Alba = suma(s_i**4) / suma(s_i**2)**2.

    Args:
        cuotas: Iterable de proporciones sujeto a ``validar_cuotas``.

    Returns:
        Índice adimensional, igual a 1/N para cuotas iguales y a 1 si una
        empresa concentra todas las ventas.

    Raises:
        TypeError: Por cuotas no reales o no iterables.
        ValueError: Por cantidad, rango, finitud o suma de cuotas inválidos.
    """
    valores = validar_cuotas(cuotas)
    suma_cuadrados = math.fsum(s ** 2 for s in valores)
    return math.fsum(s ** 4 for s in valores) / suma_cuadrados ** 2


def entropia_shannon(cuotas: Iterable[float]) -> float:
    """Devuelve IE = -suma(s_i * ln(s_i)), con aporte cero para s_i = 0.

    Args:
        cuotas: Iterable de proporciones sujeto a ``validar_cuotas``.

    Returns:
        Entropía en nats (logaritmo natural), sin redondear.

    Raises:
        TypeError: Por cuotas no reales o no iterables.
        ValueError: Por cantidad, rango, finitud o suma de cuotas inválidos.
    """
    valores = validar_cuotas(cuotas)
    return math.fsum(-s * math.log(s) for s in valores if s > 0)


def entropia_normalizada(cuotas: Iterable[float]) -> float:
    """Devuelve IE / ln(N), usando todas las empresas, incluidas cuotas cero.

    Args:
        cuotas: Iterable de proporciones sujeto a ``validar_cuotas``.

    Returns:
        Entropía adimensional normalizada: 1 para cuotas iguales y 0 cuando
        una empresa concentra todas las ventas. N es la cantidad de cuotas.

    Raises:
        TypeError: Por cuotas no reales o no iterables.
        ValueError: Por cantidad, rango, finitud o suma de cuotas inválidos.
    """
    valores = validar_cuotas(cuotas)
    entropia = math.fsum(-s * math.log(s) for s in valores if s > 0)
    return entropia / math.log(len(valores))


def calcular_crk(cuotas, n, k):
    """Adaptador: N cuotas en proporciones y k entero [1,N]; devuelve float CRk.

    Valida cantidad exacta, finitud, rango y cierre sin normalizar. Propaga
    TypeError/ValueError de validar_cuotas y crk; la salida es una proporción.
    """
    return crk(validar_cuotas(cuotas, n), k)


def calcular_ihh_decimal(cuotas, n):
    """N proporciones válidas -> float IHH proporcional; TypeError/ValueError."""
    return ihh(validar_cuotas(cuotas, n))


def calcular_ihh_puntos(cuotas, n):
    """N proporciones válidas -> float IHH en puntos (×10000), sin redondeo.

    Propaga TypeError/ValueError por N, cuotas, finitud, rango o cierre inválidos.
    """
    return ihh_puntos(validar_cuotas(cuotas, n))


def calcular_id_garcia_alba(cuotas, n):
    """N proporciones válidas -> float ID adimensional; TypeError/ValueError."""
    return indice_dominancia(validar_cuotas(cuotas, n))


def calcular_entropia(cuotas, n):
    """N proporciones válidas -> float Shannon en nats; TypeError/ValueError."""
    return entropia_shannon(validar_cuotas(cuotas, n))


def calcular_entropia_normalizada(cuotas, n):
    """N proporciones válidas -> float IE/ln(N), adimensional, contando ceros.

    Propaga TypeError/ValueError por N o cuotas inválidos; no normaliza entradas.
    """
    return entropia_normalizada(validar_cuotas(cuotas, n))
