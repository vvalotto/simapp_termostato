"""
Cliente TCP para enviar comandos al termostato en el Raspberry Pi.

Este cliente usa el patrón efímero (conectar → enviar → cerrar) para enviar
comandos JSON al termostato. Cada comando se envía en una conexión nueva.
"""
import json
import logging
from typing import Optional

from PyQt6.QtCore import QObject

from compartido.networking import EphemeralSocketClient
from ..dominio import ComandoTermostato

logger = logging.getLogger(__name__)


class ClienteComandos(QObject):
    """
    Cliente TCP para enviar comandos al termostato en el Raspberry Pi.

    Responsabilidades:
    - Enviar comandos JSON al RPi (puerto configurado, default 14000)
    - Serializar objetos ComandoTermostato a JSON
    - Patrón fire-and-forget (no espera respuesta)
    - Manejo robusto de errores (no lanza excepciones)

    El cliente encapsula un EphemeralSocketClient y se enfoca en la
    serialización de comandos y logging apropiado.

    Example:
        >>> cliente = ClienteComandos("192.168.1.50", 14000)
        >>> cmd = ComandoPower(estado=True)
        >>> exito = cliente.enviar_comando(cmd)
        >>> if exito:
        ...     print("Comando enviado")
    """

    def __init__(
        self,
        host: str,
        port: int = 14000,
        parent: Optional[QObject] = None
    ):
        """
        Inicializa el cliente de comandos.

        Args:
            host: Dirección IP del servidor RPi.
            port: Puerto TCP del servidor (default: 14000).
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._host = host
        self._port = port
        self._cliente = EphemeralSocketClient(host, port, self)

        logger.info(
            "ClienteComandos inicializado: %s:%d",
            host,
            port
        )

    @property
    def host(self) -> str:
        """Dirección IP del servidor RPi."""
        return self._host

    @property
    def port(self) -> int:
        """Puerto TCP del servidor."""
        return self._port

    def enviar_comando(self, cmd: ComandoTermostato) -> bool:
        """
        Envía un comando al termostato en el RPi.

        Este método serializa el comando a JSON, lo envía al RPi y retorna
        el resultado. Usa el patrón efímero: conectar → enviar → cerrar.

        No lanza excepciones - todos los errores son capturados y logueados.

        Args:
            cmd: Comando a enviar (ComandoPower, ComandoSetTemp, etc.)

        Returns:
            True si el comando se envió exitosamente, False si hubo error.

        Example:
            >>> cmd = ComandoSetTemp(valor=24.5)
            >>> exito = cliente.enviar_comando(cmd)
        """
        try:
            # 1. Serializar comando a JSON
            datos_json = cmd.to_json()
            tipo_comando = datos_json.get("comando", "desconocido")

            # 2. Convertir a string JSON + newline (protocolo)
            mensaje = json.dumps(datos_json) + "\n"

            logger.debug(
                "Enviando comando '%s' a %s:%d: %s",
                tipo_comando,
                self._host,
                self._port,
                datos_json
            )

            # 3. Enviar via cliente efímero (conectar → enviar → cerrar)
            exito = self._cliente.send(mensaje)

            if exito:
                logger.info(
                    "Comando '%s' enviado exitosamente a %s:%d",
                    tipo_comando,
                    self._host,
                    self._port
                )
            else:
                logger.error(
                    "Error al enviar comando '%s' a %s:%d",
                    tipo_comando,
                    self._host,
                    self._port
                )

            return exito

        except Exception as e:  # pylint: disable=broad-except
            # Catch-all: nunca lanzar excepciones al usuario
            logger.error(
                "Excepción al enviar comando a %s:%d: %s",
                self._host,
                self._port,
                e,
                exc_info=True
            )
            return False
