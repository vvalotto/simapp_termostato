"""Tests unitarios para configuración del simulador de batería.

Cubre:
- ConfigSimuladorBateria (dataclass inmutable)
- ConfigManager (singleton)
"""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.configuracion.config import ConfigSimuladorBateria, ConfigManager


class TestConfigSimuladorBateriaCreacion:
    """Tests de creación de ConfigSimuladorBateria."""

    def test_crear_con_valores(self):
        """Crear config con valores específicos."""
        config = ConfigSimuladorBateria(
            host="192.168.1.100",
            puerto=12345,
            intervalo_envio_ms=500,
            voltaje_minimo=10.0,
            voltaje_maximo=15.0,
            voltaje_inicial=12.5
        )

        assert config.host == "192.168.1.100"
        assert config.puerto == 12345
        assert config.intervalo_envio_ms == 500
        assert config.voltaje_minimo == 10.0
        assert config.voltaje_maximo == 15.0
        assert config.voltaje_inicial == 12.5

    def test_config_es_inmutable(self):
        """ConfigSimuladorBateria es frozen (inmutable)."""
        config = ConfigSimuladorBateria(
            host="127.0.0.1",
            puerto=11000,
            intervalo_envio_ms=100,
            voltaje_minimo=10.0,
            voltaje_maximo=15.0,
            voltaje_inicial=12.0
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            config.host = "10.0.0.1"

    def test_desde_defaults(self):
        """desde_defaults() crea config con valores por defecto."""
        config = ConfigSimuladorBateria.desde_defaults()

        assert config.host == "192.168.1.100"
        assert config.puerto == 11000
        assert config.intervalo_envio_ms == 1000
        assert config.voltaje_minimo == 0.0
        assert config.voltaje_maximo == 5.0
        assert config.voltaje_inicial == 2.5


class TestConfigManagerSingleton:
    """Tests del patrón singleton de ConfigManager."""

    def test_obtener_instancia_retorna_mismo_objeto(self):
        """obtener_instancia() retorna la misma instancia."""
        instancia1 = ConfigManager.obtener_instancia()
        instancia2 = ConfigManager.obtener_instancia()

        assert instancia1 is instancia2

    def test_reiniciar_permite_nueva_instancia(self):
        """reiniciar() permite crear nueva instancia."""
        instancia1 = ConfigManager.obtener_instancia()
        ConfigManager.reiniciar()
        instancia2 = ConfigManager.obtener_instancia()

        # Son objetos diferentes después de reiniciar
        assert instancia1 is not instancia2


class TestConfigManagerCargar:
    """Tests de carga de configuración."""

    def setup_method(self):
        """Reiniciar singleton antes de cada test."""
        ConfigManager.reiniciar()

    def test_cargar_usa_defaults_si_no_existe_archivo(self):
        """cargar() usa defaults si no encuentra config.json."""
        manager = ConfigManager.obtener_instancia()

        with patch.object(manager, '_buscar_config_json', return_value=None):
            config = manager.cargar()

        # Debe retornar config con defaults
        assert config.host == "192.168.1.100"
        assert config.puerto == 11000

    def test_cargar_lee_archivo_json(self):
        """cargar() lee y parsea config.json correctamente."""
        json_content = """
        {
            "raspberry_pi": {
                "ip": "10.0.0.5"
            },
            "puertos": {
                "bateria": 9999
            },
            "simulador_bateria": {
                "intervalo_envio_ms": 250,
                "voltaje_minimo": 11.0,
                "voltaje_maximo": 14.0,
                "voltaje_inicial": 12.5
            }
        }
        """

        manager = ConfigManager.obtener_instancia()
        fake_path = Path("/fake/config.json")

        with patch.object(manager, '_buscar_config_json', return_value=fake_path), \
             patch.object(Path, 'exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json_content)):
            config = manager.cargar()

        assert config.host == "10.0.0.5"
        assert config.puerto == 9999
        assert config.intervalo_envio_ms == 250
        assert config.voltaje_minimo == 11.0
        assert config.voltaje_maximo == 14.0
        assert config.voltaje_inicial == 12.5

    def test_cargar_property_cachea_resultado(self):
        """Property config cachea el resultado de cargar()."""
        manager = ConfigManager.obtener_instancia()

        with patch.object(Path, 'exists', return_value=False):
            config1 = manager.config
            config2 = manager.config

        # Debe retornar el mismo objeto
        assert config1 is config2
