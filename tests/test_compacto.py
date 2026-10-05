"""Unidades explícitas, cierre de lotes y generador directo de referencia."""

import unittest
from unittest.mock import patch

import numpy as np

from concentracion import indices, simulacion
from concentracion.simulacion import simular_mercados_compactos, simular_mercados
from medir_rendimiento import referencia_completa


class TestCompacto(unittest.TestCase):
    def test_concordancia_completa_lotes_y_api_clasica(self):
        for n, k, cantidad in ((2, 2, 1), (4, 2, 1000), (100, 50, 4101)):
            with self.subTest(n=n, k=k):
                completo = referencia_completa(n, k, cantidad, 42)
                clasico = simular_mercados(n, k, cantidad, 42)
                for lote in (1, 127, 4096):
                    compacto = simular_mercados_compactos(n, k, cantidad, 42, tamano_lote=lote)
                    for key in ("crk", "ihh_puntos", "id", "ie"):
                        np.testing.assert_allclose(getattr(compacto, key), getattr(completo, key), atol=2e-11 if key == "ihh_puntos" else 2e-14, rtol=0)
                    np.testing.assert_array_equal(compacto.ihh_puntos, clasico["ihh"] * 10000)
                    self.assertEqual(compacto.configuracion["unidades"]["ihh"], "puntos")
                    self.assertEqual(sum(getattr(compacto, key).nbytes for key in ("crk", "ihh_puntos", "id", "ie")), 32 * cantidad)
                    self.assertFalse(hasattr(compacto, "cuotas"))
                    with self.assertRaises(KeyError):
                        compacto["ihh"]

    def test_referencia_171_sin_forzar_datos(self):
        r = simular_mercados_compactos(4, 2, 1000, 42)
        self.assertEqual(np.count_nonzero(r.ihh_puntos <= indices.ihh_puntos([.4, .3, .2, .1])), 171)
        self.assertAlmostEqual(simulacion.percentil_empirico(r.ihh_puntos, indices.ihh_puntos([.4, .3, .2, .1])), 17.1)

    def test_valida_todas_las_filas_y_maximo_sin_acumular(self):
        cantidades = []
        original = simulacion._validar_filas

        def validar(cuotas, n, cantidad):
            original(cuotas, n, cantidad)
            np.testing.assert_allclose(cuotas.sum(axis=1), 1, atol=1e-10, rtol=0)
            cantidades.append(cantidad)

        with patch.object(simulacion, "_validar_filas", side_effect=validar):
            r = simular_mercados_compactos(100, 50, 100000, 42)
        self.assertEqual(sum(cantidades), 100000)
        self.assertLessEqual(max(cantidades), 4096)
        self.assertEqual(r.ihh_puntos.size, 100000)
        self.assertEqual(len(r.__dict__), 5)

    def test_parametros_y_lotes_invalidos_antes_de_generar(self):
        for cambio, error in (({"n": True}, TypeError), ({"k": False}, TypeError),
                               ({"iteraciones": True}, TypeError), ({"semilla": False}, TypeError),
                               ({"n": 101}, ValueError), ({"n": 1}, ValueError),
                               ({"k": 5}, ValueError), ({"iteraciones": 100001}, ValueError),
                               ({"tamano_lote": True}, TypeError), ({"tamano_lote": 0}, ValueError),
                               ({"tamano_lote": 4097}, ValueError)):
            parametros = dict(n=4, k=2, iteraciones=1, semilla=42)
            parametros.update(cambio)
            with self.subTest(cambio=cambio), patch.object(simulacion.np.random, "default_rng") as rng:
                with self.assertRaises(error):
                    simular_mercados_compactos(**parametros)
                rng.assert_not_called()

    def test_rechaza_cuota_superior_uno_aunque_cierre(self):
        cuotas = np.array([[1 + 5e-11, 0.]])
        with patch.object(simulacion.np.random, "default_rng") as rng:
            rng.return_value.dirichlet.return_value = cuotas
            with self.assertRaises(RuntimeError):
                simular_mercados_compactos(2, 1, 1, 42)
        self.assertEqual(cuotas[0, 0], 1 + 5e-11)


if __name__ == "__main__":
    unittest.main()
