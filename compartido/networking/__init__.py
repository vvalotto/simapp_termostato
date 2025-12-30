"""
Módulo de networking para ISSE_Simuladores.

Proporciona clases base para comunicación TCP con ISSE_Termostato.

Clases disponibles:
    Clientes:
    - SocketClientBase: Clase base abstracta con funcionalidad común.
    - PersistentSocketClient: Para conexiones de larga duración.
    - EphemeralSocketClient: Para conexiones efímeras (fire-and-forget).
    - BaseSocketClient: Alias de PersistentSocketClient (compatibilidad).

    Servidores:
    - SocketServerBase: Clase base abstracta para servidores.
    - ClientSession: Maneja comunicación con un cliente individual.
    - BaseSocketServer: Servidor TCP con soporte multi-cliente.
"""
from .socket_client_base import SocketClientBase
from .persistent_socket_client import PersistentSocketClient
from .ephemeral_socket_client import EphemeralSocketClient
from .socket_server_base import SocketServerBase
from .client_session import ClientSession
from .base_socket_server import BaseSocketServer

# Alias para compatibilidad hacia atrás
BaseSocketClient = PersistentSocketClient

__all__ = [
    # Clientes
    "SocketClientBase",
    "PersistentSocketClient",
    "EphemeralSocketClient",
    "BaseSocketClient",
    # Servidores
    "SocketServerBase",
    "ClientSession",
    "BaseSocketServer",
]
