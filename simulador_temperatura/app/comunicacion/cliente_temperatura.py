"""Cliente TCP para enviar valores de temperatura al ISSE_Termostato.

Implementa comunicación con el puerto 12000 del servidor de temperatura
usando el patrón efímero: conectar -> enviar -> cerrar.
"""
import logging
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from compartido.networking import EphemeralSocketClient
from ..dominio.estado_temperatura import EstadoTemperatura

logger = logging.getLogger(__name__)


class ClienteTemperatura(QObject):
    """Cliente TCP para enviar valores de temperatura simulados.

    Encapsula un EphemeralSocketClient para enviar valores de temperatura
    al servidor ISSE_Termostato en el puerto configurado (default 12000).

    El cliente usa el patrón efímero: cada envío crea una conexión nueva,
    envía el dato y cierra inmediatamente. Esto es compatible con el
    protocolo esperado por ProxySensorTemperatura en ISSE_Termostato.

    Signals:
        dato_enviado: Emitida cuando un valor se envía exitosamente.
            Parámetro: float con la temperatura enviada.
        error_conexion: Emitida cuando ocurre un error de conexión.
            Parámetro: str con el mensaje de error.

    Example:
        >>> cliente = ClienteTemperatura("127.0.0.1", 12000)
        >>> cliente.dato_enviado.connect(lambda t: print(f"Enviado: {t}"))
        >>> cliente.enviar_temperatura(23.5)
    """

    dato_enviado = pyqtSignal(float)
    error_conexion = pyqtSignal(str)

    def __init__(
        self,
        host: str,
        port: int,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el cliente de temperatura.

        Args:
            host: Dirección IP del servidor ISSE_Termostato.
            port: Puerto TCP del servidor (default 12000).
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
            "ClienteTemperatura inicializado: %s:%d",
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

    def enviar_temperatura(self, temperatura: float) -> bool:
        """Envía un valor de temperatura al servidor.

        Formatea el valor como string y lo envía usando el cliente efímero.
        El formato es compatible con ISSE_Termostato: "<float>".

        Args:
            temperatura: Valor de temperatura en grados Celsius.

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        self._ultimo_valor = temperatura
        mensaje = f"{temperatura:.2f}"

        logger.debug("Enviando temperatura: %s", mensaje)
        return self._cliente.send(mensaje)

    def enviar_temperatura_async(self, temperatura: float) -> None:
        """Envía un valor de temperatura de forma asíncrona.

        Similar a enviar_temperatura pero no bloquea. El resultado
        se comunica mediante las señales dato_enviado o error_conexion.

        Args:
            temperatura: Valor de temperatura en grados Celsius.
        """
        self._ultimo_valor = temperatura
        mensaje = f"{temperatura:.2f}"

        logger.debug("Enviando temperatura (async): %s", mensaje)
        self._cliente.send_async(mensaje)

    def enviar_estado(self, estado: EstadoTemperatura) -> bool:
        """Envía un EstadoTemperatura al servidor.

        Método conveniente que extrae la temperatura del estado
        y la envía al servidor.

        Args:
            estado: Objeto EstadoTemperatura con el valor a enviar.

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        return self.enviar_temperatura(estado.temperatura)

    def enviar_estado_async(self, estado: EstadoTemperatura) -> None:
        """Envía un EstadoTemperatura de forma asíncrona.

        Args:
            estado: Objeto EstadoTemperatura con el valor a enviar.
        """
        self.enviar_temperatura_async(estado.temperatura)

    def _on_data_sent(self) -> None:
        """Callback interno cuando los datos se envían exitosamente."""
        if self._ultimo_valor is not None:
            logger.info(
                "Temperatura enviada: %.2f°C -> %s:%d",
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
