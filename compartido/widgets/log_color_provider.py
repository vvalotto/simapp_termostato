"""
Proveedores de colores para LogViewer.

Define el enum de niveles de log, el protocolo para proveer colores
y una implementación por defecto.
"""
# pylint: disable=unnecessary-ellipsis
from enum import Enum
from typing import Protocol

from PyQt6.QtGui import QColor  # pylint: disable=no-name-in-module


class LogLevel(Enum):
    """Niveles de log disponibles."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class LogColorProvider(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para proveedores de colores de log.

    Permite inyectar diferentes paletas de colores al LogViewer
    sin modificar la clase, cumpliendo con OCP/DIP.

    Example:
        class DarkThemeLogColors:
            def get_color(self, level: LogLevel) -> QColor:
                # Colores para tema oscuro
                ...

        viewer = LogViewer(color_provider=DarkThemeLogColors())
    """

    def get_color(self, level: LogLevel) -> QColor:
        """
        Retorna el color para un nivel de log.

        Args:
            level: Nivel del mensaje de log.

        Returns:
            QColor para el nivel especificado.
        """
        ...


class DefaultLogColorProvider:  # pylint: disable=too-few-public-methods
    """
    Proveedor de colores por defecto para LogViewer.

    Implementa colores estándar para cada nivel de log:
    - INFO: Blanco
    - WARNING: Amarillo
    - ERROR: Rojo
    - DEBUG: Gris claro
    """

    _COLORS = {
        LogLevel.INFO: QColor(255, 255, 255),      # Blanco
        LogLevel.WARNING: QColor(255, 255, 0),     # Amarillo
        LogLevel.ERROR: QColor(255, 100, 100),     # Rojo claro
        LogLevel.DEBUG: QColor(180, 180, 180),     # Gris claro
    }

    def get_color(self, level: LogLevel) -> QColor:
        """Retorna el color para el nivel de log especificado."""
        return QColor(self._COLORS.get(level, self._COLORS[LogLevel.INFO]))
