"""Configuracion del Simulador de Temperatura."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json

from .constantes import (
    CONFIG_FILENAME,
    DEFAULT_IP,
    DEFAULT_PUERTO,
    DEFAULT_INTERVALO_MS,
    DEFAULT_TEMP_MIN,
    DEFAULT_TEMP_MAX,
    DEFAULT_TEMP_INICIAL,
    DEFAULT_RUIDO_AMPLITUD,
    DEFAULT_PASO_VARIACION,
    DEFAULT_VARIACION_AMPLITUD,
    DEFAULT_VARIACION_PERIODO,
)


@dataclass(frozen=True)
class ConfigSimuladorTemperatura:
    """Configuracion tipada del simulador de temperatura."""

    ip_raspberry: str
    puerto: int
    intervalo_envio_ms: int
    temperatura_minima: float
    temperatura_maxima: float
    temperatura_inicial: float
    ruido_amplitud: float
    paso_variacion: float
    variacion_amplitud: float
    variacion_periodo_segundos: float

    @classmethod
    def desde_defaults(cls) -> "ConfigSimuladorTemperatura":
        """Crea configuracion con valores por defecto."""
        return cls(
            ip_raspberry=DEFAULT_IP,
            puerto=DEFAULT_PUERTO,
            intervalo_envio_ms=DEFAULT_INTERVALO_MS,
            temperatura_minima=DEFAULT_TEMP_MIN,
            temperatura_maxima=DEFAULT_TEMP_MAX,
            temperatura_inicial=DEFAULT_TEMP_INICIAL,
            ruido_amplitud=DEFAULT_RUIDO_AMPLITUD,
            paso_variacion=DEFAULT_PASO_VARIACION,
            variacion_amplitud=DEFAULT_VARIACION_AMPLITUD,
            variacion_periodo_segundos=DEFAULT_VARIACION_PERIODO,
        )


class ConfigManager:
    """Singleton para gestionar la configuracion del simulador."""

    _instance: Optional["ConfigManager"] = None
    _config: Optional[ConfigSimuladorTemperatura] = None

    def __new__(cls) -> "ConfigManager":
        """Garantiza una unica instancia (Singleton)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def obtener_instancia(cls) -> "ConfigManager":
        """Obtiene la instancia unica del ConfigManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reiniciar(cls) -> None:
        """Reinicia el singleton (util para tests)."""
        cls._instance = None
        cls._config = None

    def cargar(self, ruta_config: Optional[Path] = None) -> ConfigSimuladorTemperatura:
        """Carga la configuracion desde config.json.

        Args:
            ruta_config: Ruta al archivo config.json. Si es None,
                        busca en el directorio raiz del proyecto.

        Returns:
            ConfigSimuladorTemperatura con los valores cargados.
        """
        if ruta_config is None:
            ruta_config = self._buscar_config_json()

        if ruta_config is not None and ruta_config.exists():
            self._config = self._cargar_desde_archivo(ruta_config)
        else:
            self._config = ConfigSimuladorTemperatura.desde_defaults()

        return self._config

    def _buscar_config_json(self) -> Optional[Path]:
        """Busca config.json subiendo desde el directorio actual."""
        directorio = Path(__file__).parent
        for _ in range(5):
            candidato = directorio / CONFIG_FILENAME
            if candidato.exists():
                return candidato
            directorio = directorio.parent
        return None

    def _cargar_desde_archivo(self, ruta: Path) -> ConfigSimuladorTemperatura:
        """Carga y parsea el archivo config.json."""
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)

        raspberry = datos.get("raspberry_pi", {})
        puertos = datos.get("puertos", {})
        simulador = datos.get("simulador_temperatura", {})

        return ConfigSimuladorTemperatura(
            ip_raspberry=raspberry.get("ip", DEFAULT_IP),
            puerto=puertos.get("temperatura", DEFAULT_PUERTO),
            intervalo_envio_ms=simulador.get("intervalo_envio_ms", DEFAULT_INTERVALO_MS),
            temperatura_minima=simulador.get("temperatura_minima", DEFAULT_TEMP_MIN),
            temperatura_maxima=simulador.get("temperatura_maxima", DEFAULT_TEMP_MAX),
            temperatura_inicial=simulador.get("temperatura_inicial", DEFAULT_TEMP_INICIAL),
            ruido_amplitud=simulador.get("ruido_amplitud", DEFAULT_RUIDO_AMPLITUD),
            paso_variacion=simulador.get("paso_variacion", DEFAULT_PASO_VARIACION),
            variacion_amplitud=simulador.get("variacion_amplitud", DEFAULT_VARIACION_AMPLITUD),
            variacion_periodo_segundos=simulador.get(
                "variacion_periodo_segundos", DEFAULT_VARIACION_PERIODO
            ),
        )

    @property
    def config(self) -> ConfigSimuladorTemperatura:
        """Obtiene la configuracion actual.

        Returns:
            ConfigSimuladorTemperatura cargada, o defaults si no se cargo.
        """
        if self._config is None:
            self._config = ConfigSimuladorTemperatura.desde_defaults()
        return self._config
