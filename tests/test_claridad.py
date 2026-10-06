"""Regresiones de claridad de la interfaz, sin cambiar cálculos ni controles.

AppTest inspecciona elementos y estado, incluidos hijos de desplegables cerrados.
Estas comprobaciones no sustituyen una revisión visual en un navegador.
"""

import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

import app as interfaz
import simulacion
from concentracion import indices


APP = Path(__file__).resolve().parents[1] / "app.py"


class TestResumenJustificacion(unittest.TestCase):
    def test_hasta_doce_empresas_conserva_desarrollo_completo(self):
        for n in (2, 4, 12):
            with self.subTest(n=n):
                cuotas = np.full(n, 1 / n)
                copia = cuotas.copy()
                completo = "Desarrollo completo recibido, sin reemplazar sus términos."
                resumen = interfaz.resumir_justificacion_ihh(
                    cuotas, "1.499,9999999999998", completo,
                )
                self.assertEqual(resumen, completo)
                np.testing.assert_array_equal(cuotas, copia)

    def test_mas_de_doce_resume_mayores_sin_recalcular_ihh(self):
        cuotas = np.array([.01, .05, .12, .02, .03, .04, .06,
                           .07, .08, .09, .10, .11, .22])
        cuotas = cuotas / cuotas.sum()
        copia = cuotas.copy()
        texto_ihh = "2.499,9999999999995"
        completo = "Todos los términos de la suma deben conservarse aparte."
        resumen = interfaz.resumir_justificacion_ihh(cuotas, texto_ihh, completo)
        self.assertIn("13 empresas", resumen)
        mayores = sorted((float(cuota) * 100 for cuota in cuotas), reverse=True)[:5]
        self.assertIn("[" + ", ".join(f"{v:.10g}" for v in mayores) + "] %", resumen)
        self.assertIn("todas las cuotas", resumen)
        self.assertIn(texto_ihh + " puntos", resumen)
        self.assertNotIn(completo, resumen)
        np.testing.assert_array_equal(cuotas, copia)


