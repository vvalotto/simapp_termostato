"""
Tests unitarios para BaseSocketServer.

Usa sockets reales en localhost para verificar el comportamiento
del servidor TCP.
"""
import socket
import time

import pytest

from compartido.networking import BaseSocketServer, SocketServerBase, ClientSession


@pytest.fixture
def app(qapp):
    """Fixture que proporciona la aplicación Qt."""
    return qapp


def get_free_port():
    """Obtiene un puerto libre del sistema."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def server():
    """Fixture que crea un servidor en puerto disponible."""
    port = get_free_port()
    srv = BaseSocketServer("127.0.0.1", port)
    yield srv
    srv.stop()


@pytest.fixture
def started_server(app, qtbot):
    """Fixture que crea y arranca un servidor."""
    port = get_free_port()
    srv = BaseSocketServer("127.0.0.1", port)
    srv.start()
    yield srv
    srv.stop()


class TestBaseSocketServerInit:
    """Tests de inicialización."""

    def test_init_sets_host_and_port(self):
        """Verifica que host y port se configuren correctamente."""
        server = BaseSocketServer("0.0.0.0", 14001)
        assert server.host == "0.0.0.0"
        assert server.port == 14001

    def test_init_not_running(self):
        """Verifica que el servidor inicie detenido."""
        server = BaseSocketServer("127.0.0.1", 14001)
        assert server.is_running() is False

    def test_init_zero_clients(self):
        """Verifica que inicie sin clientes."""
        server = BaseSocketServer("127.0.0.1", 14001)
        assert server.get_client_count() == 0


class TestBaseSocketServerStartStop:
    """Tests de inicio y detención."""

    def test_start_returns_true_on_success(self, app, qtbot):
        """Verifica que start retorne True al iniciar."""
        port = get_free_port()
        server = BaseSocketServer("127.0.0.1", port)

        try:
            result = server.start()
            assert result is True
            assert server.is_running() is True
        finally:
            server.stop()

    def test_start_emits_started_signal(self, app, qtbot):
        """Verifica que start emita señal started."""
        port = get_free_port()
        server = BaseSocketServer("127.0.0.1", port)

        try:
            with qtbot.waitSignal(server.started, timeout=2000):
                server.start()
        finally:
            server.stop()

    def test_start_twice_returns_true(self, app, qtbot):
        """Verifica que iniciar dos veces no cause error."""
        port = get_free_port()
        server = BaseSocketServer("127.0.0.1", port)

        try:
            server.start()
            result = server.start()  # Segunda vez
            assert result is True
        finally:
            server.stop()

    def test_stop_emits_stopped_signal(self, app, qtbot):
        """Verifica que stop emita señal stopped."""
        port = get_free_port()
        server = BaseSocketServer("127.0.0.1", port)
        server.start()

        with qtbot.waitSignal(server.stopped, timeout=2000):
            server.stop()

        assert server.is_running() is False

    def test_stop_when_not_running_is_safe(self):
        """Verifica que stop sea seguro sin estar corriendo."""
        server = BaseSocketServer("127.0.0.1", 14001)
        server.stop()  # No debe lanzar excepción
        assert server.is_running() is False

    def test_start_on_used_port_emits_error(self, app, qtbot):
        """Verifica error al iniciar en puerto ocupado."""
        port = get_free_port()

        # Ocupar el puerto
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        blocker.bind(("127.0.0.1", port))
        blocker.listen(1)

        try:
            server = BaseSocketServer("127.0.0.1", port)

            with qtbot.waitSignal(server.error_occurred, timeout=2000) as sig:
                result = server.start()

            assert result is False
            assert "error" in sig.args[0].lower()
        finally:
            blocker.close()


class TestBaseSocketServerClientConnection:
    """Tests de conexión de clientes."""

    def test_client_connect_emits_signal(self, started_server, app, qtbot):
        """Verifica que conexión de cliente emita señal."""
        with qtbot.waitSignal(
            started_server.client_connected, timeout=2000
        ) as blocker:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", started_server.port))
            time.sleep(0.1)

        assert "127.0.0.1" in blocker.args[0]
        client.close()

    def test_client_disconnect_emits_signal(self, started_server, app, qtbot):
        """Verifica que desconexión de cliente emita señal."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", started_server.port))
        time.sleep(0.1)

        with qtbot.waitSignal(
            started_server.client_disconnected, timeout=2000
        ):
            client.close()

    def test_client_count_increments(self, started_server, app, qtbot):
        """Verifica que el conteo de clientes aumente."""
        assert started_server.get_client_count() == 0

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", started_server.port))
        time.sleep(0.2)

        assert started_server.get_client_count() == 1

        client.close()
        time.sleep(0.2)

        assert started_server.get_client_count() == 0

    def test_multiple_clients_supported(self, started_server, app, qtbot):
        """Verifica soporte para múltiples clientes."""
        clients = []

        for _ in range(3):
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", started_server.port))
            clients.append(client)
            time.sleep(0.1)

        time.sleep(0.2)
        assert started_server.get_client_count() == 3

        for client in clients:
            client.close()


