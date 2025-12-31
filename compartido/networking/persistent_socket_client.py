"""
Cliente TCP para conexiones persistentes con integración PyQt6.

Implementa el patrón: conectar → enviar múltiples veces → desconectar.
Ideal para conexiones de larga duración donde se mantiene el socket abierto.
"""
import socket
import threading
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .socket_client_base import SocketClientBase


class PersistentSocketClient(SocketClientBase):
    """
    Cliente TCP para conexiones persistentes.

    Mantiene una conexión abierta con el servidor, permitiendo
    enviar y recibir múltiples mensajes antes de desconectar.

    Signals:
        connected: Emitida cuando se establece conexión con el servidor.
        disconnected: Emitida cuando se pierde o cierra la conexión.
        error_occurred: Emitida cuando ocurre un error (str: mensaje).
        data_received: Emitida cuando se reciben datos (str: datos).

    Example:
        >>> client = PersistentSocketClient("127.0.0.1", 14001)
        >>> client.connected.connect(on_connected)
        >>> client.data_received.connect(on_data)
        >>> client.connect_to_server()
        >>> # ... recibir múltiples mensajes ...
        >>> client.disconnect()
    """

    # Señales específicas de conexión persistente
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    data_received = pyqtSignal(str)

    def __init__(self, host: str, port: int, parent: Optional[QObject] = None):
        """
        Inicializa el cliente TCP persistente.

        Args:
            host: Dirección IP o hostname del servidor.
            port: Puerto TCP del servidor.
            parent: Objeto padre de Qt (opcional).
        """
        super().__init__(host, port, parent)
        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._lock = threading.Lock()

    def is_connected(self) -> bool:
        """
        Verifica si el cliente está conectado.

        Returns:
            True si hay una conexión activa, False en caso contrario.
        """
        with self._lock:
            return self._connected

    def connect_to_server(self) -> None:
        """
        Conecta al servidor en un hilo separado.

        La conexión se realiza de forma asíncrona. El resultado se
        comunica mediante las señales `connected` o `error_occurred`.
        """
        thread = threading.Thread(target=self._connect_thread, daemon=True)
        thread.start()

    def _connect_thread(self) -> None:
        """Hilo interno para realizar la conexión."""
        try:
            with self._lock:
                if self._connected:
                    return

                self._socket = self._create_socket()
                self._socket.connect((self._host, self._port))
                self._connected = True

            self.connected.emit()

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            self._cleanup_socket()
            self._handle_connection_error(e)

    def send_data(self, data: str) -> bool:
        """
        Envía datos al servidor de forma síncrona.

        Args:
            data: Cadena de texto a enviar.

        Returns:
            True si el envío fue exitoso, False en caso contrario.

        Note:
            Requiere una conexión activa establecida previamente.
        """
        with self._lock:
            if not self._connected or self._socket is None:
                return False

            try:
                self._socket.sendall(data.encode(self.ENCODING))
                return True

            except (OSError, socket.error) as e:
                self._connected = False
                self.error_occurred.emit(f"Error al enviar: {e}")
                self.disconnected.emit()
                return False

    def send_data_async(self, data: str) -> None:
        """
        Envía datos al servidor en un hilo separado.

        Args:
            data: Cadena de texto a enviar.

        Note:
            El resultado se comunica mediante señales.
        """
        thread = threading.Thread(
            target=self._send_thread,
            args=(data,),
            daemon=True
        )
        thread.start()

    def _send_thread(self, data: str) -> None:
        """Hilo interno para envío asíncrono."""
        self.send_data(data)

    def receive_data(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Recibe datos del servidor de forma síncrona.

        Args:
            timeout: Tiempo máximo de espera en segundos (opcional).

        Returns:
            Datos recibidos como string, o None si hay error/timeout.
        """
        with self._lock:
            if not self._connected or self._socket is None:
                return None

            try:
                if timeout is not None:
                    self._socket.settimeout(timeout)

                data = self._socket.recv(self.BUFFER_SIZE)

                if not data:
                    self._connected = False
                    self.disconnected.emit()
                    return None

                decoded = data.decode(self.ENCODING)
                self.data_received.emit(decoded)
                return decoded

            except socket.timeout:
                return None

            except (OSError, socket.error) as e:
                self._connected = False
                self.error_occurred.emit(f"Error al recibir: {e}")
                self.disconnected.emit()
                return None

    def disconnect(self) -> None:
        """
        Cierra la conexión con el servidor.

        Es seguro llamar este método aunque no haya conexión activa.
        """
        with self._lock:
            was_connected = self._connected
            self._cleanup_socket()
            self._connected = False

        if was_connected:
            self.disconnected.emit()

    def _cleanup_socket(self) -> None:
        """Limpia el socket de forma segura (debe llamarse con lock)."""
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

    def __del__(self):
        """Destructor: asegura que el socket se cierre."""
        # No emitir señales en destructor, solo limpiar recursos
        with self._lock:
            self._cleanup_socket()
            self._connected = False
