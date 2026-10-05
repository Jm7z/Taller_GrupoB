"""Fronteras, retroalimentación y percentil de IHH sin estado de interfaz."""

import unittest

import numpy as np

import indices
from evaluacion import clasificar_ihh, evaluar_ihh, evaluar_complementaria, PREGUNTAS_COMPLEMENTARIAS
from simulacion import percentil_empirico, simular_mercados


class TestEvaluacion(unittest.TestCase):
    def test_muestra_compacta_en_puntos_sin_multiplicacion_doble(self):
        from concentracion.simulacion import simular_mercados_compactos
        muestra = simular_mercados_compactos(4, 2, 1000, 42)
        resultado = evaluar_ihh([.4, .3, .2, .1], "Alta", muestra.ihh_puntos, unidad_muestra="puntos")
        self.assertEqual(resultado["menores_o_iguales"], 171)
        self.assertAlmostEqual(resultado["percentil_ihh"], 17.1)
        self.assertAlmostEqual(resultado["ihh_puntos"], 3000)
        with self.assertRaises(ValueError):
            evaluar_ihh([.5, .5], "Alta", [5000], unidad_muestra="inventada")

    def test_preguntas_complementarias_sin_umbrales(self):
        for indicador, pregunta in PREGUNTAS_COMPLEMENTARIAS.items():
            self.assertTrue(evaluar_complementaria(indicador, pregunta["correcta"])["acierto"])
            incorrecta = next(opcion for opcion in pregunta["opciones"] if opcion != pregunta["correcta"])
            self.assertFalse(evaluar_complementaria(indicador, incorrecta)["acierto"])
        with self.assertRaises(ValueError):
            evaluar_complementaria("IHH", "Baja")
        with self.assertRaises(ValueError):
            evaluar_complementaria("IE", None)

    def test_fronteras_exactas_y_valores_adyacentes_sin_redondear(self):
        casos = (
            (0, "Baja"), (np.nextafter(1500.0, -np.inf), "Baja"),
            (1500, "Moderada"), (np.nextafter(1500.0, np.inf), "Moderada"),
            (np.nextafter(2500.0, -np.inf), "Moderada"),
            (2500, "Alta"), (np.nextafter(2500.0, np.inf), "Alta"),
            (10000, "Alta"),
        )
        for puntos, categoria in casos:
            with self.subTest(puntos=puntos):
                self.assertEqual(clasificar_ihh(puntos), categoria)

    def test_caso_40_30_20_10_acierto_error_y_aportes(self):
        cuotas = [0.4, 0.3, 0.2, 0.1]
        muestra = simular_mercados(4, 2, 1000, 42)
        copia = muestra["ihh"].copy()
        resultado = evaluar_ihh(cuotas, "Alta", muestra["ihh"])
        self.assertTrue(resultado["acierto"])
        self.assertEqual(resultado["clasificacion"], "Alta")
        self.assertAlmostEqual(resultado["ihh_puntos"], 3000)
        self.assertEqual(resultado["intervalo"], "IHH ≥ 2500 puntos")
        self.assertEqual(resultado["cuotas_porcentaje"], (40, 30, 20, 10))
        np.testing.assert_allclose(resultado["aportes_ihh"], [1600, 900, 400, 100])
        self.assertEqual(resultado["percentil_ihh"], percentil_empirico(muestra["ihh"], indices.ihh(cuotas)))
        self.assertEqual(resultado["menores_o_iguales"], np.count_nonzero(muestra["ihh"] <= indices.ihh(cuotas)))
        self.assertIn("menor o igual", resultado["explicacion_percentil"])
        self.assertIn("no determina automáticamente", resultado["alcance"])
        np.testing.assert_array_equal(muestra["ihh"], copia)
        self.assertFalse(any(isinstance(valor, np.ndarray) for valor in resultado.values()))
        self.assertFalse(evaluar_ihh(cuotas, "Baja", muestra["ihh"])["acierto"])

    def test_percentil_incluye_todos_los_empates(self):
        cuotas = [0.4, 0.3, 0.2, 0.1]
        valor = indices.ihh(cuotas)
        muestra = np.array([0.25, valor, valor, 0.5])
        resultado = evaluar_ihh(cuotas, "Alta", muestra)
        self.assertEqual(resultado["percentil_ihh"], 75)
        self.assertEqual(resultado["menores_o_iguales"], 3)
        self.assertEqual(resultado["total_simulaciones"], 4)
        self.assertEqual(evaluar_ihh(cuotas, "Alta", [valor] * 3)["percentil_ihh"], 100)

    def test_percentil_no_determina_clasificacion(self):
        bajo = evaluar_ihh([0.25] * 4, "Alta", [0.5, 0.75])
        alto = evaluar_ihh([0.25] * 4, "Alta", [0.25, 0.25])
        self.assertEqual((bajo["percentil_ihh"], alto["percentil_ihh"]), (0, 100))
        self.assertEqual(bajo["clasificacion"], alto["clasificacion"])
        self.assertEqual(bajo["ihh_puntos"], 2500)

    def test_puntos_invalidos(self):
        for valor in (True, np.bool_(False), "1500", None, 1 + 2j):
            with self.subTest(valor=valor):
                with self.assertRaises(TypeError):
                    clasificar_ihh(valor)
        for valor in (-1, 10001, np.nan, np.inf, -np.inf, 10 ** 1000):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    clasificar_ihh(valor)

    def test_cuotas_respuestas_y_muestras_invalidas(self):
        for cuotas in ([0.5, 0.4], [-0.1, 1.1], [np.nan, 0.5], [1]):
            with self.assertRaises(ValueError):
                evaluar_ihh(cuotas, "Alta", [0.5])
        for respuesta in ("", "alta", "Ninguna"):
            with self.assertRaises(ValueError):
                evaluar_ihh([0.5, 0.5], respuesta, [0.5])
        with self.assertRaises(TypeError):
            evaluar_ihh([0.5, 0.5], None, [0.5])
        for muestra in ([], [[0.5]], [np.nan], [np.inf], [-0.1], [1.01], [3000]):
            with self.subTest(muestra=muestra):
                with self.assertRaises(ValueError):
                    evaluar_ihh([0.5, 0.5], "Alta", muestra)
        for muestra in ([True], ["0.5"], [1j]):
            with self.assertRaises(TypeError):
                evaluar_ihh([0.5, 0.5], "Alta", muestra)


if __name__ == "__main__":
    unittest.main()
