"""Regresiones de CR_N=1 después de validar, sin alterar el percentil general."""

import math
import unittest
from unittest.mock import patch

import numpy as np

import indices as adaptador_indices
import simulacion as adaptador_simulacion
from concentracion import indices, simulacion


def repartos_validos(n):
    """Iguales, desiguales y cierres tolerados: entradas sin corregir ni redondear."""
    iguales = np.full(n, 1 / n)
    desigual = (np.array([.7, .3]) if n == 2 else
                np.array([.4, .3, .2, .1]) if n == 4 else
                np.random.default_rng(19).dirichlet(np.ones(n)))
    filas = [iguales, desigual]
    for desviacion in (-5e-11, 5e-11):
        tolerada = iguales.copy()
        tolerada[0] += desviacion
        filas.append(tolerada)
    return np.asarray(filas)


class TestIdentidadCRN(unittest.TestCase):
    def test_escalar_y_adaptadores_exactos_despues_de_validar(self):
        for n in (2, 4, 100):
            for cuotas in repartos_validos(n):
                with self.subTest(n=n, cuotas=cuotas):
                    original = cuotas.copy()
                    self.assertEqual(indices.validar_cuotas(cuotas, n), tuple(cuotas))
                    self.assertEqual(indices.crk(cuotas, n), 1.0)
                    self.assertIsInstance(indices.crk(cuotas, n), float)
                    self.assertEqual(indices.calcular_crk(cuotas, n, n), 1.0)
                    self.assertEqual(adaptador_indices.calcular_crk(cuotas, n, n), 1.0)
                    np.testing.assert_array_equal(cuotas, original)

    def test_vectorizado_exacto_sin_modificar_entradas(self):
        for n in (2, 4, 100):
            with self.subTest(n=n):
                cuotas = repartos_validos(n)
                original = cuotas.copy()
                cuotas.setflags(write=False)
                for modulo in (simulacion, adaptador_simulacion):
                    valores = modulo.calcular_indicadores_vectorizados(cuotas, n, n)
                    np.testing.assert_array_equal(valores["crk"], np.ones(len(cuotas)))
                    self.assertEqual(valores["crk"].dtype, np.float64)
                np.testing.assert_array_equal(cuotas, original)

    def test_ambos_motores_lotes_compactacion_y_percentil_exactos(self):
        for n in (2, 4, 100):
            with self.subTest(n=n):
                completo = adaptador_simulacion.simular_mercados(n, n, 1000, 42)
                np.testing.assert_array_equal(completo.crk, np.ones(1000))
                np.testing.assert_array_equal(
                    simulacion.compactar_resultado(completo).crk, np.ones(1000))
                for lote in (1, 127, 4096):
                    compacto = adaptador_simulacion.simular_mercados_compactos(
                        n, n, 1000, 42, tamano_lote=lote)
                    np.testing.assert_array_equal(compacto.crk, np.ones(1000))
                    self.assertFalse(hasattr(compacto, "cuotas"))
                    for cuotas in repartos_validos(n):
                        caso = indices.crk(cuotas, n)
                        for resultado in (completo, compacto):
                            self.assertEqual(simulacion.percentil_empirico(resultado.crk, caso), 100.0)
                            self.assertEqual(adaptador_simulacion.calcular_percentil_empirico(
                                resultado.crk, caso), 100.0)

    def test_no_omite_validacion_escalar_cuando_k_es_n(self):
        invalidas = ([.4, .4], [-.1, 1.1], [np.nan, .5], [np.inf, 0],
                     [1 + 5e-11, 0], [.5, .5 + 2e-10])
        for cuotas in invalidas:
            with self.subTest(cuotas=cuotas):
                for funcion in (lambda: indices.crk(cuotas, 2),
                                lambda: indices.calcular_crk(cuotas, 2, 2),
                                lambda: adaptador_indices.calcular_crk(cuotas, 2, 2)):
                    with self.assertRaises(ValueError):
                        funcion()
        for cuotas in ([True, 0], [".5", .5], [None, 1]):
            with self.subTest(cuotas=cuotas), self.assertRaises(TypeError):
                indices.calcular_crk(cuotas, 2, 2)
        with self.assertRaises(ValueError):
            indices.calcular_crk([.5, .5], 4, 4)
        for k in (2.0, True):
            with self.subTest(k=k), self.assertRaises(TypeError):
                indices.crk([.5, .5], k)

    def test_no_omite_validacion_vectorizada_cuando_k_es_n(self):
        for fila in ([.4, .4], [-.1, 1.1], [np.nan, .5], [np.inf, 0],
                     [1 + 5e-11, 0], [.5, .5 + 2e-10]):
            cuotas = np.array([[.5, .5], fila])
            with self.subTest(fila=fila), self.assertRaises(ValueError):
                simulacion.calcular_indicadores_vectorizados(cuotas, 2, 2)
        for cuotas in (np.empty((0, 2)), [[.5, .5, 0]], [.5, .5]):
            with self.subTest(cuotas=cuotas), self.assertRaises(ValueError):
                simulacion.calcular_indicadores_vectorizados(cuotas, 2, 2)
        with self.assertRaises(TypeError):
            simulacion.calcular_indicadores_vectorizados([[True, False]], 2, 2)
        for k in (2.0, True):
            with self.subTest(k=k), self.assertRaises(TypeError):
                simulacion.calcular_indicadores_vectorizados([[.5, .5]], 2, k)

    def test_ambos_motores_rechazan_filas_invalidas_antes_de_identidad(self):
        for motor in (simulacion.simular_mercados, simulacion.simular_mercados_compactos):
            for fila in ([.4, .4], [-.1, 1.1], [np.nan, .5], [np.inf, 0],
                         [1 + 5e-11, 0], [.5, .5 + 2e-10]):
                cuotas = np.array([[.5, .5], fila])
                with self.subTest(motor=motor.__name__, fila=fila):
                    with patch.object(simulacion.np.random, "default_rng") as crear:
                        crear.return_value.dirichlet.return_value = cuotas
                        with self.assertRaises(RuntimeError):
                            motor(2, 2, 2, 42)
            with patch.object(simulacion.np.random, "default_rng") as crear:
                with self.assertRaises(ValueError):
                    motor(1, 1, 1000, 42)
                crear.assert_not_called()

    def test_k_menor_n_conserva_sumas_sin_redondear(self):
        for n in (2, 4, 100):
            cuotas = repartos_validos(n)
            for k in (1, n - 1):
                with self.subTest(n=n, k=k):
                    for fila in cuotas:
                        self.assertEqual(indices.crk(fila, k),
                                         math.fsum(sorted(fila, reverse=True)[:k]))
                    trabajo = cuotas.copy()
                    trabajo.partition(n - k, axis=1)
                    esperado = np.sum(trabajo[:, n - k:], axis=1, dtype=np.float64)
                    resultado = simulacion.calcular_indicadores_vectorizados(cuotas, n, k)
                    np.testing.assert_array_equal(resultado["crk"], esperado)
        self.assertEqual(indices.crk([.4, .3, .2, .1], 2), .7)
        muestra = simulacion.simular_mercados_compactos(4, 2, 1000, 42)
        self.assertEqual(simulacion.percentil_empirico(muestra.crk, .7), 100.0 * (234 / 1000))

    def test_identidad_no_cambia_cuotas_generadas_ni_otros_indicadores(self):
        for n in (2, 4, 100):
            with self.subTest(n=n):
                completo = simulacion.simular_mercados(n, n, 1000, 42)
                anterior = simulacion.simular_mercados(n, n - 1, 1000, 42)
                esperado = np.random.default_rng(42).dirichlet(np.ones(n), size=1000)
                np.testing.assert_array_equal(completo.cuotas, esperado)
                np.testing.assert_array_equal(completo.cuotas, anterior.cuotas)
                for clave in ("ihh", "id", "ie"):
                    np.testing.assert_array_equal(completo[clave], anterior[clave])
                for lote in (1, 127, 4096):
                    a = simulacion.simular_mercados_compactos(n, n, 1000, 42, tamano_lote=lote)
                    b = simulacion.simular_mercados_compactos(n, n - 1, 1000, 42, tamano_lote=lote)
                    for clave in ("ihh_puntos", "id", "ie"):
                        np.testing.assert_array_equal(getattr(a, clave), getattr(b, clave))
                caso = simulacion.generar_caso_aleatorio(n, n, 42)
                caso_parcial = simulacion.generar_caso_aleatorio(n, n - 1, 42)
                self.assertEqual(caso["indicadores"]["crk"], 1.0)
                np.testing.assert_array_equal(caso["cuotas"], caso_parcial["cuotas"])
                for clave in ("ihh", "id", "ie"):
                    self.assertEqual(caso["indicadores"][clave], caso_parcial["indicadores"][clave])

    def test_percentil_general_sigue_comparando_sin_tolerancia(self):
        valores = [np.nextafter(1.0, -np.inf), 1.0, np.nextafter(1.0, np.inf)]
        self.assertEqual(simulacion.percentil_empirico(valores, 1.0), 100.0 * (2 / 3))
        self.assertEqual(simulacion.percentil_empirico([1.0] * 1000, 1.0), 100.0)


if __name__ == "__main__":
    unittest.main()
