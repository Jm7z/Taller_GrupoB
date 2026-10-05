"""Benchmark reproducible: python medir_rendimiento.py --salida rendimiento.json.

Referencia completa solo para medir/concordar, no para la interfaz. Tiempos con
perf_counter sin trazado, cinco repeticiones tras calentamiento, resultados
descartados entre llamadas. Medición de memoria separada con tracemalloc:
asignaciones nuevas trazadas, no RSS; excluye bibliotecas previamente cargadas.
"""

import argparse
import gc
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import tracemalloc
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np

from concentracion.simulacion import (
    ResultadoSimulacionCompacto, _calcular_indicadores, _validar_filas,
    simular_mercados_compactos,
)


def referencia_completa(n, k, iteraciones, semilla):
    """Referencia experimental de una sola matriz para parámetros ya validados."""
    cuotas = np.random.default_rng(semilla).dirichlet(np.ones(n), size=iteraciones)
    _validar_filas(cuotas, n, iteraciones)
    series = _calcular_indicadores(cuotas, k)
    series["ihh"] *= 10000
    return ResultadoSimulacionCompacto(
        series["crk"], series["ihh"], series["id"], series["ie"], {},
    )


def medir():
    """Mide N=100,k=50,semilla=42 para 1000/10000/100000, ambos motores."""
    mediciones = []
    for nombre, motor in (("compacto", simular_mercados_compactos),
                           ("referencia_completa", referencia_completa)):
        motor(100, 50, 1000, 42)
        for cantidad in (1000, 10000, 100000):
            tiempos = []
            for _ in range(5):
                gc.collect()
                inicio = time.perf_counter()
                resultado = motor(100, 50, cantidad, 42)
                tiempos.append(time.perf_counter() - inicio)
                del resultado
            gc.collect()
            tracemalloc.start()
            try:
                resultado = motor(100, 50, cantidad, 42)
                _, pico = tracemalloc.get_traced_memory()
                retenidos = sum(getattr(resultado, key).nbytes for key in ("crk", "ihh_puntos", "id", "ie"))
                del resultado
            finally:
                tracemalloc.stop()
            mediciones.append({
                "motor": nombre, "n": 100, "k": 50, "iteraciones": cantidad,
                "semilla": 42, "repeticiones": 5,
                "segundos": tiempos, "segundos_mediana": statistics.median(tiempos),
                "pico_bytes_trazados": pico, "bytes_arrays": retenidos,
            })
    return {
        "fecha_santiago": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        "python": sys.version, "numpy": np.__version__,
        "sistema": platform.platform(), "procesador": platform.processor(),
        "metodo": "5 tiempos sin tracemalloc tras calentamiento; pico separado; no RSS ni latencia web",
        "mediciones": mediciones,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", default="rendimiento.json")
    args = parser.parse_args()
    resultados = medir()
    Path(args.salida).write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    for fila in resultados["mediciones"]:
        print(f"{fila['motor']}: M={fila['iteraciones']}, "
              f"mediana={fila['segundos_mediana']:.6f} s, "
              f"pico trazado={fila['pico_bytes_trazados']/2**20:.3f} MiB")
