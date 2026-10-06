"""Progreso observable sin alterar datos; limpieza transitoria con AppTest.

La barra se intercepta para observar actualizaciones durante la ejecución: estos
tests verifican llamadas/estado, sin afirmar una comprobación visual en navegador.
"""

from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from streamlit.testing.v1 import AppTest

from concentracion import simulacion


APP = Path(__file__).resolve().parents[1] / "app.py"


class TestCallbackProgreso(unittest.TestCase):
    def test_callback_preserva_arrays_y_configuracion_en_ambas_apis(self):
        for api in (simulacion.simular_mercados, simulacion.simular_mercados_compactos):
            for n, k, cantidad in ((2, 2, 1), (4, 2, 1000), (100, 50, 8201)):
                with self.subTest(api=api.__name__, n=n, cantidad=cantidad):
                    sin_callback = api(n, k, cantidad, 42)
                    eventos = []
                    con_callback = api(n, k, cantidad, 42,
                                       callback_progreso=lambda completas, total: eventos.append((completas, total)))
                    self.assertEqual(sin_callback.configuracion, con_callback.configuracion)
                    for nombre in ("crk", "ihh_puntos", "id", "ie"):
                        a = sin_callback[nombre] if nombre in ("id", "ie") else getattr(sin_callback, nombre)
                        b = con_callback[nombre] if nombre in ("id", "ie") else getattr(con_callback, nombre)
                        self.assertEqual(a.dtype, b.dtype)
                        self.assertEqual(a.tobytes(), b.tobytes())
                    if isinstance(con_callback, simulacion.ResultadoSimulacion):
                        self.assertEqual(sin_callback.cuotas.tobytes(), con_callback.cuotas.tobytes())
                    self.assertEqual(eventos[0], (0, cantidad))
                    self.assertEqual(eventos[-1], (cantidad, cantidad))

    def test_avances_por_lote_incluido_ultimo_parcial(self):
        for cantidad, lote, esperados in (
            (1, 4096, [0, 1]), (4096, 4096, [0, 4096]),
            (8201, 4096, [0, 4096, 8192, 8201]), (5, 2, [0, 2, 4, 5]),
        ):
            with self.subTest(cantidad=cantidad, lote=lote):
                eventos = []
                simulacion.simular_mercados_compactos(
                    4, 2, cantidad, 42, lote,
                    callback_progreso=lambda completas, total: eventos.append((completas, total)),
                )
                self.assertEqual(eventos, [(c, cantidad) for c in esperados])
                self.assertTrue(all(type(c) is int and type(t) is int for c, t in eventos))

    def test_ultimo_aviso_solo_despues_de_construir_resultado(self):
        for api, clase in ((simulacion.simular_mercados, "ResultadoSimulacion"),
                           (simulacion.simular_mercados_compactos, "ResultadoSimulacionCompacto")):
            with self.subTest(api=api.__name__):
                with patch.object(simulacion, clase, wraps=getattr(simulacion, clase)) as constructor:
                    def observar(completadas, total):
                        self.assertEqual(constructor.call_count, int(completadas == total))
                    api(4, 2, 5000, 42, callback_progreso=observar)

    def test_error_de_construccion_no_anuncia_cien_por_ciento(self):
        for api, clase in ((simulacion.simular_mercados, "ResultadoSimulacion"),
                           (simulacion.simular_mercados_compactos, "ResultadoSimulacionCompacto")):
            eventos = []
            with self.subTest(api=api.__name__), patch.object(simulacion, clase, side_effect=RuntimeError("construcción fallida")):
                with self.assertRaisesRegex(RuntimeError, "construcción fallida"):
                    api(4, 2, 5000, 42,
                        callback_progreso=lambda c, t: eventos.append((c, t)))
            self.assertEqual(eventos, [(0, 5000), (4096, 5000)])

    def test_fila_invalida_detiene_progreso_sin_repararla(self):
        cuotas = np.array([[0.4, 0.3, 0.2, 0.1], [0.4, 0.3, 0.2, 0.0]])
        original = cuotas.copy()
        eventos = []
        with patch.object(simulacion, "_crear_generador") as crear:
            crear.return_value = (MagicMock(), 42)
            crear.return_value[0].dirichlet.side_effect = [cuotas[:1], cuotas[1:]]
            with self.assertRaisesRegex(RuntimeError, "suman 1"):
                simulacion.simular_mercados_compactos(4, 2, 2, 42, 1,
                    callback_progreso=lambda c, t: eventos.append((c, t)))
        self.assertEqual(eventos, [(0, 2), (1, 2)])
        np.testing.assert_array_equal(cuotas, original)

    def test_callback_invalido_y_parametros_invalidos_no_generan(self):
        for api in (simulacion.simular_mercados, simulacion.simular_mercados_compactos):
            with self.subTest(api=api.__name__), patch.object(simulacion.np.random, "default_rng") as rng:
                with self.assertRaisesRegex(TypeError, "callback_progreso"):
                    api(4, 2, 1, 42, callback_progreso=3)
                callback = MagicMock()
                with self.assertRaises(ValueError):
                    api(1, 1, 1, 42, callback_progreso=callback)
                callback.assert_not_called()
                rng.assert_not_called()

    def test_excepcion_del_callback_se_propaga_sin_resultado_parcial(self):
        eventos = []

        def fallar(completadas, total):
            eventos.append((completadas, total))
            if completadas:
                raise OSError("observador fallido")

        with self.assertRaisesRegex(OSError, "observador fallido"):
            simulacion.simular_mercados_compactos(4, 2, 5, 42, 2, callback_progreso=fallar)
        self.assertEqual(eventos, [(0, 5), (2, 5)])


