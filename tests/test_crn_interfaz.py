"""Regresiones de los consumidores de CR_N; no calculan otro CR o percentil.

AppTest comprueba el flujo Python de Streamlit y su figura serializada. Estas
pruebas no sustituyen una comprobación visual en un navegador.
"""

import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from app import csv_muestra
from graficos import crear_histograma_comparativo, histograma_indicador
from indices import crk
import simulacion


APP = Path(__file__).resolve().parents[1] / "app.py"


def _casos_validos(n):
    iguales = np.full(n, 1.0 / n)
    desigual = {2: [0.7, 0.3], 4: [0.4, 0.3, 0.2, 0.1]}.get(n)
    if desigual is None:
        desigual = [0.5] + [0.5 / (n - 1)] * (n - 1)
    return iguales, np.asarray(desigual, dtype=np.float64)


class TestConsumidoresCRN(unittest.TestCase):
    def test_csv_consumen_crn_exacto_de_ambos_motores(self):
        for n in (2, 4, 100):
            for motor in (simulacion.simular_mercados,
                          simulacion.simular_mercados_compactos):
                with self.subTest(n=n, motor=motor.__name__):
                    muestra = motor(n, n, 1000, 42)
                    originales = muestra.crk.copy()
                    tabla = pd.read_csv(io.BytesIO(csv_muestra(muestra)),
                                        float_precision="round_trip")
                    np.testing.assert_array_equal(muestra.crk, np.ones(1000))
                    np.testing.assert_array_equal(tabla.crk_porcentaje,
                                                  np.full(1000, 100.0))
                    self.assertEqual(len(tabla), 1000)
                    self.assertTrue((tabla.n == n).all())
                    self.assertTrue((tabla.k == n).all())
                    np.testing.assert_array_equal(muestra.crk, originales)

    def test_histograma_y_adaptador_consumen_valores_y_percentil_corregidos(self):
        for n in (2, 4, 100):
            for motor in (simulacion.simular_mercados,
                          simulacion.simular_mercados_compactos):
                muestra = motor(n, n, 1000, 42)
                for cuotas in _casos_validos(n):
                    with self.subTest(n=n, motor=motor.__name__, cuotas=cuotas):
                        caso = crk(cuotas, n)
                        percentil = simulacion.percentil_empirico(muestra.crk, caso)
                        self.assertEqual(caso, 1.0)
                        self.assertEqual(percentil, 100.0)
                        originales = muestra.crk.copy()
                        figuras = (
                            histograma_indicador(muestra.crk, "crk", caso,
                                                 percentil, k=n),
                            crear_histograma_comparativo(muestra, "CRk", caso),
                        )
                        for figura in figuras:
                            self.assertTrue(figura.layout.meta["constante"])
                            self.assertFalse(figura.layout.meta["fuera_de_rango"])
                            self.assertEqual(len(figura.data[0].x), 1)
                            self.assertEqual(sum(figura.data[0].y), 1000)
                            self.assertEqual(list(figura.data[1].x), [100.0, 100.0])
                            self.assertEqual(figura.layout.annotations[0].text,
                                             "Caso: 100 %<br>Percentil: 100 %")
                        np.testing.assert_array_equal(muestra.crk, originales)

    def test_app_n100_usa_compacto_y_muestra_percentil_cien(self):
        with patch("simulacion.simular_mercados_compactos",
                   wraps=simulacion.simular_mercados_compactos) as motor:
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            self.assertFalse(app.exception)
            app.number_input(key="n").set_value(100).run()
            app.number_input(key="k").set_value(100).run()
            app.number_input(key="iteraciones").set_value(1000).run()
            app.number_input(key="semilla").set_value(42).run()
            app.button(key="iguales").click().run()
            self.assertFalse(app.exception)
            app.button(key="simular").click().run()
            self.assertFalse(app.exception)
            motor.assert_called_once()
            muestra = app.session_state["muestra"]
            self.assertIsInstance(muestra, simulacion.ResultadoSimulacionCompacto)
            self.assertFalse(hasattr(muestra, "cuotas"))
            self.assertEqual(muestra.configuracion["n"], 100)
            self.assertEqual(muestra.configuracion["k"], 100)
            self.assertEqual(muestra.configuracion["iteraciones"], 1000)
            self.assertEqual(muestra.configuracion["semilla"], 42)
            np.testing.assert_array_equal(muestra.crk, np.ones(1000))
            np.testing.assert_array_equal(app.session_state["caso_base"]["Cuota (%)"],
                                          np.ones(100))
            metricas = {metrica.label: metrica.value for metrica in app.metric}
            self.assertEqual(metricas["CR100"], "100.00 %")
            self.assertEqual(metricas["Percentil empírico del caso"], "100.00 %")
            figuras = [json.loads(grafico.proto.spec)
                       for grafico in app.get("plotly_chart")]
            histograma = next(figura for figura in figuras
                              if figura["layout"]["title"]["text"].startswith("Distribución"))
            self.assertEqual(histograma["layout"]["annotations"][0]["text"],
                             "Caso: 100 %<br>Percentil: 100 %")
            self.assertTrue(histograma["layout"]["meta"]["constante"])
            self.assertFalse(histograma["layout"]["meta"]["fuera_de_rango"])
            self.assertTrue(app.session_state["comparacion_habilitada"])


if __name__ == "__main__":
    unittest.main()
