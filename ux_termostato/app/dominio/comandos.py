"""
Comandos del termostato para enviar al Raspberry Pi.

Este módulo define la jerarquía de comandos que representa las acciones
del usuario sobre el termostato. Cada comando se serializa a JSON para
ser enviado al RPi vía TCP.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ComandoTermostato(ABC):
    """
    Clase base abstracta para todos los comandos del termostato.

    Todos los comandos son inmutables y tienen un timestamp automático.
    Cada comando debe implementar su propia serialización a JSON.

    Attributes:
        timestamp: Marca de tiempo de creación del comando
    """

    timestamp: datetime = field(default_factory=datetime.now, kw_only=True)

    @abstractmethod
    def to_json(self) -> dict:
        """
        Serializa el comando a diccionario JSON para envío al RPi.

        Returns:
            dict: Representación JSON del comando
        """


@dataclass(frozen=True)
class ComandoPower(ComandoTermostato):
    """
    Comando para encender o apagar el termostato.

    Attributes:
        estado: True para encender, False para apagar
        timestamp: Marca de tiempo heredada de ComandoTermostato
    """

    estado: bool

    def to_json(self) -> dict:
        """
        Serializa el comando a JSON.

        Returns:
            dict: {"comando": "power", "estado": "on"|"off", "timestamp": ...}
        """
        return {
            "comando": "power",
            "estado": "on" if self.estado else "off",
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class ComandoSetTemp(ComandoTermostato):
    """
    Comando para ajustar la temperatura deseada.

    Attributes:
        valor: Temperatura deseada en grados Celsius (15-35°C)
        timestamp: Marca de tiempo heredada de ComandoTermostato

    Raises:
        ValueError: Si el valor está fuera del rango 15-35°C
    """

    valor: float

    def __post_init__(self):
        """
        Valida el rango de temperatura.

        Raises:
            ValueError: Si el valor está fuera del rango 15-35°C
        """
        if not 15 <= self.valor <= 35:
            raise ValueError(
                f"Temperatura fuera de rango (15-35°C): {self.valor}"
            )

    def to_json(self) -> dict:
        """
        Serializa el comando a JSON.

        Returns:
            dict: {"comando": "set_temp_deseada", "valor": X, "timestamp": ...}
        """
        return {
            "comando": "set_temp_deseada",
            "valor": self.valor,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class ComandoAumentar(ComandoTermostato):
    """
    Comando para aumentar la temperatura deseada.

    Este comando envía "aumentar" al RPi (puerto 13000).
    No incluye valor - el incremento lo decide ISSE_Termostato.

    Attributes:
        timestamp: Marca de tiempo heredada de ComandoTermostato
    """

    def to_json(self) -> dict:
        """
        Serializa el comando a JSON.

        Returns:
            dict: {"comando": "aumentar", "timestamp": ...}
        """
        return {
            "comando": "aumentar",
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class ComandoDisminuir(ComandoTermostato):
    """
    Comando para disminuir la temperatura deseada.

    Este comando envía "disminuir" al RPi (puerto 13000).
    No incluye valor - el decremento lo decide ISSE_Termostato.

    Attributes:
        timestamp: Marca de tiempo heredada de ComandoTermostato
    """

    def to_json(self) -> dict:
        """
        Serializa el comando a JSON.

        Returns:
            dict: {"comando": "disminuir", "timestamp": ...}
        """
        return {
            "comando": "disminuir",
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class ComandoSetModoDisplay(ComandoTermostato):
    """
    Comando para cambiar el modo de visualización del display.

    Attributes:
        modo: Modo de visualización ("ambiente" | "deseada")
        timestamp: Marca de tiempo heredada de ComandoTermostato

    Raises:
        ValueError: Si el modo no es válido
    """

    modo: str

    def __post_init__(self):
        """
        Valida el modo de display.

        Raises:
            ValueError: Si el modo no es "ambiente" o "deseada"
        """
        modos_validos = {"ambiente", "deseada"}
        if self.modo not in modos_validos:
            raise ValueError(
                f"Modo inválido: {self.modo}. "
                f"Debe ser uno de: {modos_validos}"
            )

    def to_json(self) -> dict:
        """
        Serializa el comando a JSON.

        Returns:
            dict: {"comando": "set_modo_display", "modo": "...", "timestamp": ...}
        """
        return {
            "comando": "set_modo_display",
            "modo": self.modo,
            "timestamp": self.timestamp.isoformat(),
        }
