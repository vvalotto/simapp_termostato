"""Constantes del Simulador de Bateria."""

# Limites de voltaje (0-5V para slider manual)
VOLTAJE_ABSOLUTO_MIN: float = 0.0   # Volts
VOLTAJE_ABSOLUTO_MAX: float = 5.0   # Volts

# Valores por defecto (si no hay config.json)
DEFAULT_IP: str = "192.168.1.100"
DEFAULT_PUERTO: int = 11000
DEFAULT_INTERVALO_MS: int = 1000
DEFAULT_VOLTAJE_MIN: float = 0.0
DEFAULT_VOLTAJE_MAX: float = 5.0
DEFAULT_VOLTAJE_INICIAL: float = 2.5

# Rutas
CONFIG_FILENAME: str = "config.json"
