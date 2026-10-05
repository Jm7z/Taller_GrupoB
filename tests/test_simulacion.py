"""Pruebas del motor y procedimiento optativo de rendimiento.

Pruebas: python -m unittest discover -s tests -v
Medición (desde la raíz del proyecto):
python -c "import sys; sys.path.insert(0, 'tests'); from test_simulacion import medir_rendimiento; print(medir_rendimiento())"
"""

import gc
import statistics
import time
import tracemalloc
import unittest
from unittest.mock import patch

import numpy as np

import indices
import simulacion
from simulacion import (
    INDICADORES,
    MAX_ITERACIONES,
    TAMANO_LOTE,
    generar_caso_aleatorio,
    percentil_empirico,
    simular_mercados,
)


class TestSimulacion(unittest.TestCase):
    def test_dimensiones_configuracion_y_unidades(self):
        for n, k, cantidad in ((2, 1, 1), (4, 4, 37), (100, 100, 11)):
            with self.subTest(n=n, k=k, cantidad=cantidad):
                resultado = simular_mercados(n, k, cantidad, semilla=42)
                self.assertEqual(set(resultado), set(INDICADORES) | {"configuracion"})
                for nombre in INDICADORES:
                    self.assertEqual(resultado[nombre].shape, (cantidad,))
                    self.assertEqual(resultado[nombre].dtype, np.float64)
                    self.assertTrue(np.all(np.isfinite(resultado[nombre])))
                    self.assertTrue(resultado[nombre].flags.owndata)
                config = resultado["configuracion"]
                for nombre, esperado in (("n", n), ("k", k), ("iteraciones", cantidad),
                                         ("semilla", 42), ("alpha", 1.0), ("flujo", 0),
                                         ("atol", 1e-10), ("rtol", 0.0)):
                    self.assertEqual(config[nombre], esperado)
                self.assertEqual(config["version_numpy"], np.__version__)
                self.assertEqual(config["unidades"]["ie"], "nats")
                if k == n:
                    np.testing.assert_allclose(resultado["crk"], 1, atol=1e-10, rtol=0)

    def test_cierre_de_todas_las_filas_y_cuotas_de_api_completa(self):
        original = simulacion._validar_filas
        cantidades = []

        def verificar(cuotas, n, cantidad):
            self.assertEqual(cuotas.shape[1], n)
            self.assertTrue(np.all(cuotas >= 0))
            self.assertTrue(np.all(cuotas <= 1))
            self.assertTrue(np.all(np.isfinite(cuotas)))
            np.testing.assert_allclose(cuotas.sum(axis=1), 1, atol=1e-10, rtol=0)
            cantidades.append(cuotas.shape[0])
            original(cuotas, n, cantidad)

        with patch.object(simulacion, "_validar_filas", side_effect=verificar):
            resultado = simular_mercados(100, 2, 2 * TAMANO_LOTE + 3, semilla=8)
        self.assertEqual(cantidades, [TAMANO_LOTE, TAMANO_LOTE, 3])
        self.assertNotIn("cuotas", resultado)
        self.assertEqual(resultado.cuotas.shape, (sum(cantidades), 100))
        np.testing.assert_allclose(resultado.cuotas.sum(axis=1), 1, atol=1e-10, rtol=0)
        self.assertEqual(sum(resultado[n].nbytes for n in INDICADORES), 32 * sum(cantidades))

    def test_reproducibilidad_y_semillas_distintas(self):
        primero = simular_mercados(8, 3, 50, semilla=42)
        segundo = simular_mercados(8, 3, 50, semilla=42)
        diferente = simular_mercados(8, 3, 50, semilla=43)
        for nombre in INDICADORES:
            np.testing.assert_array_equal(primero[nombre], segundo[nombre])
            self.assertFalse(np.array_equal(primero[nombre], diferente[nombre]))
        self.assertEqual(primero["configuracion"], segundo["configuracion"])
        segundo["ihh"][0] = -1
        self.assertGreater(primero["ihh"][0], 0)

    def test_repeticion_con_entropia_efectiva_sin_semilla(self):
        primero = simular_mercados(4, 2, 15)
        segundo = simular_mercados(4, 2, 15, semilla=primero["configuracion"]["entropia_semilla"])
        self.assertIsNone(primero["configuracion"]["semilla"])
        for nombre in INDICADORES:
            np.testing.assert_array_equal(primero[nombre], segundo[nombre])
        caso = generar_caso_aleatorio(4, 2)
        repetido = generar_caso_aleatorio(4, 2, semilla=caso["configuracion"]["entropia_semilla"])
        np.testing.assert_array_equal(caso["cuotas"], repetido["cuotas"])

    def test_iteraciones_por_defecto(self):
        resultado = simular_mercados(4, 2, semilla=0)
        self.assertEqual(resultado["configuracion"]["iteraciones"], 1000)
        for nombre in INDICADORES:
            self.assertEqual(resultado[nombre].size, 1000)

    def test_no_modifica_estado_aleatorio_global(self):
        estado = np.random.get_state()
        simular_mercados(4, 2, 10, semilla=42)
        generar_caso_aleatorio(4, 2, semilla=42)
        posterior = np.random.get_state()
        self.assertEqual(estado[0], posterior[0])
        np.testing.assert_array_equal(estado[1], posterior[1])
        self.assertEqual(estado[2:], posterior[2:])

    def test_concordancia_mercados_simulados_con_indices(self):
        for n, k in ((2, 1), (4, 2), (100, 1), (100, 99), (100, 100)):
            with self.subTest(n=n, k=k):
                cuotas = np.random.default_rng(81).dirichlet(np.ones(n), size=37)
                resultado = simular_mercados(n, k, 37, semilla=81)
                esperado = {
                    "crk": [indices.crk(fila, k) for fila in cuotas],
                    "ihh": [indices.ihh(fila) for fila in cuotas],
                    "id": [indices.indice_dominancia(fila) for fila in cuotas],
                    "ie": [indices.entropia_shannon(fila) for fila in cuotas],
                }
                for nombre in INDICADORES:
                    np.testing.assert_allclose(resultado[nombre], esperado[nombre], atol=2e-14, rtol=0)
                np.testing.assert_allclose(resultado["ihh"] * 10000,
                                           [indices.ihh_puntos(f) for f in cuotas], atol=2e-11, rtol=0)
                np.testing.assert_allclose(resultado["ie"] / np.log(n),
                                           [indices.entropia_normalizada(f) for f in cuotas], atol=2e-14, rtol=0)

    def test_concordancia_casos_base_y_ceros_sin_mutacion(self):
        cuotas = np.array([[0.25] * 4, [0.4, 0.3, 0.2, 0.1], [1, 0, 0, 0], [0.5, 0.5, 0, 0]])
        copia = cuotas.copy()
        with np.errstate(divide="raise", invalid="raise"):
            resultado = simulacion._calcular_indicadores(cuotas, 2)
        for posicion, fila in enumerate(cuotas):
            esperado = (indices.crk(fila, 2), indices.ihh(fila),
                        indices.indice_dominancia(fila), indices.entropia_shannon(fila))
            for nombre, valor in zip(INDICADORES, esperado):
                self.assertAlmostEqual(resultado[nombre][posicion], valor, places=14)
        self.assertAlmostEqual(resultado["crk"][1], 0.7)
        self.assertAlmostEqual(resultado["ihh"][1] * 10000, 3000)
        self.assertAlmostEqual(resultado["id"][1], 0.3933333333, places=10)
        np.testing.assert_array_equal(cuotas, copia)

    def test_caso_reproducible_cierre_y_generador_independiente(self):
        caso = generar_caso_aleatorio(4, 2, semilla=42)
        self.assertEqual(caso["cuotas"].shape, (4,))
        indices.validar_cuotas(caso["cuotas"])
        self.assertEqual(caso["configuracion"]["flujo"], 1)
        simular_mercados(4, 2, 23, semilla=42)
        posterior = generar_caso_aleatorio(4, 2, semilla=42)
        np.testing.assert_array_equal(caso["cuotas"], posterior["cuotas"])
        self.assertEqual(caso["indicadores"], posterior["indicadores"])
        primera_simulacion = np.random.default_rng(42).dirichlet(np.ones(4))
        self.assertFalse(np.array_equal(caso["cuotas"], primera_simulacion))
        self.assertEqual(caso["indicadores"]["crk"], indices.crk(caso["cuotas"], 2))
        self.assertEqual(caso["indicadores"]["ihh"], indices.ihh(caso["cuotas"]))
        self.assertEqual(caso["indicadores"]["id"], indices.indice_dominancia(caso["cuotas"]))
        self.assertEqual(caso["indicadores"]["ie"], indices.entropia_shannon(caso["cuotas"]))

    def test_prefijo_reproducible_entre_lotes(self):
        corto = simular_mercados(4, 2, TAMANO_LOTE + 3, semilla=7)
        largo = simular_mercados(4, 2, TAMANO_LOTE + 11, semilla=7)
        for nombre in INDICADORES:
            np.testing.assert_array_equal(corto[nombre], largo[nombre][:TAMANO_LOTE + 3])

    def test_limites_y_enteros_numpy(self):
        resultado = simular_mercados(np.int64(2), np.int64(1), np.int64(1), np.int64(0))
        self.assertEqual(resultado["crk"].shape, (1,))
        resultado = simular_mercados(2, 2, MAX_ITERACIONES, semilla=0)
        self.assertEqual(resultado["ihh"].size, MAX_ITERACIONES)

    def test_parametros_invalidos_antes_de_crear_generador(self):
        casos = (
            ({"n": 1}, ValueError), ({"n": 101}, ValueError),
            ({"k": 0}, ValueError), ({"k": 5}, ValueError),
            ({"iteraciones": 0}, ValueError), ({"iteraciones": -1}, ValueError),
            ({"iteraciones": MAX_ITERACIONES + 1}, ValueError),
            ({"semilla": -1}, ValueError),
        )
        for nombre in ("n", "k", "iteraciones", "semilla"):
            for valor in (True, np.bool_(False), 2.0, "2", [2], np.random.default_rng(1)):
                casos += (({nombre: valor}, TypeError),)
        for nombre in ("n", "k", "iteraciones"):
            casos += (({nombre: None}, TypeError),)
        for cambio, error in casos:
            parametros = dict(n=4, k=2, iteraciones=10, semilla=1)
            parametros.update(cambio)
            with self.subTest(cambio=cambio):
                with patch.object(simulacion.np.random, "default_rng") as crear:
                    with self.assertRaises(error):
                        simular_mercados(**parametros)
                    crear.assert_not_called()
                if "iteraciones" not in cambio:
                    parametros.pop("iteraciones")
                    with self.assertRaises(error):
                        generar_caso_aleatorio(**parametros)

    def test_rechaza_cualquier_fila_generada_invalida_sin_reparar(self):
        for fila in ([0.4, 0.4], [-0.1, 1.1], [np.nan, 0.5], [np.inf, 0],
                     [0.5, 0.5 + 5e-10], [1 + 5e-11, 0]):
            for posicion in (0, 1, 2):
                cuotas = np.array([[0.5, 0.5]] * 3)
                cuotas[posicion] = fila
                with self.subTest(fila=fila, posicion=posicion):
                    with patch.object(simulacion.np.random, "default_rng") as crear:
                        crear.return_value.dirichlet.return_value = cuotas
                        with self.assertRaises(RuntimeError):
                            simular_mercados(2, 1, 3, semilla=1)
        with patch.object(simulacion.np.random, "default_rng") as crear:
            crear.return_value.dirichlet.return_value = np.array([[0.5, 0.4]])
            with self.assertRaises(RuntimeError):
                generar_caso_aleatorio(2, 1, semilla=1)

    def test_rechaza_dimensiones_incorrectas_del_generador(self):
        for cuotas in (np.array([[0.5, 0.5]]), np.empty((0, 2)),
                       np.array([0.5, 0.5]), np.full((3, 3), 1 / 3)):
            with self.subTest(forma=cuotas.shape):
                with patch.object(simulacion.np.random, "default_rng") as crear:
                    crear.return_value.dirichlet.return_value = cuotas
                    with self.assertRaises(RuntimeError):
                        simular_mercados(2, 1, 3, semilla=1)
        with patch.object(simulacion.np.random, "default_rng") as crear:
            crear.return_value.dirichlet.return_value = np.full((2, 2), 0.5)
            with self.assertRaises(RuntimeError):
                generar_caso_aleatorio(2, 1, semilla=1)

    def test_percentiles_incluyen_empates_y_extremos(self):
        muestras = np.array([1, 2, 2, 3], dtype=np.float64)
        copia = muestras.copy()
        for caso, esperado in ((0, 0), (1, 25), (2, 75), (2.5, 75), (3, 100), (4, 100)):
            self.assertEqual(percentil_empirico(muestras, caso), esperado)
        self.assertEqual(percentil_empirico([2, 2, 2], 2), 100)
        self.assertEqual(percentil_empirico([2], 1), 0)
        self.assertEqual(percentil_empirico([0, 0.5, 1, 1], 1), 100)
        np.testing.assert_array_equal(muestras, copia)

    def test_percentiles_invalidos(self):
        for muestras in ([], [[1, 2]], 1, [np.nan], [np.inf]):
            with self.subTest(muestras=muestras):
                with self.assertRaises(ValueError):
                    percentil_empirico(muestras, 1)
        for muestras in ([True], [True, 1], ["1"], [1 + 0j], [None]):
            with self.subTest(muestras=muestras):
                with self.assertRaises(TypeError):
                    percentil_empirico(muestras, 1)
        for caso in (True, np.bool_(True), "1", None, 1 + 0j):
            with self.subTest(caso=caso):
                with self.assertRaises(TypeError):
                    percentil_empirico([1, 2], caso)
        for caso in (np.nan, np.inf, -np.inf, 10 ** 1000):
            with self.subTest(caso=caso):
                with self.assertRaises(ValueError):
                    percentil_empirico([1, 2], caso)


