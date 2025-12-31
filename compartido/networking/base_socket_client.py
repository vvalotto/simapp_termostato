"""
Módulo de compatibilidad hacia atrás.

Este módulo mantiene la importación original funcionando.
Se recomienda usar las clases específicas:
    - PersistentSocketClient: Para conexiones de larga duración.
    - EphemeralSocketClient: Para conexiones efímeras.

Deprecated:
    BaseSocketClient será removido en una versión futura.
    Usar PersistentSocketClient o EphemeralSocketClient según el caso de uso.
"""
from .persistent_socket_client import PersistentSocketClient

# Alias para compatibilidad
BaseSocketClient = PersistentSocketClient

__all__ = ["BaseSocketClient"]
