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
            port: Puerto TCP base (default: 14000, no usado con protocolo texto).
            parent: Objeto padre Qt opcional.

        Note:
            El puerto se determina dinámicamente según el tipo de comando:
            - Puerto 13000: comandos de temperatura (aumentar/disminuir)
            - Puerto 14000: selector de display (ambiente/deseada)
        """
        super().__init__(parent)
        self._host = host
        self._port = port  # Puerto base (no usado con protocolo adaptado)

        logger.info(
            "ClienteComandos inicializado: %s (puertos dinámicos)",
            host
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

        PROTOCOLO ADAPTADO: Envía texto plano (no JSON) compatible con ISSE_Termostato:
        - Puerto 13000: "aumentar" o "disminuir" (comandos de temperatura)
        - Puerto 14000: "ambiente" o "deseada" (selector de display)

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
            # 1. Serializar comando a JSON (formato interno)
            datos_json = cmd.to_json()
            tipo_comando = datos_json.get("comando", "desconocido")

            # 2. Adaptar a protocolo texto plano de ISSE_Termostato
            mensaje_texto, puerto = self._adaptar_comando_a_texto(datos_json)

            if mensaje_texto is None:
                logger.warning(
                    "Comando '%s' no soportado por protocolo texto plano",
                    tipo_comando
                )
                return False

            logger.debug(
                "Enviando comando '%s' a %s:%d (texto: '%s')",
                tipo_comando,
                self._host,
                puerto,
                mensaje_texto.strip()
            )

            # 3. Crear cliente efímero con puerto correcto
            cliente = EphemeralSocketClient(self._host, puerto, self)

            # 4. Enviar texto plano (conectar → enviar → cerrar)
            exito = cliente.send(mensaje_texto)

            if exito:
                logger.info(
                    "Comando '%s' enviado exitosamente a %s:%d",
                    tipo_comando,
                    self._host,
                    puerto
                )
            else:
                logger.error(
                    "Error al enviar comando '%s' a %s:%d",
                    tipo_comando,
                    self._host,
                    puerto
                )

            return exito

        except Exception as e:  # pylint: disable=broad-except
            # Catch-all: nunca lanzar excepciones al usuario
            logger.error(
                "Excepción al enviar comando: %s",
                e,
                exc_info=True
            )
            return False

    def _adaptar_comando_a_texto(self, datos_json: dict) -> tuple[Optional[str], int]:
        """
        Adapta un comando JSON al formato texto plano de ISSE_Termostato.

        Args:
            datos_json: Comando en formato JSON interno

        Returns:
            Tupla (mensaje_texto, puerto) o (None, 0) si el comando no es soportado

        Mapeo:
            - "aumentar"  → ("aumentar", 13000)
            - "disminuir" → ("disminuir", 13000)
            - "ambiente"  → ("ambiente", 14000)
            - "deseada"   → ("deseada", 14000)
            - "power"     → (None, 0) - NO soportado por ISSE_Termostato
        """
        tipo_comando = datos_json.get("comando", "")

        # Comandos de temperatura (puerto 13000)
        if tipo_comando in ("aumentar", "disminuir"):
            return (tipo_comando, 13000)

        # Selector de display (puerto 14000)
        if tipo_comando == "set_modo_display":
            modo = datos_json.get("modo", "")
            if modo in ("ambiente", "deseada"):
                return (modo, 14000)

        # Comando 'power' NO soportado (ISSE_Termostato no tiene endpoint)
        if tipo_comando == "power":
            logger.debug(
                "Comando 'power' omitido - ISSE_Termostato no tiene endpoint de encendido"
            )
            return (None, 0)

        # Comando desconocido/no soportado
        logger.warning("Comando '%s' no reconocido", tipo_comando)
        return (None, 0)
