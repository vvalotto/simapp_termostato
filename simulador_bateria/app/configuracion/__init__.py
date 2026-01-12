"""Módulo de configuración del simulador de batería.

Contiene:
- ConfigSimuladorBateria: Dataclass con parámetros del simulador
- ConfigManager: Carga configuración desde config.json y .env
"""
from .config import ConfigSimuladorBateria, ConfigManager
from .constantes import (
    VOLTAJE_ABSOLUTO_MIN,
    VOLTAJE_ABSOLUTO_MAX,
)

__all__ = [
    "ConfigSimuladorBateria",
    "ConfigManager",
    "VOLTAJE_ABSOLUTO_MIN",
    "VOLTAJE_ABSOLUTO_MAX",
]
