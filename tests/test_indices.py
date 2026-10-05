"""Pruebas ejecutables con unittest, sin dependencias externas."""

import math
import unittest

from indices import (
    crk,
    entropia_normalizada,
    entropia_shannon,
    ihh,
    ihh_puntos,
    indice_dominancia,
    validar_cuotas,
)


class TestIndices(unittest.TestCase):
    def test_exige_n_entero_y_exactamente_n_cuotas(self):
        self.assertEqual(validar_cuotas([0.5, 0.5], n=2), (0.5, 0.5))
        with self.assertRaises(ValueError):
            validar_cuotas([0.5, 0.5], n=4)
        for n in (True, False, 2.0, "2"):
            with self.assertRaises(TypeError):
                validar_cuotas([0.5, 0.5], n=n)
        for n in (1, 101):
            with self.assertRaises(ValueError):
                validar_cuotas([0.5, 0.5], n=n)

    def test_cuotas_iguales(self):
        for n in (2, 4, 100):
            with self.subTest(n=n):
                cuotas = [1 / n] * n
                self.assertAlmostEqual(crk(cuotas, 1), 1 / n)
                self.assertAlmostEqual(crk(cuotas, n), 1)
                self.assertAlmostEqual(ihh(cuotas), 1 / n)
                self.assertAlmostEqual(ihh_puntos(cuotas), 10000 / n)
                self.assertAlmostEqual(indice_dominancia(cuotas), 1 / n)
                self.assertAlmostEqual(entropia_shannon(cuotas), math.log(n))
                self.assertAlmostEqual(entropia_normalizada(cuotas), 1)

    def test_cuotas_40_30_20_10(self):
        cuotas = [0.4, 0.3, 0.2, 0.1]
        self.assertAlmostEqual(crk(cuotas, 2), 0.7, places=12)
        self.assertAlmostEqual(ihh(cuotas), 0.3, places=12)
        self.assertAlmostEqual(ihh_puntos(cuotas), 3000, places=9)
        self.assertAlmostEqual(indice_dominancia(cuotas), 0.3933333333, places=10)
        self.assertAlmostEqual(entropia_shannon(cuotas), 1.2798542258336676, places=12)
        self.assertAlmostEqual(entropia_normalizada(cuotas), 0.9232196723355078, places=12)

    def test_concentracion_total_y_cuotas_nulas(self):
        cuotas = [1, 0, 0, 0]
        self.assertEqual(validar_cuotas(cuotas), (1.0, 0.0, 0.0, 0.0))
        self.assertEqual(crk(cuotas, 1), 1)
        self.assertEqual(crk(cuotas, 4), 1)
        self.assertEqual(ihh(cuotas), 1)
        self.assertEqual(ihh_puntos(cuotas), 10000)
        self.assertEqual(indice_dominancia(cuotas), 1)
        self.assertEqual(entropia_shannon(cuotas), 0)
        self.assertEqual(entropia_normalizada(cuotas), 0)

    def test_crk_ordena_sin_mutar_entrada(self):
        cuotas = [0.1, 0.4, 0.2, 0.3]
        self.assertAlmostEqual(crk(cuotas, 2), 0.7)
        self.assertEqual(cuotas, [0.1, 0.4, 0.2, 0.3])

    def test_n_incluye_empresas_con_cuota_cero(self):
        self.assertAlmostEqual(entropia_normalizada([0.5, 0.5, 0, 0]), 0.5)

    def test_acepta_generadores(self):
        funciones = (
            (validar_cuotas, (0.4, 0.3, 0.2, 0.1)),
            (lambda cuotas: crk(cuotas, 2), 0.7),
            (ihh, 0.3),
            (ihh_puntos, 3000),
            (indice_dominancia, 0.3933333333333333),
            (entropia_shannon, 1.2798542258336676),
            (entropia_normalizada, 0.9232196723355078),
        )
        for funcion, esperado in funciones:
            with self.subTest(funcion=funcion):
                resultado = funcion(s for s in [0.4, 0.3, 0.2, 0.1])
                if isinstance(esperado, tuple):
                    self.assertEqual(resultado, esperado)
                else:
                    self.assertAlmostEqual(resultado, esperado)

    def test_tolerancia_absoluta_sin_normalizar_ni_redondear(self):
        for desviacion in (-5e-11, 5e-11):
            with self.subTest(desviacion=desviacion):
                cuotas = [0.5, 0.5 + desviacion]
                self.assertEqual(validar_cuotas(cuotas), tuple(cuotas))
                self.assertEqual(crk(cuotas, 2), math.fsum(cuotas))
                self.assertEqual(ihh(cuotas), math.fsum(s ** 2 for s in cuotas))
                self.assertNotEqual(crk(cuotas, 2), 1)
        for desviacion in (-2e-10, 2e-10, 5e-10):
            with self.subTest(desviacion=desviacion):
                with self.assertRaises(ValueError):
                    validar_cuotas([0.5, 0.5 + desviacion])

    def test_cuotas_invalidas_en_todas_las_funciones(self):
        casos = (
            ([], ValueError),
            ([1], ValueError),
            ([1 / 101] * 101, ValueError),
            ([-0.1, 1.1], ValueError),
            ([-1e-12, 1], ValueError),
            ([1 + 1e-12, 0], ValueError),
            ([1 + 5e-11, 0], ValueError),
            ([float("nan"), 0.5], ValueError),
            ([float("inf"), 0], ValueError),
            ([float("-inf"), 1], ValueError),
            ([10 ** 1000, 0], ValueError),
            ([0.4, 0.4], ValueError),
            ([0, 0], ValueError),
            ([40, 30, 20, 10], ValueError),
            (["0.5", 0.5], TypeError),
            ([True, 0], TypeError),
            ([0.5 + 0j, 0.5], TypeError),
            ([None, 1], TypeError),
            (None, TypeError),
            (1, TypeError),
            ("01", TypeError),
            (b"01", TypeError),
        )
        funciones = (
            validar_cuotas,
            lambda cuotas: crk(cuotas, 1),
            ihh,
            ihh_puntos,
            indice_dominancia,
            entropia_shannon,
            entropia_normalizada,
        )
        for cuotas, error in casos:
            for funcion in funciones:
                with self.subTest(cuotas=cuotas, funcion=funcion):
                    with self.assertRaises(error):
                        funcion(cuotas)

    def test_k_invalido(self):
        for k in (0, -1, 5):
            with self.subTest(k=k):
                with self.assertRaises(ValueError):
                    crk([0.4, 0.3, 0.2, 0.1], k)
        for k in (2.0, 1.5, True, False, "2", None):
            with self.subTest(k=k):
                with self.assertRaises(TypeError):
                    crk([0.4, 0.3, 0.2, 0.1], k)


if __name__ == "__main__":
    unittest.main()
