"""Regresiones de llamadas, atributos, unidades y pregunta numérica recuperados."""

import importlib
import inspect
import unittest

import numpy as np
import plotly.graph_objects as go

from concentracion import indices, simulacion, graficos, evaluacion


CUOTAS = (0.4, 0.3, 0.2, 0.1)


class TestCompatibilidad(unittest.TestCase):
    def test_argumentos_originales_posicionales_y_por_nombre(self):
        casos = (
            (indices.calcular_crk, ("cuotas", "n", "k"), (CUOTAS, 4, 2), 0.7),
            (indices.calcular_ihh_decimal, ("cuotas", "n"), (CUOTAS, 4), 0.3),
            (indices.calcular_ihh_puntos, ("cuotas", "n"), (CUOTAS, 4), 3000),
            (indices.calcular_id_garcia_alba, ("cuotas", "n"), (CUOTAS, 4), 0.3933333333333333),
            (indices.calcular_entropia, ("cuotas", "n"), (CUOTAS, 4), 1.2798542258336676),
            (indices.calcular_entropia_normalizada, ("cuotas", "n"), (CUOTAS, 4), 1.2798542258336676 / np.log(4)),
        )
        for funcion, nombres, argumentos, esperado in casos:
            with self.subTest(funcion=funcion.__name__):
                self.assertEqual(tuple(inspect.signature(funcion).parameters), nombres)
                por_posicion = funcion(*argumentos)
                por_nombre = funcion(**dict(zip(nombres, argumentos)))
                self.assertIsInstance(por_posicion, float)
                self.assertEqual(por_posicion, por_nombre)
                self.assertAlmostEqual(por_posicion, esperado, places=10)
        self.assertEqual(indices.validar_cuotas(CUOTAS, 4), CUOTAS)
        self.assertEqual(indices.validar_cuotas(cuotas=CUOTAS, n=4), CUOTAS)
        with self.assertRaises(ValueError):
            indices.validar_cuotas(cuotas=CUOTAS, n=3)

    def test_imports_raiz_con_llamadas_publicas_de_indices_motor_y_graficos(self):
        origenes = {
            "indices": (indices, ("validar_cuotas", "calcular_crk", "calcular_ihh_decimal",
                "calcular_ihh_puntos", "calcular_id_garcia_alba", "calcular_entropia",
                "calcular_entropia_normalizada")),
            "simulacion": (simulacion, ("simular_mercados", "simular_mercados_compactos",
                "calcular_indicadores_vectorizados", "calcular_percentil_empirico",
                "compactar_resultado", "generar_caso_aleatorio")),
            "graficos": (graficos, ("crear_grafico_cuotas", "crear_histograma_comparativo",
                "convertir_valor_presentacion", "obtener_valores_simulados",
                "formatear_numero_indicador", "formatear_valor_indicador",
                "nombre_eje_indicador")),
        }
        raices = {}
        for nombre, (modulo, funciones) in origenes.items():
            raices[nombre] = importlib.import_module(nombre)
            for funcion in funciones:
                self.assertIs(getattr(raices[nombre], funcion), getattr(modulo, funcion))
        i, s, g = (raices[nombre] for nombre in ("indices", "simulacion", "graficos"))
        self.assertEqual(i.validar_cuotas(CUOTAS, 4), CUOTAS)
        self.assertAlmostEqual(i.calcular_crk(CUOTAS, 4, 2), 0.7)
        r = s.simular_mercados(n=4, k=2, iteraciones=13, semilla=42)
        self.assertEqual((r.n, r.iteraciones, r.cuotas.shape), (4, 13, (13, 4)))
        v = s.calcular_indicadores_vectorizados(cuotas=r.cuotas, n=4, k=2)
        for nombre, serie in v.items():
            np.testing.assert_array_equal(getattr(r, nombre), serie)
        compacto = s.compactar_resultado(resultado=r)
        directo = s.simular_mercados_compactos(n=4, k=2, iteraciones=13, semilla=42)
        np.testing.assert_array_equal(compacto.ihh_puntos, directo.ihh_puntos)
        self.assertFalse(hasattr(compacto, "cuotas"))
        self.assertEqual(s.calcular_percentil_empirico(valores_simulados=[1, 2, 2, 3], valor_caso=2), 75)
        i.validar_cuotas(s.generar_caso_aleatorio(n=4, k=2, semilla=42)["cuotas"], 4)
        self.assertIsInstance(g.crear_grafico_cuotas(cuotas=CUOTAS, n=4), go.Figure)
        figura = g.crear_histograma_comparativo(muestras=compacto, indicador="IHH", caso=i.calcular_ihh_decimal(CUOTAS, 4))
        self.assertAlmostEqual(figura.data[1].x[0], 3000)
        np.testing.assert_array_equal(g.obtener_valores_simulados(resultado=compacto, indicador="IHH"), compacto.ihh_puntos)
        self.assertEqual(g.convertir_valor_presentacion(indicador="CRk", valor=0.7), 70)
        self.assertEqual(g.formatear_numero_indicador(indicador="IHH", valor=3000, ihh_en_puntos=True), "3000.00")
        self.assertEqual(g.formatear_valor_indicador(indicador="CRk", valor=0.7), "70.00 %")
        self.assertEqual(g.nombre_eje_indicador(indicador="CRk", k=2), "CR2 (% de ventas)")

    def test_adaptadores_indices_resultados_y_unidades(self):
        self.assertAlmostEqual(indices.calcular_crk(CUOTAS, 4, 2), 0.7)
        self.assertAlmostEqual(indices.calcular_ihh_decimal(CUOTAS, 4), 0.3)
        self.assertAlmostEqual(indices.calcular_ihh_puntos(CUOTAS, 4), 3000)
        self.assertAlmostEqual(indices.calcular_id_garcia_alba(CUOTAS, 4), 0.3933333333, places=10)
        self.assertEqual(indices.calcular_entropia(CUOTAS, 4), indices.entropia_shannon(CUOTAS))
        self.assertEqual(indices.calcular_entropia_normalizada(CUOTAS, 4), indices.entropia_normalizada(CUOTAS))

    def test_adaptadores_indices_validan_n_exacto_y_entradas(self):
        funciones = (indices.calcular_ihh_decimal, indices.calcular_ihh_puntos,
                     indices.calcular_id_garcia_alba, indices.calcular_entropia,
                     indices.calcular_entropia_normalizada,
                     lambda cuotas, n: indices.calcular_crk(cuotas, n, 2))
        for funcion in funciones:
            for cuotas, n in ((CUOTAS, 3), ((0.4, 0.3, 0.2, 0.2), 4), ((1 + 5e-11, 0), 2)):
                with self.subTest(funcion=funcion.__name__, cuotas=cuotas, n=n):
                    with self.assertRaises(ValueError):
                        funcion(cuotas, n)
            with self.assertRaises(TypeError):
                funcion(CUOTAS, True)

    def test_resultado_completo_atributos_y_matriz_reproducible(self):
        r = simulacion.simular_mercados(4, 2, 1000, 42)
        self.assertIsInstance(r, simulacion.ResultadoSimulacion)
        self.assertEqual((r.n, r.iteraciones), (4, 1000))
        self.assertEqual(r.cuotas.shape, (1000, 4))
        self.assertTrue(r.cuotas.flags.owndata)
        np.testing.assert_array_equal(r.cuotas, np.random.default_rng(42).dirichlet(np.ones(4), size=1000))
        np.testing.assert_allclose(r.cuotas.sum(axis=1), 1, atol=1e-10, rtol=0)
        valores = simulacion.calcular_indicadores_vectorizados(r.cuotas, r.n, 2)
        for nombre, serie in valores.items():
            self.assertEqual(getattr(r, nombre).shape, (r.iteraciones,))
            np.testing.assert_array_equal(getattr(r, nombre), serie)
        self.assertIs(r.crk, r["crk"])
        self.assertIs(r.ihh_decimal, r["ihh"])
        self.assertEqual(set(r), {"crk", "ihh", "id", "ie", "configuracion"})

    def test_comparacion_resultados_no_compara_arrays(self):
        a = simulacion.simular_mercados(4, 2, 3, 42)
        b = simulacion.simular_mercados(4, 2, 3, 42)
        c = simulacion.compactar_resultado(a)
        d = simulacion.compactar_resultado(b)
        self.assertTrue(a == a)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertTrue(c == c)
        self.assertFalse(c == d)
        self.assertTrue((c,) != (d,))

    def test_compactar_copia_solo_cuatro_series_sin_doble_ihh(self):
        completo = simulacion.simular_mercados(4, 2, 1000, 42)
        compacto = simulacion.compactar_resultado(completo)
        directo = simulacion.simular_mercados_compactos(4, 2, 1000, 42)
        for campo in ("crk", "ihh_puntos", "id", "ie"):
            np.testing.assert_array_equal(getattr(compacto, campo), getattr(directo, campo))
            self.assertTrue(getattr(compacto, campo).flags.owndata)
        self.assertEqual(len(vars(compacto)), 5)
        self.assertFalse(hasattr(compacto, "cuotas"))
        self.assertFalse(np.shares_memory(compacto.crk, completo.crk))
        self.assertEqual(sum(getattr(compacto, c).nbytes for c in ("crk", "ihh_puntos", "id", "ie")), 32000)
        copia = simulacion.compactar_resultado(compacto)
        np.testing.assert_array_equal(copia.ihh_puntos, compacto.ihh_puntos)
        copia.ihh_puntos[0] = -1
        self.assertGreater(compacto.ihh_puntos[0], 0)
        self.assertEqual(completo.configuracion["unidades"]["ihh"], "proporcional")

    def test_vectorizados_coinciden_con_escalar_ceros_y_sin_mutacion(self):
        cuotas = np.array([[0.25] * 4, CUOTAS, [1, 0, 0, 0]])
        copia = cuotas.copy()
        esperado = {
            "crk": lambda f: indices.calcular_crk(f, 4, 2),
            "ihh_decimal": lambda f: indices.calcular_ihh_decimal(f, 4),
            "ihh_puntos": lambda f: indices.calcular_ihh_puntos(f, 4),
            "id_garcia_alba": lambda f: indices.calcular_id_garcia_alba(f, 4),
            "entropia": lambda f: indices.calcular_entropia(f, 4),
            "entropia_normalizada": lambda f: indices.calcular_entropia_normalizada(f, 4),
        }
        with np.errstate(divide="raise", invalid="raise"):
            resultado = simulacion.calcular_indicadores_vectorizados(cuotas, 4, 2)
        self.assertEqual(set(resultado), set(esperado))
        for nombre, funcion in esperado.items():
            np.testing.assert_allclose(resultado[nombre], [funcion(f) for f in cuotas], atol=2e-11 if nombre == "ihh_puntos" else 2e-14, rtol=0)
        np.testing.assert_array_equal(cuotas, copia)

    def test_vectorizados_rechazan_dimensiones_cierre_y_tipos(self):
        for cuotas in ([], [0.5, 0.5], [[0.4, 0.4]], [[np.nan, 0.5]], [[1 + 5e-11, 0]], [[-0.1, 1.1]], [[0.5, 0.5 + 5e-10]]):
            with self.subTest(cuotas=cuotas):
                with self.assertRaises(ValueError):
                    simulacion.calcular_indicadores_vectorizados(cuotas, 2, 1)
        for cuotas in ([[True, False]], [[True, 0.0]], [["0.5", "0.5"]], [[0.5j, 0.5]]):
            with self.assertRaises(TypeError):
                simulacion.calcular_indicadores_vectorizados(cuotas, 2, 1)
        with self.assertRaises(ValueError):
            simulacion.calcular_indicadores_vectorizados([CUOTAS], 3, 2)
        with self.assertRaises(ValueError):
            simulacion.calcular_indicadores_vectorizados([CUOTAS], 4, 5)

    def test_percentil_adaptador_empates_y_referencia_sin_forzar(self):
        self.assertEqual(simulacion.calcular_percentil_empirico([1, 2, 2, 3], 2), 75)
        r = simulacion.simular_mercados(4, 2, 1000, 42)
        caso = indices.calcular_ihh_puntos(CUOTAS, 4)
        self.assertEqual(np.count_nonzero(r.ihh_puntos <= caso), 171)
        self.assertAlmostEqual(simulacion.calcular_percentil_empirico(r.ihh_puntos, caso), 17.1)

    def test_adaptadores_presentacion_unidades_y_formato(self):
        self.assertEqual(graficos.convertir_valor_presentacion("CRk", 0.7), 70)
        self.assertEqual(graficos.convertir_valor_presentacion("IHH", 0.3), 3000)
        self.assertEqual(graficos.convertir_valor_presentacion("IHH", 3000, ihh_en_puntos=True), 3000)
        self.assertEqual(graficos.formatear_numero_indicador("IHH", 0.3), "3000.00")
        self.assertEqual(graficos.formatear_valor_indicador("CRk", 0.7), "70.00 %")
        self.assertEqual(graficos.formatear_valor_indicador("ID", 0.3933333333), "0.393333 adimensional")
        self.assertEqual(graficos.nombre_eje_indicador("CRk", 2), "CR2 (% de ventas)")
        self.assertIn("puntos", graficos.nombre_eje_indicador("IHH"))
        self.assertIn("nats", graficos.formatear_valor_indicador("IE", 1.2))

    def test_obtener_series_completas_y_compactas_sin_doble_escala(self):
        completo = simulacion.simular_mercados(4, 2, 23, 42)
        compacto = simulacion.compactar_resultado(completo)
        for nombre in ("CRk", "IHH", "ID", "IE"):
            np.testing.assert_array_equal(graficos.obtener_valores_simulados(completo, nombre), graficos.obtener_valores_simulados(compacto, nombre))
        np.testing.assert_array_equal(graficos.obtener_valores_simulados(compacto, "IHH"), completo.ihh_decimal * 10000)

    def test_adaptadores_graficos_llamadas_linea_y_percentil(self):
        fig = graficos.crear_grafico_cuotas(CUOTAS, 4)
        self.assertIsInstance(fig, go.Figure)
        np.testing.assert_array_equal(fig.data[0].y, [40, 30, 20, 10])
        completo = simulacion.simular_mercados(4, 2, 1000, 42)
        compacto = simulacion.compactar_resultado(completo)
        for resultado in (completo, compacto):
            fig = graficos.crear_histograma_comparativo(resultado, "IHH", indices.ihh(CUOTAS))
            np.testing.assert_allclose(fig.data[1].x, [3000, 3000], atol=2e-11, rtol=0)
            self.assertIn("17.10", fig.data[1].name)
            self.assertIn("puntos", fig.layout.xaxis.title.text)
        fig = graficos.crear_histograma_comparativo(compacto, "IHH", 3000, ihh_en_puntos=True)
        self.assertEqual(fig.data[1].x[0], 3000)
        fig = graficos.crear_histograma_comparativo([1, 1, 1], "CRk", 1, k=4)
        self.assertTrue(fig.layout.meta["constante"])
        self.assertIn("100.00", fig.data[1].name)

    def test_adaptadores_evaluacion_y_fronteras(self):
        self.assertEqual(evaluacion.intervalo_ihh(1500), evaluacion.INTERVALOS["Moderada"])
        self.assertEqual(evaluacion.intervalo_ihh(2500), evaluacion.INTERVALOS["Alta"])
        self.assertEqual(evaluacion.intervalo_ihh("Alta"), evaluacion.INTERVALOS["Alta"])
        completo = simulacion.simular_mercados(4, 2, 1000, 42)
        compacto = simulacion.compactar_resultado(completo)
        for muestra in (completo, compacto, completo.ihh_decimal):
            r = evaluacion.evaluar_respuesta_ihh(CUOTAS, "Alta", muestra, n=4)
            self.assertTrue(r["acierto"])
            self.assertAlmostEqual(r["ihh_puntos"], 3000)
            self.assertEqual(r["menores_o_iguales"], 171)
        with self.assertRaises(ValueError):
            evaluacion.evaluar_respuesta_ihh(CUOTAS, "Alta", simulacion.simular_mercados_compactos(2, 1, 10, 42))
        with self.assertRaises(ValueError):
            evaluacion.evaluar_respuesta_ihh(CUOTAS, "Alta", compacto, unidad_muestra="proporcion")

    def test_huella_comparable_sin_redondear(self):
        huella = evaluacion.huella_cuotas(np.array(CUOTAS), 4)
        self.assertIsInstance(huella, tuple)
        self.assertEqual(huella, CUOTAS)
        self.assertEqual(hash(huella), hash(CUOTAS))
        otra = (0.4 + 1e-12, 0.3 - 1e-12, 0.2, 0.1)
        self.assertNotEqual(huella, evaluacion.huella_cuotas(otra))
        with self.assertRaises(ValueError):
            evaluacion.huella_cuotas(CUOTAS, 2)


