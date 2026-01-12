"""Configuracion del Simulador de Bateria."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json

from .constantes import (
    CONFIG_FILENAME,
    DEFAULT_IP,
    DEFAULT_PUERTO,
    DEFAULT_INTERVALO_MS,
    DEFAULT_VOLTAJE_MIN,
    DEFAULT_VOLTAJE_MAX,
    DEFAULT_VOLTAJE_INICIAL,
)


@dataclass(frozen=True)
class ConfigSimuladorBateria:
    """Configuracion tipada del simulador de bateria.

    Attributes:
        host: IP del servidor destino (Raspberry Pi).
        puerto: Puerto TCP para conexion.
        intervalo_envio_ms: Intervalo de envio en milisegundos.
        voltaje_minimo: Voltaje minimo del slider (V).
        voltaje_maximo: Voltaje maximo del slider (V).
        voltaje_inicial: Voltaje inicial al iniciar (V).
    """

    host: str
    puerto: int
    intervalo_envio_ms: int
    voltaje_minimo: float
    voltaje_maximo: float
    voltaje_inicial: float

    @classmethod
    def desde_defaults(cls) -> "ConfigSimuladorBateria":
        """Crea configuracion con valores por defecto."""
        return cls(
            host=DEFAULT_IP,
            puerto=DEFAULT_PUERTO,
            intervalo_envio_ms=DEFAULT_INTERVALO_MS,
            voltaje_minimo=DEFAULT_VOLTAJE_MIN,
            voltaje_maximo=DEFAULT_VOLTAJE_MAX,
            voltaje_inicial=DEFAULT_VOLTAJE_INICIAL,
        )


class ConfigManager:
    """Singleton para gestionar la configuracion del simulador."""

    _instance: Optional["ConfigManager"] = None
    _config: Optional[ConfigSimuladorBateria] = None

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

    def cargar(self, ruta_config: Optional[Path] = None) -> ConfigSimuladorBateria:
        """Carga la configuracion desde config.json.

        Args:
            ruta_config: Ruta al archivo config.json. Si es None,
                        busca en el directorio raiz del proyecto.

        Returns:
            ConfigSimuladorBateria con los valores cargados.
        """
        if ruta_config is None:
            ruta_config = self._buscar_config_json()

        if ruta_config is not None and ruta_config.exists():
            self._config = self._cargar_desde_archivo(ruta_config)
        else:
            self._config = ConfigSimuladorBateria.desde_defaults()

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

    def _cargar_desde_archivo(self, ruta: Path) -> ConfigSimuladorBateria:
        """Carga y parsea el archivo config.json."""
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)

        raspberry = datos.get("raspberry_pi", {})
        puertos = datos.get("puertos", {})
        simulador = datos.get("simulador_bateria", {})

        return ConfigSimuladorBateria(
            host=raspberry.get("ip", DEFAULT_IP),
            puerto=puertos.get("bateria", DEFAULT_PUERTO),
            intervalo_envio_ms=simulador.get("intervalo_envio_ms", DEFAULT_INTERVALO_MS),
            voltaje_minimo=simulador.get("voltaje_minimo", DEFAULT_VOLTAJE_MIN),
            voltaje_maximo=simulador.get("voltaje_maximo", DEFAULT_VOLTAJE_MAX),
            voltaje_inicial=simulador.get("voltaje_inicial", DEFAULT_VOLTAJE_INICIAL),
        )

    @property
    def config(self) -> ConfigSimuladorBateria:
        """Obtiene la configuracion actual.

        Returns:
            ConfigSimuladorBateria cargada, o defaults si no se cargo.
        """
        if self._config is None:
            self._config = ConfigSimuladorBateria.desde_defaults()
        return self._config
