"""Casos de representación que no requieren un navegador."""

import unittest

import numpy as np

from graficos import grafico_cuotas, histograma_indicador, crear_histograma_comparativo
from simulacion import simular_mercados_compactos, percentil_empirico
from indices import crk, ihh_puntos, indice_dominancia, entropia_shannon


class TestGraficos(unittest.TestCase):
    def test_ihh_compacto_en_puntos_y_valor_del_caso(self):
        figura = histograma_indicador([2500, 3000, 5000], "ihh", 3000, 66.666, ihh_en_puntos=True)
        self.assertEqual(list(figura.data[1].x), [3000, 3000])
        self.assertIn("3000", figura.data[1].name)
        self.assertIn("percentil", figura.data[1].name)
        self.assertLess(figura.layout.xaxis.range[1], 10000)
        self.assertEqual(sum(figura.data[0].y), 3)

    def test_cuotas_porcentajes_y_unidades(self):
        figura = grafico_cuotas([0.4, 0.3, 0.2, 0.1])
        np.testing.assert_allclose(figura.data[0].y, [40, 30, 20, 10])
        self.assertIn("%", figura.layout.yaxis.title.text)
        self.assertIn("Empresa", figura.layout.xaxis.title.text)
        self.assertTrue(figura.layout.showlegend)

    def test_histograma_agrega_y_conserva_frecuencias(self):
        muestras = np.linspace(0.1, 0.9, 10000)
        copia = muestras.copy()
        figura = histograma_indicador(muestras, "crk", caso=0.4, percentil=37.5, k=2)
        self.assertLessEqual(len(figura.data[0].x), 45)
        self.assertEqual(sum(figura.data[0].y), len(muestras))
        self.assertEqual(list(figura.data[1].x), [40, 40])
        self.assertIn("37.50", figura.data[1].name)
        self.assertIn("CR2", figura.layout.title.text)
        self.assertIn("%", figura.layout.xaxis.title.text)
        self.assertIn("mercados", figura.layout.yaxis.title.text)
        np.testing.assert_array_equal(muestras, copia)

    def test_casos_fuera_de_rango_visibles(self):
        for caso in (0.01, 1.0):
            with self.subTest(caso=caso):
                figura = histograma_indicador([0.2, 0.3, 0.4], "ihh", caso, 0 if caso < 0.2 else 100)
                minimo, maximo = figura.layout.xaxis.range
                self.assertLess(minimo, caso * 10000)
                self.assertGreater(maximo, caso * 10000)
                self.assertTrue(figura.layout.meta["fuera_de_rango"])
                self.assertIn("puntos", figura.layout.xaxis.title.text)

    def test_distribucion_constante_y_un_solo_mercado(self):
        for muestras in ([1] * 20, [1], [1, 1 + np.spacing(1.0), 1 - np.spacing(1.0)]):
            with self.subTest(muestras=muestras):
                figura = histograma_indicador(muestras, "crk", 1, 100, k=4)
                self.assertTrue(figura.layout.meta["constante"])
                self.assertEqual(len(figura.data[0].x), 1)
                self.assertEqual(sum(figura.data[0].y), len(muestras))
                self.assertGreater(figura.layout.xaxis.range[1], figura.layout.xaxis.range[0])

    def test_id_ie_y_histograma_sin_caso(self):
        for clave, unidad in (("id", "adimensional"), ("ie", "nats")):
            figura = histograma_indicador([0.2, 0.3], clave)
            self.assertIn(unidad, figura.layout.xaxis.title.text)
            self.assertEqual(len(figura.data), 1)

    def test_entradas_invalidas(self):
        for muestras, indicador, caso, percentil in (
            ([], "ihh", None, None), ([[1]], "ihh", None, None),
            ([np.nan], "ihh", None, None), ([1], "otro", None, None),
            ([1], "ihh", np.inf, None), ([1], "ihh", 1, 101),
        ):
            with self.subTest(muestras=muestras, indicador=indicador):
                with self.assertRaises(ValueError):
                    histograma_indicador(muestras, indicador, caso, percentil)

    def test_etiqueta_cuatro_indicadores_con_resultados_reales(self):
        resultado = simular_mercados_compactos(4, 2, 1000, 42)
        cuotas = [.4, .3, .2, .1]
        for clave, caso, valor, unidad in (
            ("crk", crk(cuotas, 2), "70", "%"),
            ("ihh", ihh_puntos(cuotas), "3.000", "puntos"),
            ("id", indice_dominancia(cuotas), "0,393333", "adimensional"),
            ("ie", entropia_shannon(cuotas), "1,279854", "nats"),
        ):
            with self.subTest(indicador=clave):
                serie = resultado.ihh_puntos if clave == "ihh" else resultado[clave]
                percentil = percentil_empirico(serie, caso)
                original = serie.copy()
                figura = histograma_indicador(serie, clave, caso, percentil, k=2, ihh_en_puntos=True)
                self.assertEqual(len(figura.layout.annotations), 1)
                texto_percentil = f"{percentil:.3f}".rstrip("0").rstrip(".").replace(".", ",")
                self.assertEqual(figura.layout.annotations[0].text,
                                 f"Caso: {valor} {unidad}<br>Percentil: {texto_percentil} %")
                self.assertEqual(figura.data[1].line.color, "#087F83")
                self.assertEqual(figura.data[1].line.dash, "dash")
                self.assertIn("percentil", figura.data[1].name)
                self.assertIn("Caso:", figura.data[1].hovertemplate)
                self.assertTrue(figura.layout.showlegend)
                np.testing.assert_array_equal(serie, original)
        self.assertEqual(histograma_indicador(resultado.ihh_puntos, "ihh", ihh_puntos(cuotas),
                         percentil_empirico(resultado.ihh_puntos, ihh_puntos(cuotas)),
                         ihh_en_puntos=True).layout.annotations[0].text,
                         "Caso: 3.000 puntos<br>Percentil: 17,1 %")

    def test_etiqueta_ihh_decimal_y_puntos_coinciden_sin_doble_escala(self):
        a = histograma_indicador([.25, .3, .5], "ihh", .3, 66.667)
        b = histograma_indicador([2500, 3000, 5000], "ihh", 3000, 66.667, ihh_en_puntos=True)
        self.assertEqual(a.layout.annotations[0].text, b.layout.annotations[0].text)
        self.assertEqual(a.layout.annotations[0].text, "Caso: 3.000 puntos<br>Percentil: 66,667 %")
        self.assertEqual(list(b.data[1].x), [3000, 3000])

    def test_etiquetas_extremos_cero_cien_y_constantes(self):
        for clave in ("crk", "ihh", "id", "ie"):
            for muestras, caso, esperado, fuera in (
                ([.2, .3, .4], .1, 0, True), ([.2, .3, .4], .5, 100, True),
                ([.3] * 20, .3, 100, False), ([.3], .1, 0, True),
            ):
                with self.subTest(indicador=clave, caso=caso, muestras=muestras):
                    percentil = percentil_empirico(muestras, caso)
                    self.assertEqual(percentil, esperado)
                    figura = histograma_indicador(muestras, clave, caso, percentil)
                    self.assertEqual(figura.layout.meta["fuera_de_rango"], fuera)
                    anotacion = figura.layout.annotations[0]
                    self.assertIn(f"Percentil: {esperado} %", anotacion.text)
                    self.assertEqual(anotacion.text.count("<br>"), 1)
                    self.assertEqual(anotacion.xref, "paper")
                    self.assertEqual(anotacion.yref, "paper")
                    self.assertTrue(0 <= anotacion.x <= 1)
                    self.assertTrue(0 <= anotacion.y <= 1)
                    self.assertIn(anotacion.xanchor, ("left", "center", "right"))
                    self.assertGreater(figura.layout.yaxis.range[1], max(figura.data[1].y))
                    if caso < min(muestras):
                        self.assertEqual(anotacion.xanchor, "left")
                    elif caso > max(muestras):
                        self.assertEqual(anotacion.xanchor, "right")

    def test_etiqueta_sin_caso_o_sin_percentil_no_inventa_datos(self):
        for caso, percentil in ((None, None), (None, 50), (.3, None)):
            figura = histograma_indicador([.2, .3, .4], "id", caso, percentil)
            self.assertFalse(figura.layout.annotations)
            self.assertEqual(len(figura.data), 1 if caso is None else 2)
        for caso in (np.nan, np.inf, -np.inf):
            with self.assertRaises(ValueError):
                histograma_indicador([.2, .3, .4], "id", caso, 50)

    def test_adaptador_reutiliza_percentil_actual_para_etiqueta(self):
        resultado = simular_mercados_compactos(4, 2, 1000, 42)
        figura = crear_histograma_comparativo(resultado, "IHH", ihh_puntos([.4,.3,.2,.1]),
                                             ihh_en_puntos=True)
        self.assertEqual(figura.layout.annotations[0].text, "Caso: 3.000 puntos<br>Percentil: 17,1 %")


if __name__ == "__main__":
    unittest.main()
