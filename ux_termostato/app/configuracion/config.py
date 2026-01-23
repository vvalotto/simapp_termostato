"""
Configuración de la aplicación UX Termostato.

Este módulo define la clase ConfigUX que encapsula toda la configuración
de la aplicación, incluyendo comunicación con el RPi y parámetros de UI.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConfigUX:
    """
    Configuración inmutable de la aplicación UX Termostato.

    Atributos:
        ip_raspberry: Dirección IP del Raspberry Pi
        puerto_recv: Puerto para recibir estado del RPi (14001)
        puerto_send: Puerto para enviar comandos al RPi (14000)
        intervalo_recepcion_ms: Intervalo de recepción de datos (ms)
        intervalo_actualizacion_ui_ms: Intervalo de actualización de UI (ms)
        temperatura_min_setpoint: Temperatura mínima configurable (°C)
        temperatura_max_setpoint: Temperatura máxima configurable (°C)
        temperatura_setpoint_inicial: Temperatura inicial (°C)
    """

    # Comunicación
    ip_raspberry: str
    puerto_recv: int  # Puerto para recibir estado (14001)
    puerto_send: int  # Puerto para enviar comandos (14000)

    # UI
    intervalo_recepcion_ms: int
    intervalo_actualizacion_ui_ms: int
    temperatura_min_setpoint: float
    temperatura_max_setpoint: float
    temperatura_setpoint_inicial: float

    def __post_init__(self) -> None:
        """Valida la configuración después de la inicialización."""
        # Validar puertos
        if not 1 <= self.puerto_recv <= 65535:
            raise ValueError(
                f"puerto_recv fuera de rango: {self.puerto_recv} (debe estar entre 1 y 65535)"
            )
        if not 1 <= self.puerto_send <= 65535:
            raise ValueError(
                f"puerto_send fuera de rango: {self.puerto_send} (debe estar entre 1 y 65535)"
            )

        # Validar intervalos
        if self.intervalo_recepcion_ms <= 0:
            raise ValueError(
                f"intervalo_recepcion_ms debe ser positivo: {self.intervalo_recepcion_ms}"
            )
        if self.intervalo_actualizacion_ui_ms <= 0:
            raise ValueError(
                f"intervalo_actualizacion_ui_ms debe ser positivo: "
                f"{self.intervalo_actualizacion_ui_ms}"
            )

        # Validar temperaturas
        if self.temperatura_min_setpoint >= self.temperatura_max_setpoint:
            raise ValueError(
                f"temperatura_min_setpoint ({self.temperatura_min_setpoint}) "
                f"debe ser menor que temperatura_max_setpoint ({self.temperatura_max_setpoint})"
            )

        if not (
            self.temperatura_min_setpoint
            <= self.temperatura_setpoint_inicial
            <= self.temperatura_max_setpoint
        ):
            raise ValueError(
                f"temperatura_setpoint_inicial ({self.temperatura_setpoint_inicial}) "
                f"debe estar entre {self.temperatura_min_setpoint} y "
                f"{self.temperatura_max_setpoint}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfigUX":
        """
        Crea una instancia de ConfigUX desde un diccionario.

        Este método parsea la estructura del config.json del proyecto.

        Args:
            data: Diccionario con la configuración completa del config.json

        Returns:
            Nueva instancia de ConfigUX

        Raises:
            KeyError: Si falta alguna clave requerida
            ValueError: Si los valores están fuera de rango

        Example:
            >>> import json
            >>> with open("config.json") as f:
            ...     data = json.load(f)
            >>> config = ConfigUX.from_dict(data)
        """
        return cls(
            ip_raspberry=data["raspberry_pi"]["ip"],
            puerto_recv=data["puertos"]["visualizador_temperatura"],
            puerto_send=data["puertos"]["selector_temperatura"],
            intervalo_recepcion_ms=data["ux_termostato"]["intervalo_recepcion_ms"],
            intervalo_actualizacion_ui_ms=data["ux_termostato"]["intervalo_actualizacion_ui_ms"],
            temperatura_min_setpoint=data["ux_termostato"]["temperatura_minima_setpoint"],
            temperatura_max_setpoint=data["ux_termostato"]["temperatura_maxima_setpoint"],
            temperatura_setpoint_inicial=data["ux_termostato"]["temperatura_setpoint_inicial"],
        )

    @classmethod
    def defaults(cls) -> "ConfigUX":
        """
        Crea una instancia con valores por defecto.

        Returns:
            ConfigUX con valores por defecto para testing/desarrollo
        """
        return cls(
            ip_raspberry="127.0.0.1",
            puerto_recv=14001,
            puerto_send=14000,
            intervalo_recepcion_ms=500,
            intervalo_actualizacion_ui_ms=100,
            temperatura_min_setpoint=15.0,
            temperatura_max_setpoint=30.0,
            temperatura_setpoint_inicial=22.0,
        )
