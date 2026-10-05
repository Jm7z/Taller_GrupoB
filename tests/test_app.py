"""Flujo con AppTest de Streamlit y verificaciones de porcentajes/CSV.

AppTest no edita las celdas del data_editor: las pruebas de casos reemplazan
su tabla base. La edición real en el navegador se comprueba por separado.
"""

import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from app import (csv_caso, csv_muestra, validar_porcentajes,
                 _formatear_ihh_evaluacion, _mensaje_error_ihh)
import simulacion
from simulacion import percentil_empirico


APP = Path(__file__).resolve().parents[1] / "app.py"


class TestDatosInterfaz(unittest.TestCase):
    def test_seis_errores_ihh_desde_cuotas_actuales(self):
        from evaluacion import evaluar_ihh
        ejemplos = (([.1] * 10, "Baja", "1.000"), ([.2] * 5, "Moderada", "2.000"),
                    ([.4, .3, .2, .1], "Alta", "3.000"))
        seis = 0
        for cuotas, correcta, puntos in ejemplos:
            for respuesta in ("Baja", "Moderada", "Alta"):
                if respuesta == correcta:
                    continue
                with self.subTest(correcta=correcta, respuesta=respuesta):
                    resultado = evaluar_ihh(cuotas, respuesta, [.1, .2, .4])
                    copia = dict(resultado)
                    texto = _mensaje_error_ihh(resultado)
                    self.assertIn(f"Seleccionaste {respuesta.lower()}", texto)
                    self.assertIn(f"El caso tiene {puntos} puntos", texto)
                    self.assertIn(f"concentración {correcta.lower()}", texto)
                    self.assertIn("no pertenece a ese intervalo", texto)
                    self.assertEqual(resultado, copia)
                    limites = {"Baja": "IHH < 1.500 puntos", "Moderada": "1.500 ≤ IHH < 2.500 puntos",
                               "Alta": "IHH ≥ 2.500 puntos"}
                    self.assertIn(limites[respuesta], texto)
                    self.assertIn(limites[correcta], texto)
                    seis += 1
        self.assertEqual(seis, 6)

    def test_feedback_precision_de_fronteras_y_adyacentes(self):
        from evaluacion import clasificar_ihh
        for frontera in (1500., 2500.):
            for valor in (np.nextafter(frontera, -np.inf), frontera, np.nextafter(frontera, np.inf)):
                with self.subTest(valor=valor):
                    texto = _formatear_ihh_evaluacion(valor)
                    recuperado = float(texto.replace(".", "").replace(",", "."))
                    self.assertEqual(recuperado, valor)
                    self.assertEqual(clasificar_ihh(recuperado), clasificar_ihh(valor))
                    correcta = clasificar_ihh(valor)
                    for respuesta in ("Baja", "Moderada", "Alta"):
                        if respuesta != correcta:
                            mensaje = _mensaje_error_ihh({"respuesta": respuesta,
                                "clasificacion": correcta, "ihh_puntos": valor})
                            self.assertIn(texto + " puntos", mensaje)
                            self.assertIn("concentración " + correcta.lower(), mensaje)

    def test_csv_compacto_y_caso_preservan_unidades_y_precision(self):
        r = simulacion.simular_mercados_compactos(4, 2, 1000, 42)
        tabla = pd.read_csv(io.BytesIO(csv_muestra(r)), float_precision="round_trip")
        self.assertEqual(len(tabla), 1000)
        np.testing.assert_array_equal(tabla.ihh_puntos, r.ihh_puntos)
        np.testing.assert_array_equal(tabla.crk_porcentaje, r.crk * 100)
        np.testing.assert_array_equal(tabla.ie_nats, r.ie)
        self.assertTrue((tabla.semilla == 42).all())
        self.assertTrue((tabla.version_numpy == np.__version__).all())
        porcentajes = [40.12345678901234, 29.87654321098766, 20, 10]
        original = pd.DataFrame({"Empresa": ["A", "B", "C", "D"], "Cuota (%)": porcentajes})
        exportado = pd.read_csv(io.BytesIO(csv_caso(original)), float_precision="round_trip")
        np.testing.assert_array_equal(exportado["Cuota (%)"], porcentajes)
        self.assertEqual(exportado.Empresa.tolist(), ["A", "B", "C", "D"])
        with self.assertRaises(ValueError):
            csv_caso(pd.DataFrame({"Empresa": ["A", "B"], "Cuota (%)": [45, 45]}))

    def test_convierte_porcentajes_sin_normalizacion(self):
        self.assertEqual(validar_porcentajes([40, 30, 20, 10], 4), (0.4, 0.3, 0.2, 0.1))
        for caso in ([40, 30, 20, 9], [101, 0], [-1, 101], [np.nan, 100], [np.inf, 0], [10 ** 1000, 0]):
            with self.subTest(caso=caso):
                with self.assertRaises(ValueError):
                    validar_porcentajes(caso, len(caso))
        for caso in ([True, 0], [None, 100], ["50", 50]):
            with self.assertRaises(TypeError):
                validar_porcentajes(caso, 2)
        with self.assertRaises(ValueError):
            validar_porcentajes([50, 50], 4)

    def test_csv_unidades_configuracion_y_todas_las_filas(self):
        muestra = simulacion.simular_mercados(4, 2, 7, 42)
        tabla = pd.read_csv(io.BytesIO(csv_muestra(muestra)))
        self.assertEqual(len(tabla), 7)
        np.testing.assert_allclose(tabla.crk_porcentaje, muestra["crk"] * 100)
        np.testing.assert_allclose(tabla.ihh_puntos, muestra["ihh"] * 10000)
        np.testing.assert_allclose(tabla.ie_normalizada, muestra["ie"] / np.log(4))
        self.assertTrue((tabla.n == 4).all())
        self.assertTrue((tabla.k == 2).all())
        self.assertTrue((tabla.semilla_efectiva == 42).all())


