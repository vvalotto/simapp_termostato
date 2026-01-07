"""Tests unitarios para GraficoTemperatura."""
import time
import pytest

from app.presentacion import GraficoTemperatura, ConfigGrafico


class TestConfigGrafico:
    """Tests para el dataclass ConfigGrafico."""

    def test_config_por_defecto(self):
        """Verifica configuración por defecto."""
        config = ConfigGrafico()
        assert config.ventana_segundos == 60
        assert config.temp_min_display == -10.0
        assert config.temp_max_display == 50.0
        assert config.max_puntos == 600
        assert config.color_linea == "#4fc3f7"
        assert config.color_referencia == "#ff5252"

    def test_config_personalizada(self):
        """Verifica configuración personalizada."""
        config = ConfigGrafico(
            ventana_segundos=120,
            temp_min_display=0.0,
            temp_max_display=100.0,
        )
        assert config.ventana_segundos == 120
        assert config.temp_min_display == 0.0
        assert config.temp_max_display == 100.0


class TestGraficoTemperaturaCreacion:
    """Tests de creación del GraficoTemperatura."""

    def test_crear_grafico(self, qtbot):
        """Verifica creación básica del gráfico."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        assert grafico is not None
        assert grafico.cantidad_puntos == 0
        assert grafico.ultima_temperatura is None

    def test_crear_grafico_con_config(self, qtbot):
        """Verifica creación con configuración personalizada."""
        config = ConfigGrafico(ventana_segundos=120)
        grafico = GraficoTemperatura(config=config)
        qtbot.addWidget(grafico)

        assert grafico is not None

    def test_crear_grafico_con_referencias(self, qtbot):
        """Verifica creación con líneas de referencia."""
        grafico = GraficoTemperatura(
            temp_min_referencia=-5.0,
            temp_max_referencia=40.0,
        )
        qtbot.addWidget(grafico)

        assert grafico._temp_min_ref == -5.0
        assert grafico._temp_max_ref == 40.0


class TestGraficoTemperaturaAddPunto:
    """Tests de agregar puntos al gráfico."""

    def test_add_punto(self, qtbot):
        """Verifica agregar un punto."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        grafico.add_punto(25.0)

        assert grafico.cantidad_puntos == 1
        assert grafico.ultima_temperatura == 25.0

    def test_add_punto_con_timestamp(self, qtbot):
        """Verifica agregar punto con timestamp específico."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        timestamp = time.time()
        grafico.add_punto(25.0, timestamp=timestamp)

        assert grafico.cantidad_puntos == 1

    def test_add_multiples_puntos(self, qtbot):
        """Verifica agregar múltiples puntos."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        for temp in [20.0, 21.0, 22.0, 23.0, 24.0]:
            grafico.add_punto(temp)

        assert grafico.cantidad_puntos == 5
        assert grafico.ultima_temperatura == 24.0

    def test_add_punto_emite_signal(self, qtbot):
        """Verifica que add_punto emite señal."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        with qtbot.waitSignal(grafico.punto_agregado, timeout=1000) as blocker:
            grafico.add_punto(25.0)

        assert blocker.args[1] == 25.0  # temperatura


class TestGraficoTemperaturaBufferCircular:
    """Tests del buffer circular."""

    def test_buffer_limita_puntos(self, qtbot):
        """Verifica que el buffer limita la cantidad de puntos."""
        config = ConfigGrafico(max_puntos=10)
        grafico = GraficoTemperatura(config=config)
        qtbot.addWidget(grafico)

        # Agregar más puntos que el máximo
        for i in range(15):
            grafico.add_punto(float(i))

        assert grafico.cantidad_puntos == 10
        # El primer punto debe ser el 5 (se descartaron 0-4)
        assert grafico._temperaturas[0] == 5.0

    def test_buffer_mantiene_orden(self, qtbot):
        """Verifica que el buffer mantiene el orden FIFO."""
        config = ConfigGrafico(max_puntos=5)
        grafico = GraficoTemperatura(config=config)
        qtbot.addWidget(grafico)

        for temp in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]:
            grafico.add_punto(temp)

        temps = list(grafico._temperaturas)
        assert temps == [30.0, 40.0, 50.0, 60.0, 70.0]


class TestGraficoTemperaturaClear:
    """Tests de limpiar el gráfico."""

    def test_clear_elimina_datos(self, qtbot):
        """Verifica que clear elimina todos los datos."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        grafico.add_punto(25.0)
        grafico.add_punto(26.0)
        grafico.clear()

        assert grafico.cantidad_puntos == 0
        assert grafico.ultima_temperatura is None

    def test_clear_permite_nuevos_datos(self, qtbot):
        """Verifica que se pueden agregar datos después de clear."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        grafico.add_punto(25.0)
        grafico.clear()
        grafico.add_punto(30.0)

        assert grafico.cantidad_puntos == 1
        assert grafico.ultima_temperatura == 30.0


class TestGraficoTemperaturaLineasReferencia:
    """Tests de líneas de referencia."""

    def test_set_limites_referencia(self, qtbot):
        """Verifica establecer límites de referencia."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        grafico.set_limites_referencia(temp_min=-5.0, temp_max=45.0)

        assert grafico._temp_min_ref == -5.0
        assert grafico._temp_max_ref == 45.0

    def test_actualizar_limites_existentes(self, qtbot):
        """Verifica actualizar límites existentes."""
        grafico = GraficoTemperatura(
            temp_min_referencia=0.0,
            temp_max_referencia=40.0,
        )
        qtbot.addWidget(grafico)

        grafico.set_limites_referencia(temp_min=-10.0, temp_max=50.0)

        assert grafico._temp_min_ref == -10.0
        assert grafico._temp_max_ref == 50.0


class TestGraficoTemperaturaVentanaTiempo:
    """Tests de ventana de tiempo."""

    def test_set_ventana_tiempo(self, qtbot):
        """Verifica cambiar ventana de tiempo."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        grafico.set_ventana_tiempo(120)

        assert grafico._config.ventana_segundos == 120


class TestGraficoTemperaturaProperties:
    """Tests de propiedades del gráfico."""

    def test_cantidad_puntos_inicial(self, qtbot):
        """Verifica cantidad de puntos inicial."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        assert grafico.cantidad_puntos == 0

    def test_ultima_temperatura_none_si_vacio(self, qtbot):
        """Verifica última temperatura None si está vacío."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        assert grafico.ultima_temperatura is None

    def test_ultima_temperatura_retorna_ultimo_valor(self, qtbot):
        """Verifica que última temperatura retorna el último valor."""
        grafico = GraficoTemperatura()
        qtbot.addWidget(grafico)

        grafico.add_punto(20.0)
        grafico.add_punto(25.0)
        grafico.add_punto(30.0)

        assert grafico.ultima_temperatura == 30.0
