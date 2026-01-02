"""
Modulo de configuracion del Simulador de Temperatura.

Proporciona:
    - ConfigSimuladorTemperatura: Dataclass con configuracion tipada
    - ConfigManager: Singleton para gestionar la configuracion
    - Constantes: Valores por defecto y limites tecnicos
"""
from .config import ConfigSimuladorTemperatura, ConfigManager
from .constantes import (
    TEMP_ABSOLUTA_MIN,
    TEMP_ABSOLUTA_MAX,
    DEFAULT_IP,
    DEFAULT_PUERTO,
    DEFAULT_INTERVALO_MS,
    DEFAULT_TEMP_MIN,
    DEFAULT_TEMP_MAX,
    DEFAULT_TEMP_INICIAL,
    DEFAULT_RUIDO_AMPLITUD,
    DEFAULT_PASO_VARIACION,
    CONFIG_FILENAME,
)

__all__ = [
    # Clases principales
    "ConfigSimuladorTemperatura",
    "ConfigManager",
    # Limites tecnicos
    "TEMP_ABSOLUTA_MIN",
    "TEMP_ABSOLUTA_MAX",
    # Valores por defecto
    "DEFAULT_IP",
    "DEFAULT_PUERTO",
    "DEFAULT_INTERVALO_MS",
    "DEFAULT_TEMP_MIN",
    "DEFAULT_TEMP_MAX",
    "DEFAULT_TEMP_INICIAL",
    "DEFAULT_RUIDO_AMPLITUD",
    "DEFAULT_PASO_VARIACION",
    # Rutas
    "CONFIG_FILENAME",
]