class TestFlujoInterfaz(unittest.TestCase):
    def setUp(self):
        self.parche = patch("simulacion.simular_mercados_compactos", wraps=simulacion.simular_mercados_compactos)
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

    def test_arranque_sin_simular_y_evaluacion_bloqueada(self):
        self.assertEqual(self.motor.call_count, 0)
        self.assertIsNone(self.app.session_state["muestra"])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.assertFalse(self.app.session_state["evaluacion_habilitada"])
        self.assertIsNone(self.app.radio(key="respuesta_evaluacion").value)
        self.assertTrue(self.app.button(key="comprobar_evaluacion").disabled)
        self.assertEqual(self.app.number_input(key="iteraciones").value, 1000)

    def test_etiquetas_cuatro_graficos_y_caso_invalido_sin_resimular(self):
        muestra = self.simular()
        self.app.button(key="ejemplo").click().run()
        for clave, unidad in (("CRk", "%"), ("IHH", "puntos"),
                             ("ID", "adimensional"), ("IE", "nats")):
            with self.subTest(indicador=clave):
                self.app.selectbox(key="indicador").select(clave).run()
                self.assertFalse(self.app.exception)
                figuras = [json.loads(c.proto.spec) for c in self.app.get("plotly_chart")]
                histograma = next(f for f in figuras if f["layout"]["title"]["text"].startswith("Distribución"))
                texto = histograma["layout"]["annotations"][0]["text"]
                self.assertIn(unidad, texto)
                self.assertIn("Percentil:", texto)
                if clave == "IHH":
                    self.assertEqual(texto, "Caso: 3.000 puntos<br>Percentil: 17,1 %")
                self.assertIs(self.app.session_state["muestra"], muestra)
                self.assertEqual(self.motor.call_count, 1)
        self.cambiar_caso([40, 30, 20, 9])
        histograma = json.loads(self.app.get("plotly_chart")[0].proto.spec)
        self.assertFalse(histograma["layout"].get("annotations"))
        self.assertEqual(len(histograma["data"]), 1)
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertEqual(self.motor.call_count, 1)

    def test_indicador_y_caso_reutilizan_muestra(self):
        muestra = self.simular()
        self.assertTrue(self.app.session_state["comparacion_habilitada"])
        self.app.selectbox(key="indicador").select("IE").run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.number_input(key="k").disabled)
        self.cambiar_caso([40, 30, 20, 10])
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertEqual(self.motor.call_count, 1)
        self.assertTrue(self.app.session_state["comparacion_habilitada"])
        etiquetas = {m.label: m.value for m in self.app.metric}
        self.assertEqual(etiquetas["IHH (puntos)"], "3000.00")

    def test_cada_parametro_invalida_sin_simular_automaticamente(self):
        for clave, valor in (("n", 5), ("k", 3), ("iteraciones", 2000), ("semilla", 43)):
            with self.subTest(clave=clave):
                muestra = self.simular()
                llamadas = self.motor.call_count
                self.app.number_input(key=clave).set_value(valor).run()
                self.assertFalse(self.app.exception)
                self.assertTrue(self.app.session_state["muestra_desactualizada"])
                self.assertFalse(self.app.session_state["comparacion_habilitada"])
                self.assertIs(self.app.session_state["muestra"], muestra)
                self.assertEqual(self.motor.call_count, llamadas)
                self.assertNotIn("Percentil empírico del caso", [m.label for m in self.app.metric])
        self.simular()
        self.app.checkbox(key="usar_semilla").uncheck().run()
        self.assertTrue(self.app.session_state["muestra_desactualizada"])

    def test_requiere_nueva_simulacion_aunque_se_restaure_configuracion(self):
        self.simular()
        self.app.number_input(key="iteraciones").set_value(2000).run()
        self.app.number_input(key="iteraciones").set_value(1000).run()
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.simular()
        self.assertTrue(self.app.session_state["comparacion_habilitada"])
        self.assertFalse(self.app.session_state["muestra_desactualizada"])

    def test_n_actualiza_tabla_y_acota_k(self):
        self.app.number_input(key="k").set_value(4).run()
        self.app.number_input(key="n").set_value(2).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.number_input(key="k").value, 2)
        self.assertEqual(len(self.app.session_state["caso_base"]), 2)
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [50, 50])

    def test_casos_aleatorios_varian_y_boton_cuotas_iguales(self):
        muestra = self.simular()
        self.app.button(key="aleatorio").click().run()
        primero = self.app.session_state["caso_base"]["Cuota (%)"].to_numpy(copy=True)
        self.app.button(key="aleatorio").click().run()
        segundo = self.app.session_state["caso_base"]["Cuota (%)"].to_numpy(copy=True)
        self.assertFalse(self.app.exception)
        self.assertFalse(np.array_equal(primero, segundo))
        self.assertEqual(self.motor.call_count, 1)
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertTrue(self.app.session_state["comparacion_habilitada"])
        self.app.button(key="iguales").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [25] * 4)
        self.assertEqual(self.motor.call_count, 1)

    def test_caso_invalido_bloquea_comparacion_y_muestra_diferencia(self):
        self.simular()
        self.cambiar_caso([20, 20, 20, 20])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.assertTrue(any("Falta 20 %" in aviso.value for aviso in self.app.warning))
        self.assertTrue(any("No se normaliza" in error.value for error in self.app.error))
        self.assertEqual(self.motor.call_count, 1)
        self.assertNotIn("Percentil empírico del caso", [m.label for m in self.app.metric])

    def test_crn_constante_y_caso_fuera_de_rango(self):
        self.app.number_input(key="k").set_value(4).run()
        self.simular()
        self.assertTrue(any("Distribución constante" in aviso.value for aviso in self.app.info))
        self.app.selectbox(key="indicador").select("IHH").run()
        self.cambiar_caso([100, 0, 0, 0])
        self.assertTrue(any("fuera del rango" in aviso.value for aviso in self.app.info))
        self.assertTrue(self.app.session_state["comparacion_habilitada"])
        self.assertEqual(self.motor.call_count, 1)

    def comprobar(self, respuesta="Alta"):
        self.app.radio(key="respuesta_evaluacion").set_value(respuesta).run()
        self.app.button(key="comprobar_evaluacion").click().run()
        self.assertFalse(self.app.exception)
        return self.app.session_state["resultado_evaluacion"]

    def test_evaluacion_sin_preseleccion_y_feedback_acierto_error(self):
        self.simular()
        self.cambiar_caso([40, 30, 20, 10])
        self.assertIsNone(self.app.radio(key="respuesta_evaluacion").value)
        self.assertTrue(self.app.button(key="comprobar_evaluacion").disabled)
        resultado = self.comprobar("Baja")
        self.assertFalse(resultado["acierto"])
        self.assertTrue(any("Error en la respuesta" in error.value for error in self.app.error))
        self.assertTrue(any("Seleccionaste baja" in e.value and "3.000 puntos" in e.value
                            and "IHH < 1.500 puntos" in e.value
                            and "IHH ≥ 2.500 puntos" in e.value for e in self.app.error))
        resultado = self.comprobar("Moderada")
        self.assertTrue(any("Seleccionaste moderada" in e.value
                            and "límite superior excluido" in e.value for e in self.app.error))
        resultado = self.comprobar("Alta")
        self.assertTrue(resultado["acierto"])
        self.assertAlmostEqual(resultado["ihh_puntos"], 3000)
        self.assertTrue(any("Acierto" in aviso.value for aviso in self.app.success))

    def test_evaluacion_usa_ihh_con_cualquier_grafico(self):
        muestra = self.simular()
        self.cambiar_caso([40, 30, 20, 10])
        resultado = self.comprobar()
        esperado = percentil_empirico(muestra.ihh_puntos, 10000 * sum(s ** 2 for s in [0.4, 0.3, 0.2, 0.1]))
        self.assertEqual(resultado["percentil_ihh"], esperado)
        for indicador in ("CRk", "IHH", "ID", "IE"):
            self.app.selectbox(key="indicador").select(indicador).run()
            self.assertFalse(self.app.exception)
            self.assertEqual(self.app.session_state["resultado_evaluacion"], resultado)
            self.assertIs(self.app.session_state["muestra"], muestra)
            self.assertEqual(self.motor.call_count, 1)
            etiquetas = {m.label: m.value for m in self.app.metric}
            self.assertEqual(etiquetas["Percentil real del IHH en la muestra vigente"], f"{esperado:.6g} %")

    def test_cambiar_respuesta_limpia_feedback_antes_de_comprobar(self):
        self.simular()
        self.comprobar()
        self.app.radio(key="respuesta_evaluacion").set_value("Moderada").run()
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertNotIn("Percentil real del IHH en la muestra vigente", [m.label for m in self.app.metric])

    def test_cambiar_caso_invalido_o_valido_limpia_y_bloquea(self):
        self.simular()
        self.comprobar()
        self.cambiar_caso([20] * 4)
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertIsNone(self.app.radio(key="respuesta_evaluacion").value)
        self.assertFalse(self.app.session_state["evaluacion_habilitada"])
        self.assertTrue(self.app.button(key="comprobar_evaluacion").disabled)
        self.cambiar_caso([40, 30, 20, 10])
        self.assertTrue(self.app.session_state["evaluacion_habilitada"])
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.comprobar()
        self.app.button(key="iguales").click().run()
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.comprobar()
        self.app.button(key="aleatorio").click().run()
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertEqual(self.motor.call_count, 1)

    def test_nueva_simulacion_identica_y_muestra_desactualizada_limpian(self):
        self.simular()
        self.comprobar()
        self.simular()  # Mismos parámetros y semilla: igualmente es una nueva muestra.
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertIsNone(self.app.radio(key="respuesta_evaluacion").value)
        self.comprobar()
        self.app.number_input(key="iteraciones").set_value(2000).run()
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertFalse(self.app.session_state["evaluacion_habilitada"])
        self.assertTrue(self.app.button(key="comprobar_evaluacion").disabled)
        self.app.number_input(key="iteraciones").set_value(1000).run()
        self.assertFalse(self.app.session_state["evaluacion_habilitada"])
        self.simular()
        self.assertTrue(self.app.session_state["evaluacion_habilitada"])
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])

    def test_k_vacio_bloquea_y_limpia_evaluacion(self):
        self.simular()
        self.comprobar()
        self.app.number_input(key="k").set_value(None).run()
        self.assertFalse(self.app.exception)
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertFalse(self.app.session_state["evaluacion_habilitada"])
        self.app.number_input(key="k").set_value(2).run()
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertTrue(self.app.button(key="comprobar_evaluacion").disabled)

    def test_botones_ejemplo_tiempo_y_muestra_compacta(self):
        muestra = self.simular()
        duracion = self.app.session_state["duracion_simulacion"]
        self.assertIsInstance(muestra, simulacion.ResultadoSimulacionCompacto)
        self.assertGreaterEqual(duracion, 0)
        self.assertFalse(self.app.session_state["simulacion_en_curso"])
        self.app.button(key="ejemplo").click().run()
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [40, 30, 20, 10])
        r = self.comprobar()
        self.assertEqual(r["menores_o_iguales"], 171)
        self.assertAlmostEqual(r["percentil_ihh"], 17.1)
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertEqual(self.app.session_state["duracion_simulacion"], duracion)
        self.assertEqual(self.motor.call_count, 1)

    def test_descargas_se_preparan_solo_bajo_demanda(self):
        # Streamlit recibe callables; no convierte DataFrames a CSV en los reruns.
        with patch.object(pd.DataFrame, "to_csv", side_effect=AssertionError("CSV preparado anticipadamente")):
            muestra = self.simular()
            self.app.button(key="ejemplo").click().run()
            self.assertFalse(self.app.exception)
            self.app.selectbox(key="indicador").select("IE").run()
            self.assertFalse(self.app.exception)
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertEqual(self.motor.call_count, 1)

    def test_controles_vacios_no_fallan_y_bloquean(self):
        for clave in ("n", "iteraciones", "semilla"):
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            app.button(key="simular").click().run()
            app.number_input(key=clave).set_value(None).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.session_state["evaluacion_habilitada"])
            self.assertTrue(app.session_state["muestra_desactualizada"])

    def test_complementarias_sin_preseleccion_y_limpieza(self):
        from concentracion.evaluacion import PREGUNTAS_COMPLEMENTARIAS
        self.simular()
        for indicador, pregunta in PREGUNTAS_COMPLEMENTARIAS.items():
            self.assertIsNone(self.app.radio(key=f"respuesta_{indicador}").value)
            self.app.radio(key=f"respuesta_{indicador}").set_value(pregunta["correcta"]).run()
            self.app.button(key=f"comprobar_{indicador}").click().run()
            self.assertTrue(self.app.session_state[f"feedback_{indicador}"]["acierto"])
            incorrecta = next(o for o in pregunta["opciones"] if o != pregunta["correcta"])
            self.app.radio(key=f"respuesta_{indicador}").set_value(incorrecta).run()
            self.assertIsNone(self.app.session_state[f"feedback_{indicador}"])
        self.app.button(key="ejemplo").click().run()
        for indicador in PREGUNTAS_COMPLEMENTARIAS:
            self.assertIsNone(self.app.radio(key=f"respuesta_{indicador}").value)
            self.assertIsNone(self.app.session_state[f"feedback_{indicador}"])

    def test_extremos_n_una_iteracion_monopolio_y_cierre_90(self):
        for n in (2, 100):
            self.app.number_input(key="n").set_value(n).run()
            self.app.number_input(key="k").set_value(n).run()
            self.app.number_input(key="iteraciones").set_value(1).run()
            self.simular()
            self.assertTrue(self.app.session_state["evaluacion_habilitada"])
            self.assertTrue(any("Distribución constante" in e.value for e in self.app.info))
            self.cambiar_caso([100] + [0] * (n - 1))
            self.assertEqual(self.comprobar()["ihh_puntos"], 10000)
            self.cambiar_caso([90] + [0] * (n - 1))
            self.assertFalse(self.app.session_state["evaluacion_habilitada"])
            self.assertTrue(any("Falta 10 %" in a.value for a in self.app.warning))

    def test_maximo_ui_advertencia_y_no_acumula_muestras(self):
        anterior = self.simular()
        self.app.number_input(key="n").set_value(100).run()
        self.app.number_input(key="k").set_value(50).run()
        self.app.number_input(key="iteraciones").set_value(100000).run()
        self.assertTrue(any("Volumen alto" in aviso.value for aviso in self.app.warning))
        nueva = self.simular()
        self.assertIsNot(nueva, anterior)
        self.assertEqual(nueva.ihh_puntos.size, 100000)
        self.assertFalse(hasattr(nueva, "cuotas"))
        self.assertEqual(self.motor.call_count, 2)

    def test_muestra_de_version_anterior_se_bloquea_sin_confundir_unidades(self):
        anterior = simulacion.simular_mercados(4, 2, 1000, 42)
        self.app.session_state["muestra"] = anterior
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertFalse(self.app.session_state["evaluacion_habilitada"])
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        migrada = self.app.session_state["muestra"]
        self.assertIsInstance(migrada, simulacion.ResultadoSimulacionCompacto)
        self.assertFalse(hasattr(migrada, "cuotas"))
        np.testing.assert_array_equal(migrada.ihh_puntos, anterior.ihh_puntos)
        self.simular()
        self.assertTrue(self.app.session_state["evaluacion_habilitada"])

    def test_ejemplo_desde_n2_actualiza_widgets_y_bloquea_muestra(self):
        self.app.number_input(key="n").set_value(2).run()
        self.app.number_input(key="k").set_value(1).run()
        muestra = self.simular()
        self.assertFalse(self.app.button(key="ejemplo").disabled)
        self.app.button(key="ejemplo").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.number_input(key="n").value, 4)
        self.assertEqual(self.app.number_input(key="k").value, 1)
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [40, 30, 20, 10])
        self.assertEqual(len(self.app.dataframe[0].value), 4)
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.assertTrue(self.app.button(key="comprobar_crk_numerico").disabled)
        self.assertEqual(self.motor.call_count, 1)

    def test_ejemplo_desde_n100_limita_k_y_limpia_respuestas(self):
        self.app.number_input(key="n").set_value(100).run()
        self.app.number_input(key="k").set_value(99).run()
        muestra = self.simular()
        self.app.text_input(key="respuesta_crk_numerica").set_value("100").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertIsNotNone(self.app.session_state["feedback_crk_numerico"])
        self.app.radio(key="respuesta_evaluacion").set_value("Baja").run()
        self.app.button(key="comprobar_evaluacion").click().run()
        self.app.button(key="ejemplo").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.number_input(key="n").value, 4)
        self.assertEqual(self.app.number_input(key="k").value, 4)
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [40, 30, 20, 10])
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertIsNone(self.app.radio(key="respuesta_evaluacion").value)
        self.assertEqual(self.app.text_input(key="respuesta_crk_numerica").value, "")
        self.assertIsNone(self.app.session_state["resultado_evaluacion"])
        self.assertIsNone(self.app.session_state["feedback_crk_numerico"])

    def test_numerica_vacia_feedback_y_edicion_reutilizan_motor(self):
        muestra = self.simular()
        self.app.button(key="ejemplo").click().run()
        self.assertEqual(self.app.text_input(key="respuesta_crk_numerica").value, "")
        self.assertTrue(self.app.button(key="comprobar_crk_numerico").disabled)
        self.app.text_input(key="respuesta_crk_numerica").set_value("70,01").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertTrue(self.app.session_state["feedback_crk_numerico"]["acierto"])
        self.app.selectbox(key="indicador").select("IE").run()
        self.assertTrue(self.app.session_state["feedback_crk_numerico"]["acierto"])
        self.app.text_input(key="respuesta_crk_numerica").set_value("30").run()
        self.assertIsNone(self.app.session_state["feedback_crk_numerico"])
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertFalse(self.app.session_state["feedback_crk_numerico"]["acierto"])
        self.cambiar_caso([35, 35, 20, 10])
        self.assertIsNone(self.app.session_state["feedback_crk_numerico"])
        self.assertEqual(self.app.text_input(key="respuesta_crk_numerica").value, "")
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertEqual(self.motor.call_count, 1)

    def test_numerica_cambio_k_simulacion_e_invalido(self):
        self.simular()
        self.app.text_input(key="respuesta_crk_numerica").set_value("50").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.app.number_input(key="k").set_value(3).run()
        self.assertIsNone(self.app.session_state["feedback_crk_numerico"])
        self.assertEqual(self.app.text_input(key="respuesta_crk_numerica").value, "")
        self.assertTrue(self.app.button(key="comprobar_crk_numerico").disabled)
        self.simular()
        self.app.text_input(key="respuesta_crk_numerica").set_value("75").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertTrue(self.app.session_state["feedback_crk_numerico"]["acierto"])
        self.simular()
        self.assertIsNone(self.app.session_state["feedback_crk_numerico"])
        self.assertEqual(self.app.text_input(key="respuesta_crk_numerica").value, "")
        self.cambiar_caso([40, 30, 20, 9])
        self.assertTrue(self.app.text_input(key="respuesta_crk_numerica").disabled)
        self.assertTrue(self.app.button(key="comprobar_crk_numerico").disabled)

    def test_numerica_no_finita_muestra_error_sin_excepcion(self):
        self.simular()
        self.app.button(key="ejemplo").click().run()
        self.app.text_input(key="respuesta_crk_numerica").set_value("nan").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertFalse(self.app.exception)
        self.assertIn("error_entrada", self.app.session_state["feedback_crk_numerico"])
        self.assertTrue(any("finita" in e.value for e in self.app.error))

    def test_ejemplo_desde_n100_conserva_k2_y_bloquea_comparacion(self):
        self.app.number_input(key="n").set_value(100).run()
        muestra = self.simular()
        self.app.button(key="ejemplo").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.number_input(key="n").value, 4)
        self.assertEqual(self.app.number_input(key="k").value, 2)
        self.assertEqual(self.app.session_state["caso_base"]["Cuota (%)"].tolist(), [40, 30, 20, 10])
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertFalse(hasattr(muestra, "cuotas"))
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.assertEqual(self.motor.call_count, 1)

    def test_ejemplo_compatible_limpia_respuesta_y_conserva_muestra_vigente(self):
        muestra = self.simular()
        self.app.text_input(key="respuesta_crk_numerica").set_value("50").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertTrue(self.app.session_state["feedback_crk_numerico"]["acierto"])
        self.app.button(key="ejemplo").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.text_input(key="respuesta_crk_numerica").value, "")
        self.assertIsNone(self.app.session_state["feedback_crk_numerico"])
        self.assertIs(self.app.session_state["muestra"], muestra)
        self.assertFalse(self.app.session_state["muestra_desactualizada"])
        self.assertTrue(self.app.session_state["comparacion_habilitada"])
        self.assertFalse(self.app.text_input(key="respuesta_crk_numerica").disabled)
        self.app.text_input(key="respuesta_crk_numerica").set_value("70").run()
        self.app.button(key="comprobar_crk_numerico").click().run()
        self.assertTrue(self.app.session_state["feedback_crk_numerico"]["acierto"])
        self.assertEqual(self.app.session_state["feedback_crk_numerico"]["cuotas_mayores_porcentaje"], (40, 30))
        self.assertEqual(self.motor.call_count, 1)


if __name__ == "__main__":
    unittest.main()
