"""Cliente TCP para enviar valores de voltaje al ISSE_Termostato.

Implementa comunicación con el puerto 11000 del servidor de batería
usando el patrón efímero: conectar -> enviar -> cerrar.
"""
import logging
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from compartido.networking import EphemeralSocketClient
from ..dominio.estado_bateria import EstadoBateria

logger = logging.getLogger(__name__)


class ClienteBateria(QObject):
    """Cliente TCP para enviar valores de voltaje simulados.

    Encapsula un EphemeralSocketClient para enviar valores de voltaje
    al servidor ISSE_Termostato en el puerto configurado (default 11000).

    El cliente usa el patrón efímero: cada envío crea una conexión nueva,
    envía el dato y cierra inmediatamente.

    Signals:
        dato_enviado: Emitida cuando un valor se envía exitosamente.
            Parámetro: float con el voltaje enviado.
        error_conexion: Emitida cuando ocurre un error de conexión.
            Parámetro: str con el mensaje de error.
    """

    dato_enviado = pyqtSignal(float)
    error_conexion = pyqtSignal(str)

    def __init__(
        self,
        host: str,
        port: int,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el cliente de batería.

        Args:
            host: Dirección IP del servidor ISSE_Termostato.
            port: Puerto TCP del servidor (default 11000).
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._host = host
        self._port = port
        self._cliente = EphemeralSocketClient(host, port, self)

        self._cliente.data_sent.connect(self._on_data_sent)
        self._cliente.error_occurred.connect(self._on_error)

        self._ultimo_valor: Optional[float] = None

        logger.info(
            "ClienteBateria inicializado: %s:%d",
            host, port
        )

    @property
    def host(self) -> str:
        """Dirección IP del servidor."""
        return self._host

    @property
    def port(self) -> int:
        """Puerto TCP del servidor."""
        return self._port

    def enviar_voltaje(self, voltaje: float) -> bool:
        """Envía un valor de voltaje al servidor.

        Formatea el valor como string y lo envía usando el cliente efímero.
        El formato es compatible con ISSE_Termostato: "<float>".

        Args:
            voltaje: Valor de voltaje en Volts.

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        self._ultimo_valor = voltaje
        mensaje = f"{voltaje:.2f}"

        logger.debug("Enviando voltaje: %s", mensaje)
        return self._cliente.send(mensaje)

    def enviar_voltaje_async(self, voltaje: float) -> None:
        """Envía un valor de voltaje de forma asíncrona.

        Similar a enviar_voltaje pero no bloquea. El resultado
        se comunica mediante las señales dato_enviado o error_conexion.

        Args:
            voltaje: Valor de voltaje en Volts.
        """
        self._ultimo_valor = voltaje
        mensaje = f"{voltaje:.2f}"

        logger.debug("Enviando voltaje (async): %s", mensaje)
        self._cliente.send_async(mensaje)

    def enviar_estado(self, estado: EstadoBateria) -> bool:
        """Envía un EstadoBateria al servidor.

        Método conveniente que extrae el voltaje del estado
        y lo envía al servidor.

        Args:
            estado: Objeto EstadoBateria con el valor a enviar.

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        return self.enviar_voltaje(estado.voltaje)

    def enviar_estado_async(self, estado: EstadoBateria) -> None:
        """Envía un EstadoBateria de forma asíncrona.

        Args:
            estado: Objeto EstadoBateria con el valor a enviar.
        """
        self.enviar_voltaje_async(estado.voltaje)

    def _on_data_sent(self) -> None:
        """Callback interno cuando los datos se envían exitosamente."""
        if self._ultimo_valor is not None:
            logger.info(
                "Voltaje enviado: %.2fV -> %s:%d",
                self._ultimo_valor, self._host, self._port
            )
            self.dato_enviado.emit(self._ultimo_valor)

    def _on_error(self, mensaje: str) -> None:
        """Callback interno cuando ocurre un error de conexión."""
        logger.error(
            "Error de conexión con %s:%d - %s",
            self._host, self._port, mensaje
        )
        self.error_conexion.emit(mensaje)
