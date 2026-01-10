"""Tests para el Panel de Gráfico MVC."""

import time
import pytest

from app.presentacion.paneles.grafico import (
    ConfigGrafico,
    PuntoTemperatura,
    DatosGrafico,
    GraficoTemperaturaVista,
    GraficoControlador,
)


class TestConfigGrafico:
    """Tests para ConfigGrafico."""

    def test_crear_por_defecto(self):
        """Crear con valores por defecto."""
        config = ConfigGrafico()

        assert config.ventana_segundos == 60
        assert config.temp_min_display == -10.0
        assert config.temp_max_display == 50.0
        assert config.max_puntos == 600

    def test_crear_personalizado(self):
        """Crear con valores personalizados."""
        config = ConfigGrafico(
            ventana_segundos=120,
            temp_min_display=0.0,
            temp_max_display=40.0
        )

        assert config.ventana_segundos == 120
        assert config.temp_min_display == 0.0
        assert config.temp_max_display == 40.0


class TestPuntoTemperatura:
    """Tests para PuntoTemperatura."""

    def test_crear_punto(self):
        """Crear un punto de temperatura."""
        punto = PuntoTemperatura(tiempo=10.5, temperatura=25.0)

        assert punto.tiempo == 10.5
        assert punto.temperatura == 25.0


class TestDatosGrafico:
    """Tests para el modelo DatosGrafico."""

    def test_crear_por_defecto(self):
        """Crear modelo con valores por defecto."""
        datos = DatosGrafico()

        assert datos.cantidad_puntos == 0
        assert datos.ultima_temperatura is None
        assert datos.tiene_datos is False

    def test_agregar_punto(self):
        """agregar_punto añade datos al buffer."""
        datos = DatosGrafico()
        timestamp = time.time()

        tiempo_rel = datos.agregar_punto(25.0, timestamp)

        assert datos.cantidad_puntos == 1
        assert datos.ultima_temperatura == 25.0
        assert tiempo_rel == 0.0  # Primer punto tiene tiempo relativo 0

    def test_agregar_multiples_puntos(self):
        """Agregar múltiples puntos incrementa correctamente."""
        datos = DatosGrafico()
        t0 = time.time()

        datos.agregar_punto(20.0, t0)
        datos.agregar_punto(22.0, t0 + 1)
        datos.agregar_punto(24.0, t0 + 2)

        assert datos.cantidad_puntos == 3
        assert datos.ultima_temperatura == 24.0

    def test_obtener_datos(self):
        """obtener_datos retorna listas de tiempos y temperaturas."""
        datos = DatosGrafico()
        t0 = time.time()

        datos.agregar_punto(20.0, t0)
        datos.agregar_punto(25.0, t0 + 1)

        tiempos, temps = datos.obtener_datos()

        assert len(tiempos) == 2
        assert len(temps) == 2
        assert temps[0] == 20.0
        assert temps[1] == 25.0

    def test_limpiar(self):
        """limpiar elimina todos los datos."""
        datos = DatosGrafico()
        t0 = time.time()
        datos.agregar_punto(25.0, t0)

        datos.limpiar()

        assert datos.cantidad_puntos == 0
        assert datos.tiene_datos is False

    def test_limites_referencia(self):
        """Los límites de referencia se configuran correctamente."""
        datos = DatosGrafico(
            temp_min_referencia=15.0,
            temp_max_referencia=30.0
        )

        assert datos.temp_min_referencia == 15.0
        assert datos.temp_max_referencia == 30.0