class TestBaseSocketServerDataReceive:
    """Tests de recepción de datos."""

    def test_receive_data_emits_signal(self, started_server, app, qtbot):
        """Verifica que datos recibidos emitan señal."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", started_server.port))
        time.sleep(0.1)

        with qtbot.waitSignal(
            started_server.data_received, timeout=2000
        ) as blocker:
            client.sendall(b"ambiente: 23.5")
            time.sleep(0.1)

        assert blocker.args[0] == "ambiente: 23.5"
        client.close()

    def test_receive_multiple_messages(self, started_server, app, qtbot):
        """Verifica recepción de múltiples mensajes."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", started_server.port))
        time.sleep(0.1)

        # Primer mensaje
        with qtbot.waitSignal(
            started_server.data_received, timeout=2000
        ) as blocker1:
            client.sendall(b"mensaje1")

        assert blocker1.args[0] == "mensaje1"

        # Segundo mensaje
        with qtbot.waitSignal(
            started_server.data_received, timeout=2000
        ) as blocker2:
            client.sendall(b"mensaje2")

        assert blocker2.args[0] == "mensaje2"
        client.close()

    def test_receive_from_multiple_clients(self, started_server, app, qtbot):
        """Verifica recepción desde múltiples clientes."""
        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client1.connect(("127.0.0.1", started_server.port))

        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2.connect(("127.0.0.1", started_server.port))

        time.sleep(0.1)

        # Mensaje desde cliente 1
        with qtbot.waitSignal(
            started_server.data_received, timeout=2000
        ) as blocker1:
            client1.sendall(b"desde_cliente_1")

        assert blocker1.args[0] == "desde_cliente_1"

        # Mensaje desde cliente 2
        with qtbot.waitSignal(
            started_server.data_received, timeout=2000
        ) as blocker2:
            client2.sendall(b"desde_cliente_2")

        assert blocker2.args[0] == "desde_cliente_2"

        client1.close()
        client2.close()


