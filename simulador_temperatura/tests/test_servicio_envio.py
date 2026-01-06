"""Tests unitarios para ServicioEnvioTemperatura."""
import pytest
from unittest.mock import MagicMock, patch

from app.comunicacion import ServicioEnvioTemperatura, ClienteTemperatura
from app.dominio import GeneradorTemperatura, EstadoTemperatura
from app.configuracion.config import ConfigSimuladorTemperatura


@pytest.fixture
def config():
    """Fixture con configuración estándar para tests."""
    return ConfigSimuladorTemperatura(
        ip_raspberry="127.0.0.1",
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
    return GeneradorTemperatura(config)


@pytest.fixture
def mock_cliente(qtbot):
    """Fixture con mock de ClienteTemperatura."""
    with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient'):
        cliente = ClienteTemperatura("127.0.0.1", 12000)
        return cliente


@pytest.fixture
def servicio(generador, mock_cliente, qtbot):
    """Fixture con servicio de envío."""
    return ServicioEnvioTemperatura(generador, mock_cliente)


class TestServicioEnvioCreacion:
    """Tests de creación del servicio."""

    def test_crear_servicio(self, generador, mock_cliente, qtbot):
        """Verifica creación básica del servicio."""
        servicio = ServicioEnvioTemperatura(generador, mock_cliente)

        assert servicio is not None
        assert servicio.activo is False

    def test_propiedades_generador_cliente(self, servicio, generador, mock_cliente):
        """Verifica getters de generador y cliente."""
        assert servicio.generador is generador
        assert servicio.cliente is mock_cliente


class TestServicioEnvioInicioDetener:
    """Tests de inicio y detención del servicio."""

    def test_iniciar_servicio(self, servicio, qtbot):
        """Verifica que iniciar activa el servicio."""
        servicio.iniciar()

        assert servicio.activo is True

        servicio.detener()

    def test_detener_servicio(self, servicio, qtbot):
        """Verifica que detener desactiva el servicio."""
        servicio.iniciar()
        servicio.detener()

        assert servicio.activo is False

    def test_iniciar_ya_activo_no_error(self, servicio, qtbot):
        """Verifica que iniciar dos veces no causa error."""
        servicio.iniciar()
        servicio.iniciar()  # No debería causar error

        assert servicio.activo is True

        servicio.detener()

    def test_detener_ya_inactivo_no_error(self, servicio, qtbot):
        """Verifica que detener sin iniciar no causa error."""
        servicio.detener()  # No debería causar error

        assert servicio.activo is False


class TestServicioEnvioSignals:
    """Tests de señales Qt."""

    def test_signal_servicio_iniciado(self, servicio, qtbot):
        """Verifica emisión de señal servicio_iniciado."""
        with qtbot.waitSignal(servicio.servicio_iniciado, timeout=1000):
            servicio.iniciar()

        servicio.detener()

    def test_signal_servicio_detenido(self, servicio, qtbot):
        """Verifica emisión de señal servicio_detenido."""
        servicio.iniciar()

        with qtbot.waitSignal(servicio.servicio_detenido, timeout=1000):
            servicio.detener()

    def test_signal_envio_exitoso(self, servicio, qtbot):
        """Verifica emisión de señal envio_exitoso."""
        with qtbot.waitSignal(servicio.envio_exitoso, timeout=1000) as blocker:
            servicio._on_dato_enviado(25.5)

        assert blocker.args[0] == 25.5

    def test_signal_envio_fallido(self, servicio, qtbot):
        """Verifica emisión de señal envio_fallido."""
        with qtbot.waitSignal(servicio.envio_fallido, timeout=1000) as blocker:
            servicio._on_error_conexion("Connection refused")

        assert blocker.args[0] == "Connection refused"


class TestServicioEnvioIntegracion:
    """Tests de integración entre componentes."""

    def test_valor_generado_se_envia(self, config, qtbot):
        """Verifica que los valores generados se envían al cliente."""
        generador = GeneradorTemperatura(config)

        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            cliente = ClienteTemperatura("127.0.0.1", 12000)
            servicio = ServicioEnvioTemperatura(generador, cliente)

            servicio.iniciar()
            qtbot.wait(150)  # Esperar al menos una emisión
            servicio.detener()

            # Verificar que se llamó enviar_estado_async
            assert mock_instance.send_async.called

    def test_conexion_generador_cliente(self, generador, qtbot):
        """Verifica conexión correcta de señales."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            cliente = ClienteTemperatura("127.0.0.1", 12000)
            servicio = ServicioEnvioTemperatura(generador, cliente)

            # Simular valor generado manualmente
            estado = EstadoTemperatura(temperatura=22.5)

            servicio.iniciar()
            servicio._on_valor_generado(estado)
            servicio.detener()

            mock_instance.send_async.assert_called_with("22.50")
