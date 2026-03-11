"""Interfaces para la capa de comunicación del simulador de temperatura.

Usa typing.Protocol para evitar conflictos de metaclass con QObject.
Permite testear con mocks tipados sin depender de EphemeralSocketClient.
"""
from typing import Protocol, runtime_checkable

from ..dominio.estado_temperatura import EstadoTemperatura


@runtime_checkable
class IClienteTemperatura(Protocol):
    """Interfaz del cliente TCP para enviar temperatura al ISSE_Termostato.

    Desacopla ServicioEnvioTemperatura de la implementación concreta
    ClienteTemperatura. Cualquier clase que implemente los métodos satisface
    este protocolo (structural subtyping), sin herencia explícita.
    """

    def enviar_temperatura(self, temperatura: float) -> bool:
        """Envía un valor de temperatura al servidor."""
        ...

    def enviar_estado(self, estado: EstadoTemperatura) -> bool:
        """Envía un EstadoTemperatura al servidor."""
        ...
