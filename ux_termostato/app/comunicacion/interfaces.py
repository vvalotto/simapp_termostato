"""Interfaces para la capa de comunicación de la UX del termostato.

Usa typing.Protocol para evitar conflictos de metaclass con QObject y
BaseSocketServer. Permite testear con mocks tipados sin necesitar TCP real.
"""
from typing import Protocol, runtime_checkable

from ..dominio import ComandoTermostato


@runtime_checkable
class IServidorEstado(Protocol):
    """Interfaz del servidor TCP que recibe estado del RPi.

    Desacopla el coordinator de la implementación concreta ServidorEstado.
    Cualquier clase que implemente iniciar/detener/esta_activo satisface
    este protocolo (structural subtyping), sin herencia explícita.
    """

    def iniciar(self) -> bool:
        """Inicia el servidor en un hilo separado."""
        ...

    def detener(self) -> None:
        """Detiene el servidor y cierra conexiones."""
        ...

    def esta_activo(self) -> bool:
        """Verifica si el servidor está ejecutándose."""
        ...


@runtime_checkable
class IClienteComandos(Protocol):
    """Interfaz del cliente TCP que envía comandos al RPi.

    Desacopla el coordinator de la implementación concreta ClienteComandos.
    """

    def enviar_comando(self, cmd: ComandoTermostato) -> bool:
        """Envía un comando al termostato en el RPi."""
        ...