def medir_rendimiento():
    """Mide N=100, k=50, semilla=42; 5 tiempos y una medición de memoria.

    Devuelve tiempos sin tracemalloc (mínimo/mediana/máximo), bytes retenidos
    por los cuatro arrays y pico de asignaciones trazadas con tracemalloc.
    El pico NO es el RSS total del proceso ni incluye el intérprete/NumPy
    cargados antes de iniciar el trazado. No acumula resultados entre llamadas.
    No impone pruebas de velocidad dependientes del equipo.
    """
    simular_mercados(100, 50, 1000, semilla=42)  # Calentamiento.
    mediciones = []
    for cantidad in (1000, 10_000, 50_000, MAX_ITERACIONES):
        tiempos = []
        for _ in range(5):
            gc.collect()
            inicio = time.perf_counter()
            resultado = simular_mercados(100, 50, cantidad, semilla=42)
            tiempos.append(time.perf_counter() - inicio)
            del resultado
        gc.collect()
        tracemalloc.start()
        try:
            resultado = simular_mercados(100, 50, cantidad, semilla=42)
            _, pico = tracemalloc.get_traced_memory()
            bytes_arrays = sum(resultado[nombre].nbytes for nombre in INDICADORES)
            del resultado
        finally:
            tracemalloc.stop()
        mediciones.append({
            "n": 100, "k": 50, "iteraciones": cantidad,
            "segundos_min": min(tiempos), "segundos_mediana": statistics.median(tiempos),
            "segundos_max": max(tiempos), "bytes_arrays": bytes_arrays,
            "pico_bytes_trazados": pico, "version_numpy": np.__version__,
        })
    return mediciones


if __name__ == "__main__":
    unittest.main()