class TestClaridadInterfaz(unittest.TestCase):
    def setUp(self):
        self.parche = patch(
            "simulacion.simular_mercados_compactos",
            wraps=simulacion.simular_mercados_compactos,
        )
        self.motor = self.parche.start()
        self.addCleanup(self.parche.stop)
        self.app = AppTest.from_file(str(APP), default_timeout=30).run()
        self.assertFalse(self.app.exception)

    def simular(self):
        self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        return self.app.session_state["muestra"]

    def cambiar_caso(self, porcentajes):
        self.app.session_state["caso_base"] = pd.DataFrame({
            "Empresa": [f"Empresa {i + 1}" for i in range(len(porcentajes))],
            "Cuota (%)": np.asarray(porcentajes, dtype=np.float64),
        })
        self.app.session_state["editor_revision"] += 1
        self.app.run()
        self.assertFalse(self.app.exception)

    def textos_como_leerlo(self):
        return [m.value for m in self.app.markdown if "**Cómo leerlo:**" in m.value]

    def comprobar_ihh(self, respuesta):
        self.app.radio(key="respuesta_evaluacion").set_value(respuesta).run()
        self.app.button(key="comprobar_evaluacion").click().run()
        self.assertFalse(self.app.exception)
        return self.app.session_state["resultado_evaluacion"]

    def test_cuatro_ayudas_y_percentiles_de_la_muestra_sin_resimular(self):
        muestra = self.simular()
        self.cambiar_caso([40, 30, 20, 10])
        cuotas = (.4, .3, .2, .1)
        datos = {
            "CRk": (muestra.crk, indices.crk(cuotas, 2), "CR2"),
            "IHH": (muestra.ihh_puntos, indices.ihh_puntos(cuotas), "IHH"),
            "ID": (muestra.id, indices.indice_dominancia(cuotas), "ID"),
            "IE": (muestra.ie, indices.entropia_shannon(cuotas), "IE"),
        }
        for indicador, (serie, valor, nombre) in datos.items():
            with self.subTest(indicador=indicador):
                self.app.selectbox(key="indicador").select(indicador).run()
                self.assertFalse(self.app.exception)
                ayudas = [c.value for c in self.app.caption]
                self.assertEqual(ayudas.count(interfaz.AYUDAS_INDICADORES[indicador]), 1)
                for otro in interfaz.AYUDAS_INDICADORES:
                    if otro != indicador:
                        self.assertNotIn(interfaz.AYUDAS_INDICADORES[otro], ayudas)
                esperado = simulacion.percentil_empirico(serie, valor)
                textos = self.textos_como_leerlo()
                self.assertEqual(len(textos), 1)
                self.assertIn(f"**{esperado:.2f} %**", textos[0])
                self.assertIn(f"**{nombre}**", textos[0])
                self.assertIn("menor o igual", textos[0])
                self.assertIn("Se incluyen los empates", textos[0])
                contextos = [t for t in ayudas if "No es un umbral normativo" in t]
                self.assertEqual(len(contextos), 1)
                self.assertIn("mismo N", contextos[0])
                self.assertIn("Dirichlet(1,…,1)", contextos[0])
                explicaciones_ie = [i.value for i in self.app.info
                                    if "no significa mayor concentración" in i.value]
                self.assertEqual(len(explicaciones_ie), int(indicador == "IE"))
                self.assertIs(self.app.session_state["muestra"], muestra)
                self.assertEqual(self.motor.call_count, 1)

    def test_lectura_del_percentil_no_aparece_sin_caso_valido_o_muestra_vigente(self):
        self.assertEqual(self.textos_como_leerlo(), [])
        self.simular()
        self.assertEqual(len(self.textos_como_leerlo()), 1)
        self.cambiar_caso([40, 30, 20, 9])
        self.assertEqual(self.textos_como_leerlo(), [])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.cambiar_caso([40, 30, 20, 10])
        self.assertEqual(len(self.textos_como_leerlo()), 1)
        self.app.number_input(key="iteraciones").set_value(2000).run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertEqual(self.textos_como_leerlo(), [])
        self.assertEqual(self.motor.call_count, 1)

    def test_cr100_muestra_empates_exactos_y_explica_percentil_100(self):
        self.app.number_input(key="n").set_value(100).run()
        self.app.number_input(key="k").set_value(100).run()
        muestra = self.simular()
        np.testing.assert_array_equal(muestra.crk, np.ones(1000))
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [1.] * 100)
        self.assertEqual(indices.crk([.01] * 100, 100), 1.)
        self.assertEqual(simulacion.percentil_empirico(muestra.crk, 1.), 100.)
        self.assertIn("**100.00 %**", self.textos_como_leerlo()[0])
        textos = [e.value for tipo in (self.app.caption, self.app.info, self.app.markdown)
                  for e in tipo]
        mensaje = (
            "Cuando k=N, CRk es 100 % en todos los mercados. Por eso no distingue "
            "niveles de concentración. Todos los valores empatan y, con la "
            "definición utilizada, el percentil es 100 %."
        )
        self.assertEqual(textos.count(mensaje), 1)
        self.assertFalse(any("pueden separar empates matemáticos" in t for t in textos))
        figuras = [json.loads(c.proto.spec) for c in self.app.get("plotly_chart")]
        histograma = next(f for f in figuras if f["layout"]["title"]["text"].startswith("Distribución"))
        self.assertIn("Percentil: 100 %", histograma["layout"]["annotations"][0]["text"])

    def test_desarrollo_ihh_corto_visible_y_usa_percentil_propio(self):
        muestra = self.simular()
        self.cambiar_caso([40, 30, 20, 10])
        self.app.selectbox(key="indicador").select("IE").run()
        resultado = self.comprobar_ihh("Alta")
        self.assertEqual(resultado["percentil_ihh"],
                         simulacion.percentil_empirico(muestra.ihh_puntos, resultado["ihh_puntos"]))
        self.assertAlmostEqual(resultado["percentil_ihh"], 17.1)
        self.assertIn(resultado["justificacion"], [m.value for m in self.app.markdown])
        self.assertNotIn("Desarrollo completo y aportes al IHH",
                         [e.label for e in self.app.get("expander")])
        aportes = [d.value for d in self.app.dataframe if "Aporte al IHH (puntos)" in d.value.columns]
        self.assertEqual(len(aportes), 1)
        np.testing.assert_array_equal(aportes[0]["Aporte al IHH (puntos)"], resultado["aportes_ihh"])
        self.assertTrue(any("Acierto" in s.value for s in self.app.success))
        etiquetas = {m.label: m.value for m in self.app.metric}
        self.assertEqual(etiquetas["Percentil real del IHH en la muestra vigente"], "17.1 %")
        self.assertIn("**IE**", self.textos_como_leerlo()[0])

    def test_desarrollo_largo_preserva_calculos_y_tabla_en_desplegable(self):
        for n in (13, 100):
            with self.subTest(n=n):
                self.app.number_input(key="n").set_value(n).run()
                muestra = self.simular()
                resultado = self.comprobar_ihh("Baja")
                cuotas = indices.validar_cuotas([1 / n] * n)
                texto_ihh = interfaz._formatear_ihh_evaluacion(resultado["ihh_puntos"])
                resumen = interfaz.resumir_justificacion_ihh(cuotas, texto_ihh, resultado["justificacion"])
                self.assertIn(f"{n} empresas", resumen)
                self.assertIn(resumen, [m.value for m in self.app.markdown])
                desarrollos = [e for e in self.app.get("expander")
                               if e.label == "Desarrollo completo y aportes al IHH"]
                self.assertEqual(len(desarrollos), 1)
                detalle = desarrollos[0]
                self.assertIn(resultado["justificacion"], [m.value for m in detalle.markdown])
                self.assertEqual(len(detalle.dataframe), 1)
                tabla = detalle.dataframe[0].value
                self.assertEqual(len(tabla), n)
                np.testing.assert_array_equal(tabla["Cuota (%)"], resultado["cuotas_porcentaje"])
                np.testing.assert_array_equal(tabla["Aporte al IHH (puntos)"], resultado["aportes_ihh"])
                self.assertEqual(resultado["ihh_puntos"], indices.ihh_puntos(cuotas))
                esperado = simulacion.percentil_empirico(muestra.ihh_puntos, resultado["ihh_puntos"])
                self.assertEqual(resultado["percentil_ihh"], esperado)
                visibles = [m.value for m in self.app.markdown]
                self.assertTrue(any("**IHH calculado:** " + texto_ihh in t for t in visibles))
                self.assertTrue(any("**Intervalo:**" in t for t in visibles))
                self.assertTrue(any("Acierto" in s.value for s in self.app.success))
                self.assertIn("Percentil real del IHH en la muestra vigente", [m.label for m in self.app.metric])
                self.app.selectbox(key="indicador").select("ID").run()
                self.assertEqual(self.app.session_state["resultado_evaluacion"], resultado)
                self.assertIs(self.app.session_state["muestra"], muestra)

    def test_advertencia_breve_detalle_tecnico_y_aviso_de_volumen_alto(self):
        principales = [w.value for w in self.app.warning
                       if "Máximo permitido:" in w.value]
        self.assertEqual(len(principales), 1)
        maximo = f"{simulacion.MAX_ITERACIONES:,}".replace(",", ".")
        self.assertIn(maximo + " iteraciones", principales[0])
        self.assertIn("tiempo de respuesta", principales[0])
        self.assertIn("memoria y procesamiento", principales[0])
        self.assertNotIn(simulacion.ADVERTENCIA_RECURSOS, [w.value for w in self.app.warning])
        detalles = [e for e in self.app.get("expander") if e.label == "Detalles de rendimiento"]
        self.assertEqual(len(detalles), 1)
        self.assertIn(simulacion.ADVERTENCIA_RECURSOS, [m.value for m in detalles[0].markdown])
        self.app.number_input(key="iteraciones").set_value(50000).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(sum("Volumen alto" in w.value for w in self.app.warning), 1)
        self.assertEqual(self.motor.call_count, 0)


if __name__ == "__main__":
    unittest.main()
