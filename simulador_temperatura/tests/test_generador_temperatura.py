"""Tests unitarios para GeneradorTemperatura."""
import time
import pytest
from unittest.mock import MagicMock

from PyQt6.QtCore import QCoreApplication

from app.dominio import GeneradorTemperatura, EstadoTemperatura
from app.configuracion.config import ConfigSimuladorTemperatura


@pytest.fixture
def config():
    """Fixture con configuración estándar para tests."""
    return ConfigSimuladorTemperatura(
        ip_raspberry="192.168.1.100",
        puerto=12000,
        intervalo_envio_ms=100,
        temperatura_minima=-10.0,
        temperatura_maxima=50.0,
        temperatura_inicial=20.0,
        ruido_amplitud=0.5,
        paso_variacion=0.1,
        variacion_amplitud=5.0,
        variacion_periodo_segundos=60.0,
    )


@pytest.fixture
def generador(config, qtbot):
    """Fixture con generador de temperatura."""
    gen = GeneradorTemperatura(config)
    return gen


class TestGeneradorTemperaturaCreacion:
    """Tests de creación del generador."""

    def test_crear_generador(self, config, qtbot):
        """Verifica creación básica del generador."""
        generador = GeneradorTemperatura(config)

        assert generador is not None
        assert generador.modo_manual is False

    def test_modo_inicial_automatico(self, generador):
        """Verifica que el modo inicial es automático."""
        assert generador.modo_manual is False


class TestGeneradorTemperaturaModoAutomatico:
    """Tests del modo automático."""

    def test_generar_valor_automatico(self, generador):
        """Genera valor en modo automático."""
        estado = generador.generar_valor()

        assert isinstance(estado, EstadoTemperatura)

    def test_generar_valor_retorna_estado_temperatura(self, generador):
        """Verifica tipo de retorno."""
        estado = generador.generar_valor()

        assert isinstance(estado, EstadoTemperatura)
        assert hasattr(estado, 'temperatura')
        assert hasattr(estado, 'timestamp')
        assert hasattr(estado, 'en_rango')

    def test_temperatura_actual_en_modo_automatico(self, generador):
        """Verifica que temperatura_actual retorna valor senoidal."""
        temp = generador.temperatura_actual

        # En t=0, debería estar cerca de temperatura_base (20.0)
        assert 15.0 <= temp <= 25.0

    def test_temperatura_valida_rango(self, generador):
        """Verifica que el estado valida el rango."""
        estado = generador.generar_valor()

        # Con amplitud 5 y base 20, rango es 15-25, dentro de -10 a 50
        assert estado.en_rango is True


class TestGeneradorTemperaturaModoManual:
    """Tests del modo manual."""

    def test_set_temperatura_manual(self, generador):
        """Verifica cambio a modo manual."""
        generador.set_temperatura_manual(25.0)

        assert generador.modo_manual is True

    def test_generar_valor_manual(self, generador):
        """Genera valor en modo manual."""
        generador.set_temperatura_manual(30.0)

        estado = generador.generar_valor()

        assert estado.temperatura == 30.0

    def test_temperatura_actual_en_modo_manual(self, generador):
        """Verifica temperatura_actual en modo manual."""
        generador.set_temperatura_manual(35.0)

        assert generador.temperatura_actual == 35.0

    def test_set_modo_automatico(self, generador):
        """Verifica retorno a modo automático."""
        generador.set_temperatura_manual(25.0)
        assert generador.modo_manual is True

        generador.set_modo_automatico()

        assert generador.modo_manual is False

    def test_temperatura_manual_fuera_de_rango(self, generador):
        """Verifica validación de rango con temperatura manual."""
        generador.set_temperatura_manual(100.0)  # Fuera del rango -10 a 50

        estado = generador.generar_valor()

        assert estado.temperatura == 100.0
        assert estado.en_rango is False


class TestGeneradorTemperaturaSignals:
    """Tests de señales Qt."""

    def test_signal_valor_generado(self, generador, qtbot):
        """Verifica emisión de señal valor_generado."""
        with qtbot.waitSignal(generador.valor_generado, timeout=1000) as blocker:
            generador.generar_valor()

        assert isinstance(blocker.args[0], EstadoTemperatura)

    def test_signal_temperatura_cambiada_modo_manual(self, generador, qtbot):
        """Verifica emisión de señal al cambiar a modo manual."""
        with qtbot.waitSignal(generador.temperatura_cambiada, timeout=1000) as blocker:
            generador.set_temperatura_manual(25.0)

        assert blocker.args[0] == 25.0

    def test_signal_temperatura_cambiada_al_generar(self, generador, qtbot):
        """Verifica emisión de señal cuando cambia la temperatura."""
        # Primera generación - debería emitir porque es el primer valor
        with qtbot.waitSignal(generador.temperatura_cambiada, timeout=1000):
            generador.generar_valor()


class TestGeneradorTemperaturaTimer:
    """Tests del timer interno."""

    def test_iniciar_timer(self, generador, qtbot):
        """Verifica que iniciar activa el timer."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()

        # Esperar al menos 2 emisiones (intervalo 100ms)
        qtbot.wait(250)

        generador.detener()

        assert len(signal_spy) >= 2

    def test_detener_timer(self, generador, qtbot):
        """Verifica que detener para el timer."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()
        qtbot.wait(150)
        generador.detener()

        count_after_stop = len(signal_spy)
        qtbot.wait(150)

        # No deberían haberse emitido más señales
        assert len(signal_spy) == count_after_stop


class TestGeneradorTemperaturaIntegracion:
    """Tests de integración con otros componentes."""

    def test_integracion_con_variacion_senoidal(self, config, qtbot):
        """Verifica integración correcta con VariacionSenoidal."""
        generador = GeneradorTemperatura(config)

        # Generar varios valores y verificar que varían
        valores = [generador.generar_valor().temperatura for _ in range(10)]

        # En modo automático, los valores deberían estar en el rango esperado
        for valor in valores:
            assert config.temperatura_inicial - config.variacion_amplitud <= valor
            assert valor <= config.temperatura_inicial + config.variacion_amplitud

    def test_to_string_del_estado_generado(self, generador):
        """Verifica que el estado generado puede convertirse a string TCP."""
        estado = generador.generar_valor()

        resultado = estado.to_string()

        assert resultado.endswith('\n')
        # Verificar que es un número válido
        float(resultado.strip())
