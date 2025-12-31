"""
Sesión de cliente para servidores TCP.

Encapsula la comunicación con un cliente individual conectado.
Responsabilidad única: recibir datos de un cliente.
"""
import socket
from typing import Optional, Callable

from PyQt6.QtCore import QObject, pyqtSignal


class ClientSession(QObject):
    """
    Maneja la comunicación con un cliente TCP conectado.

    Encapsula el socket del cliente y proporciona métodos para
    recibir datos. Emite señales cuando hay datos o errores.

    Signals:
        data_received: Emitida cuando se reciben datos (str: datos).
        disconnected: Emitida cuando el cliente se desconecta.
        error_occurred: Emitida cuando ocurre un error (str: mensaje).

    Attributes:
        address (str): Dirección del cliente (ip:puerto).
    """

    # Señales
    data_received = pyqtSignal(str)
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)

    # Constantes
    BUFFER_SIZE = 4096
    ENCODING = "utf-8"
    DEFAULT_TIMEOUT = 1.0

    def __init__(
        self,
        client_socket: socket.socket,
        address: str,
        parent: Optional[QObject] = None
    ):
        """
        Inicializa la sesión del cliente.

        Args:
            client_socket: Socket conectado del cliente.
            address: Dirección del cliente (ip:puerto).
            parent: Objeto padre de Qt (opcional).
        """
        super().__init__(parent)
        self._socket = client_socket
        self._address = address
        self._active = True

    @property
    def address(self) -> str:
        """Retorna la dirección del cliente."""
        return self._address

    def is_active(self) -> bool:
        """
        Verifica si la sesión está activa.

        Returns:
            True si la sesión está activa, False si terminó.
        """
        return self._active

    def receive_once(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Intenta recibir datos una vez.

        Args:
            timeout: Tiempo máximo de espera (usa DEFAULT_TIMEOUT si None).

        Returns:
            Datos recibidos como string, o None si timeout/error.
        """
        if not self._active:
            return None

        try:
            self._socket.settimeout(timeout or self.DEFAULT_TIMEOUT)
            data = self._socket.recv(self.BUFFER_SIZE)

            if not data:
                # Cliente cerró la conexión
                self._active = False
                self.disconnected.emit()
                return None

            decoded = data.decode(self.ENCODING).strip()
            if decoded:
                self.data_received.emit(decoded)
            return decoded

        except socket.timeout:
            # Timeout normal, no es error
            return None

        except UnicodeDecodeError as e:
            self.error_occurred.emit(f"Error decodificando datos: {e}")
            return None

        except OSError as e:
            self._active = False
            self.error_occurred.emit(f"Error de socket: {e}")
            self.disconnected.emit()
            return None

    def run_receive_loop(self, should_continue: Callable[[], bool]) -> None:
        """
        Ejecuta un bucle de recepción hasta que se indique parar.

        Este método está diseñado para ejecutarse en un hilo separado.

        Args:
            should_continue: Función que retorna True mientras
                           el bucle debe continuar.
        """
        while should_continue() and self._active:
            self.receive_once()

        self.close()

    def close(self) -> None:
        """
        Cierra la sesión y el socket del cliente.

        Es seguro llamar múltiples veces.
        """
        if not self._active:
            return

        self._active = False

        try:
            self._socket.close()
        except OSError:
            pass

    def __del__(self):
        """Destructor: asegura que el socket se cierre."""
        try:
            self._socket.close()
        except (OSError, AttributeError):
            pass
