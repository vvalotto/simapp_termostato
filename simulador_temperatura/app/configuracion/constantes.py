"""Constantes del Simulador de Temperatura."""

# Limites tecnicos del sensor NTC
TEMP_ABSOLUTA_MIN: float = -40.0  # Celsius
TEMP_ABSOLUTA_MAX: float = 125.0  # Celsius

# Valores por defecto (si no hay config.json)
DEFAULT_IP: str = "192.168.1.100"
DEFAULT_PUERTO: int = 12000
DEFAULT_INTERVALO_MS: int = 1000
DEFAULT_TEMP_MIN: float = -10.0
DEFAULT_TEMP_MAX: float = 50.0
DEFAULT_TEMP_INICIAL: float = 20.0
DEFAULT_RUIDO_AMPLITUD: float = 0.5
DEFAULT_PASO_VARIACION: float = 0.1

# Rutas
CONFIG_FILENAME: str = "config.json"
