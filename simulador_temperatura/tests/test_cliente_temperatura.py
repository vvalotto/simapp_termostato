"""Tests unitarios para ClienteTemperatura."""
import pytest
from unittest.mock import MagicMock, patch

from app.comunicacion import ClienteTemperatura
from app.dominio import EstadoTemperatura


@pytest.fixture
def mock_ephemeral_client():
    """Fixture con mock de EphemeralSocketClient."""
    with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
        mock_instance = MagicMock()
        mock_instance.send.return_value = True
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def cliente(mock_ephemeral_client, qtbot):
    """Fixture con cliente de temperatura usando mock."""
    with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
        mock_class.return_value = mock_ephemeral_client
        cliente = ClienteTemperatura("127.0.0.1", 12000)
        return cliente


class TestClienteTemperaturaCreacion:
    """Tests de creación del cliente."""

    def test_crear_cliente(self, qtbot):
        """Verifica creación básica del cliente."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient'):
            cliente = ClienteTemperatura("192.168.1.100", 12000)

            assert cliente is not None

    def test_propiedades_host_port(self, qtbot):
        """Verifica getters de host y port."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient'):
            cliente = ClienteTemperatura("192.168.1.100", 12000)

            assert cliente.host == "192.168.1.100"
            assert cliente.port == 12000

    def test_crear_cliente_con_host_localhost(self, qtbot):
        """Verifica creación con localhost."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient'):
            cliente = ClienteTemperatura("localhost", 12000)

            assert cliente.host == "localhost"


class TestClienteTemperaturaEnvio:
    """Tests de envío de datos."""

    def test_enviar_temperatura_formato(self, cliente, mock_ephemeral_client):
        """Verifica formato correcto del mensaje."""
        cliente.enviar_temperatura(23.5)

        mock_ephemeral_client.send.assert_called_once_with("23.50")

    def test_enviar_temperatura_formato_negativo(self, cliente, mock_ephemeral_client):
        """Verifica formato con temperatura negativa."""
        cliente.enviar_temperatura(-5.75)

        mock_ephemeral_client.send.assert_called_once_with("-5.75")

    def test_enviar_temperatura_exitoso_retorna_true(self, cliente, mock_ephemeral_client):
        """Verifica que retorna True en envío exitoso."""
        mock_ephemeral_client.send.return_value = True

        resultado = cliente.enviar_temperatura(20.0)

        assert resultado is True

    def test_enviar_temperatura_fallido_retorna_false(self, cliente, mock_ephemeral_client):
        """Verifica que retorna False en envío fallido."""
        mock_ephemeral_client.send.return_value = False

        resultado = cliente.enviar_temperatura(20.0)

        assert resultado is False

    def test_enviar_estado(self, cliente, mock_ephemeral_client):
        """Verifica envío desde EstadoTemperatura."""
        estado = EstadoTemperatura(temperatura=25.5)

        cliente.enviar_estado(estado)

        mock_ephemeral_client.send.assert_called_once_with("25.50")

    def test_enviar_estado_retorna_resultado(self, cliente, mock_ephemeral_client):
        """Verifica que enviar_estado retorna resultado correcto."""
        mock_ephemeral_client.send.return_value = True
        estado = EstadoTemperatura(temperatura=25.5)

        resultado = cliente.enviar_estado(estado)

        assert resultado is True


class TestClienteTemperaturaEnvioAsync:
    """Tests de envío asíncrono."""

    def test_enviar_temperatura_async(self, cliente, mock_ephemeral_client):
        """Verifica envío asíncrono."""
        cliente.enviar_temperatura_async(30.0)

        mock_ephemeral_client.send_async.assert_called_once_with("30.00")

    def test_enviar_estado_async(self, cliente, mock_ephemeral_client):
        """Verifica envío asíncrono desde EstadoTemperatura."""
        estado = EstadoTemperatura(temperatura=28.5)

        cliente.enviar_estado_async(estado)

        mock_ephemeral_client.send_async.assert_called_once_with("28.50")


class TestClienteTemperaturaSignals:
    """Tests de señales Qt."""

    def test_signal_dato_enviado(self, qtbot):
        """Verifica emisión de señal dato_enviado."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
            mock_instance = MagicMock()
            mock_instance.send.return_value = True
            mock_class.return_value = mock_instance

            cliente = ClienteTemperatura("127.0.0.1", 12000)
            cliente._ultimo_valor = 23.5

            with qtbot.waitSignal(cliente.dato_enviado, timeout=1000) as blocker:
                cliente._on_data_sent()

            assert blocker.args[0] == 23.5

    def test_signal_error_conexion(self, qtbot):
        """Verifica emisión de señal error_conexion."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
            mock_class.return_value = MagicMock()

            cliente = ClienteTemperatura("127.0.0.1", 12000)

            with qtbot.waitSignal(cliente.error_conexion, timeout=1000) as blocker:
                cliente._on_error("Connection refused")

            assert blocker.args[0] == "Connection refused"


class TestClienteTemperaturaIntegracion:
    """Tests de integración con EphemeralSocketClient."""

    def test_usa_ephemeral_socket_client(self, qtbot):
        """Verifica que usa EphemeralSocketClient internamente."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
            cliente = ClienteTemperatura("127.0.0.1", 12000)

            # Verificar que se creó con los parámetros correctos
            call_args = mock_class.call_args
            assert call_args[0][0] == "127.0.0.1"
            assert call_args[0][1] == 12000

    def test_conecta_signals_del_cliente_interno(self, qtbot):
        """Verifica que conecta las señales del cliente interno."""
        with patch('app.comunicacion.cliente_temperatura.EphemeralSocketClient') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            ClienteTemperatura("127.0.0.1", 12000)

            # Verifica que se conectaron las señales
            mock_instance.data_sent.connect.assert_called_once()
            mock_instance.error_occurred.connect.assert_called_once()
