"""
Tests unitarios para PersistentSocketClient (anteriormente BaseSocketClient).

Usa mocks para simular el comportamiento del socket sin necesidad
de un servidor real.

Note:
    BaseSocketClient es ahora un alias de PersistentSocketClient.
    Estos tests verifican ambos nombres por compatibilidad.
"""
import socket
from unittest.mock import Mock, patch, MagicMock

import pytest

from compartido.networking import (
    BaseSocketClient,
    PersistentSocketClient,
    SocketClientBase,
)


@pytest.fixture
def app(qapp):
    """Fixture que proporciona la aplicación Qt."""
    return qapp


@pytest.fixture
def client():
    """Fixture que crea un cliente persistente."""
    return PersistentSocketClient("127.0.0.1", 12000)


class TestBackwardsCompatibility:
    """Tests de compatibilidad hacia atrás."""

    def test_base_socket_client_is_persistent(self):
        """Verifica que BaseSocketClient sea alias de PersistentSocketClient."""
        assert BaseSocketClient is PersistentSocketClient

    def test_persistent_inherits_from_base(self):
        """Verifica la jerarquía de herencia."""
        client = PersistentSocketClient("127.0.0.1", 12000)
        assert isinstance(client, SocketClientBase)


class TestPersistentSocketClientInit:
    """Tests de inicialización."""

    def test_init_sets_host_and_port(self, client):
        """Verifica que host y port se configuren correctamente."""
        assert client.host == "127.0.0.1"
        assert client.port == 12000

    def test_init_not_connected(self, client):
        """Verifica que el cliente inicie desconectado."""
        assert client.is_connected() is False

    def test_init_with_custom_values(self):
        """Verifica inicialización con valores personalizados."""
        client = PersistentSocketClient("192.168.1.100", 14001)
        assert client.host == "192.168.1.100"
        assert client.port == 14001


class TestPersistentSocketClientConnection:
    """Tests de conexión."""

    def test_connect_emits_connected_signal(self, client, app, qtbot):
        """Verifica que se emita señal connected al conectar."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

    def test_connect_refused_emits_error(self, client, app, qtbot):
        """Verifica que conexión rechazada emita error."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.connect.side_effect = ConnectionRefusedError()
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.error_occurred, timeout=2000) as blocker:
                client.connect_to_server()

            assert "rechazada" in blocker.args[0].lower()

    def test_connect_timeout_emits_error(self, client, app, qtbot):
        """Verifica que timeout emita error."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.connect.side_effect = socket.timeout()
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.error_occurred, timeout=2000) as blocker:
                client.connect_to_server()

            assert "timeout" in blocker.args[0].lower()

    def test_is_connected_returns_true_after_connect(self, client, app, qtbot):
        """Verifica is_connected después de conectar."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

            assert client.is_connected() is True


class TestPersistentSocketClientSendData:
    """Tests de envío de datos."""

    def test_send_data_returns_false_when_not_connected(self, client):
        """Verifica que send_data retorne False si no está conectado."""
        result = client.send_data("test")
        assert result is False

    def test_send_data_returns_true_on_success(self, client, app, qtbot):
        """Verifica que send_data retorne True al enviar exitosamente."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

            result = client.send_data("23.5")
            assert result is True
            mock_socket.sendall.assert_called_once_with(b"23.5")

    def test_send_data_emits_error_on_failure(self, client, app, qtbot):
        """Verifica que error de envío emita señal."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

            mock_socket.sendall.side_effect = OSError("Connection lost")

            with qtbot.waitSignal(client.error_occurred, timeout=2000):
                client.send_data("test")


class TestPersistentSocketClientDisconnect:
    """Tests de desconexión."""

    def test_disconnect_when_not_connected(self, client):
        """Verifica que disconnect sea seguro sin conexión."""
        client.disconnect()
        assert client.is_connected() is False

    def test_disconnect_emits_signal(self, client, app, qtbot):
        """Verifica que disconnect emita señal disconnected."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

            with qtbot.waitSignal(client.disconnected, timeout=2000):
                client.disconnect()

            assert client.is_connected() is False


class TestPersistentSocketClientReceive:
    """Tests de recepción de datos."""

    def test_receive_returns_none_when_not_connected(self, client):
        """Verifica que receive retorne None si no está conectado."""
        result = client.receive_data()
        assert result is None

    def test_receive_returns_data(self, client, app, qtbot):
        """Verifica que receive retorne los datos recibidos."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket.recv.return_value = b"ambiente: 23.5"
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

            result = client.receive_data()
            assert result == "ambiente: 23.5"

    def test_receive_emits_data_received_signal(self, client, app, qtbot):
        """Verifica que receive emita señal data_received."""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket.recv.return_value = b"test data"
            mock_socket_class.return_value = mock_socket

            with qtbot.waitSignal(client.connected, timeout=2000):
                client.connect_to_server()

            with qtbot.waitSignal(client.data_received, timeout=2000) as blocker:
                client.receive_data()

            assert blocker.args[0] == "test data"


class TestPersistentSocketClientIntegration:
    """Tests de integración con servidor real."""

    @pytest.mark.skip(reason="Requiere ISSE_Termostato ejecutándose")
    def test_real_connection_to_termostato(self, app, qtbot):
        """Test de integración real con ISSE_Termostato."""
        client = PersistentSocketClient("127.0.0.1", 12000)

        with qtbot.waitSignal(client.connected, timeout=5000):
            client.connect_to_server()

        assert client.is_connected() is True

        result = client.send_data("25.0")
        assert result is True

        client.disconnect()
        assert client.is_connected() is False