class TestBaseSocketServerUseCases:
    """Tests de casos de uso del sistema."""

    def test_receive_temperature_state(self, started_server, app, qtbot):
        """Caso de uso: recibir estado de temperatura de ISSE_Termostato."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", started_server.port))
        time.sleep(0.1)

        with qtbot.waitSignal(
            started_server.data_received, timeout=2000
        ) as blocker:
            # Simular envío de ISSE_Termostato
            client.sendall(b"ambiente: 23.5")

        assert "ambiente" in blocker.args[0]
        assert "23.5" in blocker.args[0]
        client.close()

    def test_receive_battery_state(self, app, qtbot):
        """Caso de uso: recibir estado de batería."""
        port = get_free_port()
        server = BaseSocketServer("127.0.0.1", port)
        server.start()

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", port))
            time.sleep(0.1)

            with qtbot.waitSignal(
                server.data_received, timeout=2000
            ) as blocker:
                client.sendall(b"75.5")

            assert blocker.args[0] == "75.5"
            client.close()
        finally:
            server.stop()


class TestSocketServerBase:
    """Tests para la clase base SocketServerBase."""

    def test_inherits_from_qobject(self):
        """Verifica herencia de QObject."""
        from PyQt6.QtCore import QObject
        server = SocketServerBase("127.0.0.1", 14001)
        assert isinstance(server, QObject)

    def test_has_error_signal(self):
        """Verifica que tenga señal error_occurred."""
        server = SocketServerBase("127.0.0.1", 14001)
        assert hasattr(server, "error_occurred")

    def test_create_server_socket(self):
        """Verifica que _create_server_socket cree un socket válido."""
        server = SocketServerBase("127.0.0.1", 14001)
        sock = server._create_server_socket()
        assert sock is not None
        assert sock.family == socket.AF_INET
        assert sock.type == socket.SOCK_STREAM
        sock.close()

    def test_constants_defined(self):
        """Verifica que las constantes estén definidas."""
        assert SocketServerBase.BUFFER_SIZE == 4096
        assert SocketServerBase.ENCODING == "utf-8"
        assert SocketServerBase.BACKLOG == 5


class TestClientSession:
    """Tests para la clase ClientSession."""

    @pytest.fixture
    def socket_pair(self):
        """Crea un par de sockets conectados para testing."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        server_sock.listen(1)
        port = server_sock.getsockname()[1]

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(("127.0.0.1", port))

        conn_sock, _ = server_sock.accept()
        server_sock.close()

        yield client_sock, conn_sock

        try:
            client_sock.close()
        except OSError:
            pass
        try:
            conn_sock.close()
        except OSError:
            pass

    def test_init_sets_address(self, socket_pair):
        """Verifica que la dirección se configure correctamente."""
        _, conn_sock = socket_pair
        session = ClientSession(conn_sock, "127.0.0.1:12345")
        assert session.address == "127.0.0.1:12345"

    def test_is_active_initially_true(self, socket_pair):
        """Verifica que la sesión inicie activa."""
        _, conn_sock = socket_pair
        session = ClientSession(conn_sock, "127.0.0.1:12345")
        assert session.is_active() is True

    def test_receive_once_returns_data(self, socket_pair, app, qtbot):
        """Verifica que receive_once retorne datos."""
        client_sock, conn_sock = socket_pair
        session = ClientSession(conn_sock, "127.0.0.1:12345")

        client_sock.sendall(b"test data")
        time.sleep(0.1)

        result = session.receive_once(timeout=2.0)
        assert result == "test data"

    def test_receive_once_emits_signal(self, socket_pair, app, qtbot):
        """Verifica que receive_once emita data_received."""
        client_sock, conn_sock = socket_pair
        session = ClientSession(conn_sock, "127.0.0.1:12345")

        with qtbot.waitSignal(session.data_received, timeout=2000) as blocker:
            client_sock.sendall(b"signal test")
            session.receive_once(timeout=2.0)

        assert blocker.args[0] == "signal test"

    def test_close_deactivates_session(self, socket_pair):
        """Verifica que close desactive la sesión."""
        _, conn_sock = socket_pair
        session = ClientSession(conn_sock, "127.0.0.1:12345")

        session.close()
        assert session.is_active() is False

    def test_disconnect_emits_signal(self, socket_pair, app, qtbot):
        """Verifica que desconexión emita señal."""
        client_sock, conn_sock = socket_pair
        session = ClientSession(conn_sock, "127.0.0.1:12345")

        with qtbot.waitSignal(session.disconnected, timeout=2000):
            client_sock.close()
            session.receive_once(timeout=1.0)


class TestBaseSocketServerInheritance:
    """Tests de herencia y composición."""

    def test_inherits_from_socket_server_base(self):
        """Verifica que BaseSocketServer herede de SocketServerBase."""
        server = BaseSocketServer("127.0.0.1", 14001)
        assert isinstance(server, SocketServerBase)

    def test_has_create_client_session_method(self):
        """Verifica que tenga el factory method para sesiones."""
        server = BaseSocketServer("127.0.0.1", 14001)
        assert hasattr(server, "_create_client_session")
        assert callable(server._create_client_session)
