"""Interfaces para la capa de comunicación del simulador de batería.

Usa typing.Protocol para evitar conflictos de metaclass con QObject.
Permite testear con mocks tipados sin depender de EphemeralSocketClient.
"""
from typing import Protocol, runtime_checkable

from ..dominio.estado_bateria import EstadoBateria


@runtime_checkable
class IClienteBateria(Protocol):
    """Interfaz del cliente TCP para enviar voltajes al ISSE_Termostato.

    Desacopla ServicioEnvioBateria de la implementación concreta ClienteBateria.
    Cualquier clase que implemente enviar_voltaje y enviar_estado satisface
    este protocolo (structural subtyping), sin herencia explícita.
    """

    def enviar_voltaje(self, voltaje: float) -> bool:
        """Envía un valor de voltaje al servidor."""
        ...

    def enviar_estado(self, estado: EstadoBateria) -> bool:
        """Envía un EstadoBateria al servidor."""
        ...