class TestProgresoInterfaz(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP), default_timeout=30).run()
        self.assertFalse(self.app.exception)

    def test_barra_real_termina_en_cien_y_desaparece_al_reejecutar(self):
        self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        barras = self.app.get("progress")
        self.assertEqual(len(barras), 1)
        self.assertEqual(barras[0].proto.value, 100)
        self.assertEqual(barras[0].proto.text, "1,000 / 1,000 iteraciones completadas")
        muestra = self.app.session_state["muestra"]
        self.app.selectbox(key="indicador").select("IE").run()
        self.assertFalse(self.app.get("progress"))
        self.assertIs(self.app.session_state["muestra"], muestra)
        with patch.object(simulacion, "simular_mercados_compactos", side_effect=RuntimeError("fallo comprobado")):
            self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        self.assertFalse(self.app.get("progress"))
        self.assertIs(self.app.session_state["muestra"], muestra)

    def test_barra_avanza_y_cien_solo_con_muestra_guardada(self):
        self.app.number_input(key="iteraciones").set_value(10000).run()
        barra = MagicMock()
        avances = []

        def observar(valor, *, text):
            avances.append((valor, text))
            muestra = self.app.session_state["muestra"]
            if valor == 1.0:
                self.assertIsInstance(muestra, simulacion.ResultadoSimulacionCompacto)
                self.assertEqual(muestra.crk.size, 10000)
                self.assertTrue(np.isfinite(muestra.ihh_puntos).all())
                self.assertFalse(self.app.session_state["muestra_desactualizada"])
            else:
                self.assertIsNone(muestra)

        barra.progress.side_effect = observar
        with patch("streamlit.progress", return_value=barra) as crear:
            self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        crear.assert_called_once_with(0.0, text="0 / 10,000 iteraciones completadas")
        self.assertEqual([v for v, _ in avances], [0.0, 0.4096, 0.8192, 1.0])
        self.assertEqual([t for _, t in avances], [
            "0 / 10,000 iteraciones completadas", "4,096 / 10,000 iteraciones completadas",
            "8,192 / 10,000 iteraciones completadas", "10,000 / 10,000 iteraciones completadas",
        ])
        barra.empty.assert_not_called()
        self.assertFalse(self.app.session_state["simulacion_en_curso"])
        with self.assertRaises(KeyError):
            self.app.session_state["progreso"]

    def test_fallo_durante_lotes_limpia_barra_y_conserva_ultima_muestra(self):
        self.app.button(key="simular").click().run()
        anterior = self.app.session_state["muestra"]
        revision = self.app.session_state["revision_muestra"]
        self.app.number_input(key="iteraciones").set_value(10000).run()
        validar = simulacion._validar_filas
        llamadas = []

        def fallar_segundo(cuotas, n, cantidad):
            llamadas.append(cantidad)
            validar(cuotas, n, cantidad)
            if len(llamadas) == 2:
                raise RuntimeError("fallo de lote comprobado")

        barra = MagicMock()
        with patch("streamlit.progress", return_value=barra), patch.object(simulacion, "_validar_filas", side_effect=fallar_segundo):
            self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual([c.args[0] for c in barra.progress.call_args_list], [0.0, 0.4096])
        barra.empty.assert_called_once_with()
        self.assertIs(self.app.session_state["muestra"], anterior)
        self.assertEqual(self.app.session_state["revision_muestra"], revision)
        self.assertTrue(self.app.session_state["muestra_desactualizada"])
        self.assertFalse(self.app.session_state["simulacion_en_curso"])
        self.assertFalse(self.app.session_state["comparacion_habilitada"])
        self.assertTrue(any("fallo de lote comprobado" in e.value for e in self.app.error))

    def test_error_del_observador_limpia_barra_sin_cien_por_ciento(self):
        barra = MagicMock()
        barra.progress.side_effect = OSError("barra no disponible")
        with patch("streamlit.progress", return_value=barra):
            self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        barra.empty.assert_called_once_with()
        self.assertEqual([c.args[0] for c in barra.progress.call_args_list], [0.0])
        self.assertIsNone(self.app.session_state["muestra"])
        self.assertFalse(self.app.session_state["simulacion_en_curso"])
        self.assertTrue(any("barra no disponible" in e.value for e in self.app.error))

    def test_error_de_memoria_limpia_barra_inicial(self):
        barra = MagicMock()
        with patch("streamlit.progress", return_value=barra), patch.object(simulacion, "simular_mercados_compactos", side_effect=MemoryError("memoria insuficiente")):
            self.app.button(key="simular").click().run()
        self.assertFalse(self.app.exception)
        barra.empty.assert_called_once_with()
        barra.progress.assert_not_called()
        self.assertIsNone(self.app.session_state["muestra"])
        self.assertFalse(self.app.session_state["simulacion_en_curso"])
        self.assertTrue(any("memoria insuficiente" in e.value for e in self.app.error))

    def test_ayudas_unicas_y_percentil_ie_sin_resimular(self):
        textos = [c.value for c in self.app.caption]
        self.assertEqual(sum("Dirichlet(1,…,1)" in t for t in textos), 1)
        self.assertEqual(sum("atol=1e-10, rtol=0" in t for t in textos), 1)
        self.app.button(key="simular").click().run()
        muestra = self.app.session_state["muestra"]
        self.app.selectbox(key="indicador").select("IE").run()
        self.assertFalse(self.app.exception)
        self.assertIs(self.app.session_state["muestra"], muestra)
        ayudas = [c.value for c in self.app.caption if "El percentil compara este caso" in c.value]
        self.assertEqual(len(ayudas), 1)
        self.assertIn("variabilidad estadística", ayudas[0])
        self.assertIn("mismo entorno", ayudas[0])
        self.assertEqual(sum("Se incluyen los empates" in e.value for e in self.app.markdown), 1)
        self.assertEqual(sum("no significa mayor concentración" in e.value for e in self.app.info), 1)


if __name__ == "__main__":
    unittest.main()
