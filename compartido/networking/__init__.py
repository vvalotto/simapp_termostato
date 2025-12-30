"""
Módulo de networking para ISSE_Simuladores.

Proporciona clases base para comunicación TCP con ISSE_Termostato.

Clases disponibles:
    - SocketClientBase: Clase base abstracta con funcionalidad común.
    - PersistentSocketClient: Para conexiones de larga duración.
    - EphemeralSocketClient: Para conexiones efímeras (fire-and-forget).
    - BaseSocketClient: Alias de PersistentSocketClient (compatibilidad).
"""
from .socket_client_base import SocketClientBase
from .persistent_socket_client import PersistentSocketClient
from .ephemeral_socket_client import EphemeralSocketClient

# Alias para compatibilidad hacia atrás
BaseSocketClient = PersistentSocketClient

__all__ = [
    "SocketClientBase",
    "PersistentSocketClient",
    "EphemeralSocketClient",
    "BaseSocketClient",
]
