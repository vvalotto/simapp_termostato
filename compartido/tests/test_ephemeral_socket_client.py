"""
Tests unitarios para EphemeralSocketClient.

Usa mocks para simular el comportamiento del socket sin necesidad
de un servidor real.
"""
import socket
from unittest.mock import Mock, patch, MagicMock

import pytest

from compartido.networking import EphemeralSocketClient, SocketClientBase


@pytest.fixture
def app(qapp):
    """Fixture que proporciona la aplicación Qt."""
    return qapp


@pytest.fixture
def client():
    """Fixture que crea un cliente efímero."""
    return EphemeralSocketClient("127.0.0.1", 12000)


class TestEphemeralSocketClientInit:
    """Tests de inicialización."""

    def test_init_sets_host_and_port(self, client):
        """Verifica que host y port se configuren correctamente."""
        assert client.host == "127.0.0.1"
        assert client.port == 12000

    def test_inherits_from_socket_client_base(self, client):
        """Verifica la jerarquía de herencia."""
        assert isinstance(client, SocketClientBase)

    def test_has_data_sent_signal(self, client):
        """Verifica que tenga la señal data_sent."""
        assert hasattr(client, "data_sent")

    def test_has_error_occurred_signal(self, client):
        """Verifica que tenga la señal error_occurred."""
        assert hasattr(client, "error_occurred")

    def test_no_connected_signal(self, client):
        """Verifica que NO tenga señal connected (es efímero)."""
        # EphemeralSocketClient no debe tener connected porque
        # la conexión se cierra inmediatamente después de enviar
        assert not hasattr(client, "connected") or \
               "connected" not in type(client).__dict__


class TestEphemeralSocketClientSend:
    """Tests del método send síncrono."""

    def test_send_returns_true_on_success(self, client):
        """Verifica que send retorne True al enviar exitosamente."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_create.return_value = mock_socket

            result = client.send("23.5")

            assert result is True
            mock_socket.connect.assert_called_once_with(("127.0.0.1", 12000))
            mock_socket.sendall.assert_called_once_with(b"23.5")

    def test_send_emits_data_sent_signal(self, client, app, qtbot):
        """Verifica que send emita señal data_sent."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.data_sent, timeout=1000):
                client.send("test data")

    def test_send_returns_false_on_connection_refused(self, client):
        """Verifica que send retorne False si conexión rechazada."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_socket.connect.side_effect = ConnectionRefusedError()
            mock_create.return_value = mock_socket

            result = client.send("test")

            assert result is False

    def test_send_emits_error_on_connection_refused(self, client, app, qtbot):
        """Verifica que conexión rechazada emita error."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_socket.connect.side_effect = ConnectionRefusedError()
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.error_occurred, timeout=1000) as blocker:
                client.send("test")

            assert "rechazada" in blocker.args[0].lower()

    def test_send_returns_false_on_timeout(self, client):
        """Verifica que send retorne False en timeout."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_socket.connect.side_effect = socket.timeout()
            mock_create.return_value = mock_socket

            result = client.send("test")

            assert result is False

    def test_send_emits_error_on_timeout(self, client, app, qtbot):
        """Verifica que timeout emita error."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_socket.connect.side_effect = socket.timeout()
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.error_occurred, timeout=1000) as blocker:
                client.send("test")

            assert "timeout" in blocker.args[0].lower()

    def test_send_handles_os_error(self, client, app, qtbot):
        """Verifica manejo de OSError genérico."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_socket.connect.side_effect = OSError("Network unreachable")
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.error_occurred, timeout=1000) as blocker:
                result = client.send("test")

            assert result is False
            assert "error" in blocker.args[0].lower()


class TestEphemeralSocketClientSendAsync:
    """Tests del método send_async."""

    def test_send_async_emits_data_sent(self, client, app, qtbot):
        """Verifica que send_async emita data_sent en éxito."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.data_sent, timeout=2000):
                client.send_async("23.5")

    def test_send_async_emits_error_on_failure(self, client, app, qtbot):
        """Verifica que send_async emita error en fallo."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_socket.connect.side_effect = ConnectionRefusedError()
            mock_create.return_value = mock_socket

            with qtbot.waitSignal(client.error_occurred, timeout=2000):
                client.send_async("test")


class TestEphemeralSocketClientUseCases:
    """Tests de casos de uso típicos."""

    def test_multiple_sends_create_new_connections(self, client):
        """Verifica que cada send cree una nueva conexión."""
        call_count = 0

        def count_calls():
            nonlocal call_count
            call_count += 1
            mock = MagicMock()
            mock.__enter__ = Mock(return_value=mock)
            mock.__exit__ = Mock(return_value=False)
            return mock

        with patch.object(client, "_create_socket", side_effect=count_calls):
            client.send("23.5")
            client.send("24.0")
            client.send("24.5")

        assert call_count == 3

    def test_send_temperature_value(self, client, app, qtbot):
        """Caso de uso: enviar valor de temperatura al termostato."""
        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_create.return_value = mock_socket

            # Simular envío de temperatura como float string
            result = client.send("23.5")

            assert result is True
            mock_socket.sendall.assert_called_with(b"23.5")

    def test_send_battery_voltage(self, app, qtbot):
        """Caso de uso: enviar voltaje de batería."""
        client = EphemeralSocketClient("127.0.0.1", 11000)

        with patch.object(client, "_create_socket") as mock_create:
            mock_socket = MagicMock()
            mock_socket.__enter__ = Mock(return_value=mock_socket)
            mock_socket.__exit__ = Mock(return_value=False)
            mock_create.return_value = mock_socket

            result = client.send("3.7")

            assert result is True
            mock_socket.connect.assert_called_with(("127.0.0.1", 11000))


class TestEphemeralSocketClientIntegration:
    """Tests de integración con servidor real."""

    @pytest.mark.skip(reason="Requiere ISSE_Termostato ejecutándose")
    def test_real_send_to_termostato(self, app, qtbot):
        """Test de integración real con ISSE_Termostato."""
        client = EphemeralSocketClient("127.0.0.1", 12000)

        with qtbot.waitSignal(client.data_sent, timeout=5000):
            client.send("25.0")
