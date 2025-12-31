"""
Formateadores de mensajes para LogViewer.

Define el protocolo para formatear mensajes de log y una
implementación por defecto con timestamp.
"""
# pylint: disable=unnecessary-ellipsis
from datetime import datetime
from typing import Protocol

from .log_color_provider import LogLevel


class LogFormatter(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para formateadores de mensajes de log.

    Permite inyectar diferentes formatos de log sin modificar
    LogViewer, cumpliendo con OCP/DIP.

    Example:
        class CompactFormatter:
            def format(self, message: str, level: LogLevel) -> str:
                return f"[{level.value[0].upper()}] {message}"

        viewer = LogViewer(formatter=CompactFormatter())
    """

    def format(self, message: str, level: LogLevel, timestamp: datetime) -> str:
        """
        Formatea un mensaje de log.

        Args:
            message: Mensaje a formatear.
            level: Nivel del log.
            timestamp: Momento del log.

        Returns:
            Mensaje formateado como string.
        """
        ...


class TimestampLogFormatter:
    """
    Formateador de logs con timestamp.

    Formato por defecto: [HH:MM:SS] [LEVEL] mensaje

    Example:
        formatter = TimestampLogFormatter()
        text = formatter.format("Conexión establecida", LogLevel.INFO, datetime.now())
        # "[14:30:45] [INFO] Conexión establecida"
    """

    def __init__(
        self,
        time_format: str = "%H:%M:%S",
        show_level: bool = True
    ):
        """
        Inicializa el formateador.

        Args:
            time_format: Formato de strftime para el timestamp.
            show_level: Si mostrar el nivel en el formato.
        """
        self._time_format = time_format
        self._show_level = show_level

    def format(self, message: str, level: LogLevel, timestamp: datetime) -> str:
        """Formatea el mensaje con timestamp y nivel."""
        time_str = timestamp.strftime(self._time_format)

        if self._show_level:
            return f"[{time_str}] [{level.value.upper()}] {message}"
        return f"[{time_str}] {message}"

    @property
    def time_format(self) -> str:
        """Retorna el formato de tiempo actual."""
        return self._time_format

    @property
    def show_level(self) -> bool:
        """Retorna si se muestra el nivel."""
        return self._show_level