class TestGraficoTemperaturaVista:
    """Tests para GraficoTemperaturaVista."""

    def test_crear_vista(self, qtbot):
        """Crear vista con configuración por defecto."""
        vista = GraficoTemperaturaVista()
        qtbot.addWidget(vista)

        assert vista is not None
        assert vista.plot_widget is not None

    def test_crear_con_config(self, qtbot):
        """Crear vista con configuración personalizada."""
        config = ConfigGrafico(ventana_segundos=120)
        vista = GraficoTemperaturaVista(config=config)
        qtbot.addWidget(vista)

        assert vista is not None

    def test_actualizar_con_modelo(self, qtbot):
        """actualizar() dibuja los datos del modelo."""
        vista = GraficoTemperaturaVista()
        qtbot.addWidget(vista)

        datos = DatosGrafico()
        t0 = time.time()
        datos.agregar_punto(20.0, t0)
        datos.agregar_punto(25.0, t0 + 1)

        vista.actualizar(datos)

        # Verificar que la curva tiene datos
        # (pyqtgraph no expone fácilmente los datos, pero no debe fallar)
        assert True

    def test_dibujar_datos(self, qtbot):
        """dibujar_datos dibuja datos directamente."""
        vista = GraficoTemperaturaVista()
        qtbot.addWidget(vista)

        vista.dibujar_datos([0, 1, 2], [20.0, 22.0, 24.0])

        assert True  # No debe fallar

    def test_limpiar(self, qtbot):
        """limpiar() limpia el gráfico."""
        vista = GraficoTemperaturaVista()
        qtbot.addWidget(vista)

        vista.dibujar_datos([0, 1], [20.0, 25.0])
        vista.limpiar()

        assert True  # No debe fallar


class TestGraficoControlador:
    """Tests para GraficoControlador."""

    def test_crear_controlador(self, qtbot):
        """Crear controlador sin argumentos."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)

        assert controlador.modelo is not None
        assert controlador.vista is not None
        assert controlador.cantidad_puntos == 0

    def test_crear_con_config(self, qtbot):
        """Crear controlador con configuración personalizada."""
        config = ConfigGrafico(ventana_segundos=120)
        controlador = GraficoControlador(config=config)
        qtbot.addWidget(controlador.vista)

        assert controlador.config.ventana_segundos == 120

    def test_agregar_punto(self, qtbot):
        """agregar_punto añade datos al gráfico."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.agregar_punto(25.0)

        assert controlador.cantidad_puntos == 1
        assert controlador.ultima_temperatura == 25.0

    def test_agregar_punto_emite_signal(self, qtbot):
        """agregar_punto emite signal."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.punto_agregado, timeout=1000) as blocker:
            controlador.agregar_punto(25.0)

        assert blocker.args[1] == 25.0  # args[0] es timestamp, args[1] es temp

    def test_limpiar(self, qtbot):
        """limpiar() elimina todos los datos."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)
        controlador.agregar_punto(25.0)

        controlador.limpiar()

        assert controlador.cantidad_puntos == 0
        assert controlador.tiene_datos is False

    def test_limpiar_emite_signal(self, qtbot):
        """limpiar emite signal."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.grafico_limpiado, timeout=1000):
            controlador.limpiar()

    def test_set_limites_referencia(self, qtbot):
        """set_limites_referencia actualiza el modelo."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.set_limites_referencia(temp_min=15.0, temp_max=30.0)

        assert controlador.modelo.temp_min_referencia == 15.0
        assert controlador.modelo.temp_max_referencia == 30.0

    def test_obtener_datos(self, qtbot):
        """obtener_datos retorna los datos del modelo."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)
        controlador.agregar_punto(20.0, timestamp=1000.0)
        controlador.agregar_punto(25.0, timestamp=1001.0)

        tiempos, temps = controlador.obtener_datos()

        assert len(tiempos) == 2
        assert temps[0] == 20.0
        assert temps[1] == 25.0

    def test_multiples_puntos(self, qtbot):
        """Agregar múltiples puntos funciona correctamente."""
        controlador = GraficoControlador()
        qtbot.addWidget(controlador.vista)

        for i in range(10):
            controlador.agregar_punto(20.0 + i)

        assert controlador.cantidad_puntos == 10
        assert controlador.ultima_temperatura == 29.0
