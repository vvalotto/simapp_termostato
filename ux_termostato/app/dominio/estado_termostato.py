"""
Modelo de dominio que representa el estado completo del termostato.

Este módulo define el modelo inmutable EstadoTermostato que contiene
toda la información del estado del sistema recibida desde el Raspberry Pi.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EstadoTermostato:
    """
    Estado completo del termostato.

    Representa el estado del sistema recibido desde el Raspberry Pi vía JSON.
    Es inmutable para garantizar que cada actualización crea un nuevo objeto.

    Attributes:
        temperatura_actual: Temperatura medida por el sensor (-40°C a 85°C)
        temperatura_deseada: Temperatura objetivo configurada (15°C a 35°C)
        modo_climatizador: Estado actual del sistema de climatización
            ("calentando" | "enfriando" | "reposo" | "apagado")
        falla_sensor: Indica si hay falla en el sensor de temperatura
        bateria_baja: Indica si la batería del sistema está baja
        encendido: Indica si el termostato está encendido
        modo_display: Modo de visualización en el display
            ("ambiente" | "deseada")
        timestamp: Marca de tiempo del estado

    Raises:
        ValueError: Si algún valor está fuera del rango permitido o es inválido
    """

    temperatura_actual: float
    temperatura_deseada: float
    modo_climatizador: str
    falla_sensor: bool
    bateria_baja: bool
    encendido: bool
    modo_display: str
    timestamp: datetime

    def __post_init__(self):
        """
        Valida los valores del estado después de la inicialización.

        Raises:
            ValueError: Si algún valor está fuera del rango o es inválido
        """
        # Validar temperatura actual (rango del sensor)
        if not -40 <= self.temperatura_actual <= 85:
            raise ValueError(
                f"temperatura_actual fuera de rango (-40 a 85°C): "
                f"{self.temperatura_actual}"
            )

        # Validar temperatura deseada (rango operativo)
        if not 15 <= self.temperatura_deseada <= 35:
            raise ValueError(
                f"temperatura_deseada fuera de rango (15 a 35°C): "
                f"{self.temperatura_deseada}"
            )

        # Validar modo climatizador
        modos_validos = {"calentando", "enfriando", "reposo", "apagado"}
        if self.modo_climatizador not in modos_validos:
            raise ValueError(
                f"modo_climatizador inválido: {self.modo_climatizador}. "
                f"Debe ser uno de: {modos_validos}"
            )

        # Validar modo display
        modos_display_validos = {"ambiente", "deseada"}
        if self.modo_display not in modos_display_validos:
            raise ValueError(
                f"modo_display inválido: {self.modo_display}. "
                f"Debe ser uno de: {modos_display_validos}"
            )

    @classmethod
    def from_json(cls, data: dict) -> "EstadoTermostato":
        """
        Crea una instancia desde un diccionario JSON recibido del RPi.

        Args:
            data: Diccionario con los datos del estado

        Returns:
            Instancia de EstadoTermostato

        Raises:
            ValueError: Si falta algún campo requerido o el formato es inválido
            KeyError: Si falta un campo requerido
        """
        # Parsear timestamp - puede venir como string ISO o datetime
        timestamp = data["timestamp"]
        if isinstance(timestamp, str):
            # Parsear string ISO 8601
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        return cls(
            temperatura_actual=float(data["temperatura_actual"]),
            temperatura_deseada=float(data["temperatura_deseada"]),
            modo_climatizador=str(data["modo_climatizador"]),
            falla_sensor=bool(data["falla_sensor"]),
            bateria_baja=bool(data["bateria_baja"]),
            encendido=bool(data["encendido"]),
            modo_display=str(data["modo_display"]),
            timestamp=timestamp,
        )

    def to_dict(self) -> dict:
        """
        Convierte el estado a un diccionario para logging/debugging.

        Returns:
            dict: Representación del estado como diccionario
        """
        return {
            "temperatura_actual": self.temperatura_actual,
            "temperatura_deseada": self.temperatura_deseada,
            "modo_climatizador": self.modo_climatizador,
            "falla_sensor": self.falla_sensor,
            "bateria_baja": self.bateria_baja,
            "encendido": self.encendido,
            "modo_display": self.modo_display,
            "timestamp": self.timestamp.isoformat(),
        }