class TestCRkNumerico(unittest.TestCase):
    def test_coma_punto_y_tolerancia_inclusiva(self):
        for texto in ("70", "70,0", "70.0", "70,01", "69.99", " 70.005 "):
            with self.subTest(texto=texto):
                r = evaluacion.evaluar_crk_numerico(CUOTAS, 2, texto)
                self.assertTrue(r["acierto"])
                self.assertEqual(r["porcentaje_correcto"], 70)
                self.assertEqual(r["cuotas_mayores_porcentaje"], (40, 30))
                self.assertEqual(r["tolerancia_pp"], 0.01)
                self.assertIn("40 % + 30 % = 70 %", r["justificacion"])
        for texto in ("70.01000001", "69,98999", "30", "70.0100000000000000000000000000000001"):
            self.assertFalse(evaluacion.evaluar_crk_numerico(CUOTAS, 2, texto)["acierto"])

    def test_respuestas_invalidas_y_cuotas_invalidas(self):
        for texto in ("", "NaN", "nan", "Infinity", "-inf", "1e10000", "-1", "101", "abc", "70,0.0"):
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError):
                    evaluacion.evaluar_crk_numerico(CUOTAS, 2, texto)
        for valor in (70, None, True):
            with self.assertRaises(TypeError):
                evaluacion.evaluar_crk_numerico(CUOTAS, 2, valor)
        with self.assertRaises(ValueError):
            evaluacion.evaluar_crk_numerico([0.4, 0.3, 0.2, 0.2], 2, "70")
        with self.assertRaises(ValueError):
            evaluacion.evaluar_crk_numerico(CUOTAS, 5, "100")

    def test_se_calcula_desde_cuotas_actuales_y_k(self):
        cuotas = (0.1, 0.4, 0.2, 0.3)
        self.assertTrue(evaluacion.evaluar_crk_numerico(cuotas, 3, "90")["acierto"])
        self.assertTrue(evaluacion.evaluar_crk_numerico([0.25] * 4, 4, "100")["acierto"])
        cuotas = (0.401234567, 0.3, 0.2, 0.098765433)
        r = evaluacion.evaluar_crk_numerico(cuotas, 2, "70.1234567")
        self.assertEqual(r["porcentaje_correcto"], indices.crk(cuotas, 2) * 100)
        self.assertTrue(r["acierto"])


if __name__ == "__main__":
    unittest.main()
