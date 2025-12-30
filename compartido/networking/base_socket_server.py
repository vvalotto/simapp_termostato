"""
Servidor TCP base con integración PyQt6.

Orquesta la aceptación de conexiones y delega el manejo
de cada cliente a instancias de ClientSession.
"""
import socket
import threading
from typing import Optional, Dict

from PyQt6.QtCore import pyqtSignal

from .socket_server_base import SocketServerBase
from .client_session import ClientSession


class BaseSocketServer(SocketServerBase):
    """
    Servidor TCP que acepta múltiples clientes simultáneamente.

    Responsabilidad: Orquestar la aceptación de conexiones y
    gestionar el ciclo de vida de las sesiones de clientes.

    Delega la comunicación con cada cliente a ClientSession,
    aplicando el principio de responsabilidad única.

    Signals:
        started: Emitida cuando el servidor inicia correctamente.
        stopped: Emitida cuando el servidor se detiene.
        client_connected: Emitida cuando un cliente conecta (str: dirección).
        client_disconnected: Emitida cuando un cliente desconecta (str: dirección).
        data_received: Emitida cuando se reciben datos (str: datos).
        error_occurred: Emitida cuando ocurre un error (str: mensaje).

    Example:
        >>> server = BaseSocketServer("0.0.0.0", 14001)
        >>> server.data_received.connect(on_data)
        >>> server.start()
        >>> # ... recibir datos de ISSE_Termostato ...
        >>> server.stop()
    """

    # Señales específicas del servidor
    started = pyqtSignal()
    stopped = pyqtSignal()
    client_connected = pyqtSignal(str)
    client_disconnected = pyqtSignal(str)
    data_received = pyqtSignal(str)

    def __init__(
        self,
        host: str,
        port: int,
        parent=None
    ):
        """
        Inicializa el servidor TCP.

        Args:
            host: Dirección IP donde escuchar (ej: "0.0.0.0" para todas).
            port: Puerto TCP donde escuchar.
            parent: Objeto padre de Qt (opcional).
        """
        super().__init__(host, port, parent)
        self._server_socket: Optional[socket.socket] = None
        self._running = False
        self._accept_thread: Optional[threading.Thread] = None
        self._sessions: Dict[str, ClientSession] = {}
        self._session_threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def is_running(self) -> bool:
        """
        Verifica si el servidor está ejecutándose.

        Returns:
            True si el servidor está activo, False en caso contrario.
        """
        with self._lock:
            return self._running

    def start(self) -> bool:
        """
        Inicia el servidor en un hilo separado.

        Returns:
            True si el servidor inició correctamente, False si hubo error.
        """
        with self._lock:
            if self._running:
                return True

            try:
                self._server_socket = self._create_server_socket()
                self._server_socket.bind((self._host, self._port))
                self._server_socket.listen(self.BACKLOG)
                self._server_socket.settimeout(self.ACCEPT_TIMEOUT)
                self._running = True

            except OSError as e:
                self._cleanup_server_socket()
                self._handle_bind_error(e)
                return False

        self._start_accept_thread()
        self.started.emit()
        return True

    def stop(self) -> None:
        """
        Detiene el servidor y cierra todas las conexiones.

        Es seguro llamar este método aunque el servidor no esté activo.
        """
        with self._lock:
            if not self._running:
                return
            self._running = False

        self._cleanup_server_socket()
        self._wait_for_accept_thread()
        self._close_all_sessions()

        self.stopped.emit()

    def get_client_count(self) -> int:
        """
        Retorna el número de clientes conectados actualmente.

        Returns:
            Cantidad de clientes conectados.
        """
        with self._lock:
            return len(self._sessions)

    # --- Métodos de orquestación (privados) ---

    def _start_accept_thread(self) -> None:
        """Inicia el hilo que acepta conexiones."""
        self._accept_thread = threading.Thread(
            target=self._accept_loop,
            daemon=True
        )
        self._accept_thread.start()

    def _wait_for_accept_thread(self) -> None:
        """Espera a que termine el hilo de aceptación."""
        if self._accept_thread is not None:
            self._accept_thread.join(timeout=2.0)
            self._accept_thread = None

    def _accept_loop(self) -> None:
        """Bucle principal que acepta conexiones entrantes."""
        while self.is_running():
            try:
                client_socket, address = self._server_socket.accept()
                client_addr = f"{address[0]}:{address[1]}"
                self._handle_new_client(client_socket, client_addr)

            except socket.timeout:
                continue

            except OSError:
                break

    def _handle_new_client(
        self,
        client_socket: socket.socket,
        client_addr: str
    ) -> None:
        """
        Maneja la llegada de un nuevo cliente.

        Crea una ClientSession y la ejecuta en un hilo separado.

        Args:
            client_socket: Socket del cliente conectado.
            client_addr: Dirección del cliente (ip:puerto).
        """
        session = self._create_client_session(client_socket, client_addr)
        self._register_session(session, client_addr)
        self._start_session_thread(session, client_addr)
        self.client_connected.emit(client_addr)

    def _create_client_session(
        self,
        client_socket: socket.socket,
        client_addr: str
    ) -> ClientSession:
        """
        Factory method para crear sesiones de cliente.

        Puede ser sobrescrito para personalizar el tipo de sesión (DIP).

        Args:
            client_socket: Socket del cliente.
            client_addr: Dirección del cliente.

        Returns:
            Nueva instancia de ClientSession.
        """
        return ClientSession(client_socket, client_addr)

    def _register_session(self, session: ClientSession, client_addr: str) -> None:
        """Registra una sesión en el diccionario de sesiones activas."""
        with self._lock:
            self._sessions[client_addr] = session

    def _start_session_thread(
        self,
        session: ClientSession,
        client_addr: str
    ) -> None:
        """Inicia el hilo para manejar la sesión del cliente."""
        thread = threading.Thread(
            target=self._run_session,
            args=(session, client_addr),
            daemon=True
        )
        with self._lock:
            self._session_threads[client_addr] = thread
        thread.start()

    def _run_session(self, session: ClientSession, client_addr: str) -> None:
        """
        Ejecuta el bucle de recepción de una sesión.

        Args:
            session: Sesión del cliente.
            client_addr: Dirección del cliente.
        """
        try:
            # Bucle de recepción manejado directamente para evitar
            # problemas de señales entre hilos
            while self.is_running() and session.is_active():
                data = session.receive_once()
                if data:
                    self.data_received.emit(data)
        finally:
            session.close()
            self._unregister_session(client_addr)
            self.client_disconnected.emit(client_addr)

    def _unregister_session(self, client_addr: str) -> None:
        """Elimina una sesión del registro."""
        with self._lock:
            self._sessions.pop(client_addr, None)
            self._session_threads.pop(client_addr, None)

    def _close_all_sessions(self) -> None:
        """Cierra todas las sesiones activas."""
        with self._lock:
            sessions = list(self._sessions.values())

        for session in sessions:
            session.close()

        self._sessions.clear()
        self._session_threads.clear()

    def _cleanup_server_socket(self) -> None:
        """Cierra el socket del servidor de forma segura."""
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None

    def __del__(self):
        """Destructor: asegura que el servidor se detenga."""
        with self._lock:
            if self._running:
                self._running = False
                self._cleanup_server_socket()
