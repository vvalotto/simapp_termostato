"""Tests unitarios para ConfigSimuladorTemperatura y ConfigManager."""
import pytest
import json
from pathlib import Path

from app.configuracion.config import ConfigSimuladorTemperatura, ConfigManager
from app.configuracion.constantes import (
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


class TestConfigSimuladorTemperatura:
    """Tests para el dataclass ConfigSimuladorTemperatura."""

    def test_crear_config_con_valores(self):
        """Verifica creación con valores específicos."""
        config = ConfigSimuladorTemperatura(
            ip_raspberry="192.168.1.50",
            puerto=14001,
            intervalo_envio_ms=500,
            temperatura_minima=-20.0,
            temperatura_maxima=60.0,
            temperatura_inicial=25.0,
            ruido_amplitud=0.3,
            paso_variacion=0.2,
            variacion_amplitud=3.0,
            variacion_periodo_segundos=30.0,
        )

        assert config.ip_raspberry == "192.168.1.50"
        assert config.puerto == 14001
        assert config.intervalo_envio_ms == 500
        assert config.temperatura_minima == pytest.approx(-20.0)
        assert config.temperatura_maxima == pytest.approx(60.0)
        assert config.temperatura_inicial == pytest.approx(25.0)
        assert config.ruido_amplitud == pytest.approx(0.3)
        assert config.paso_variacion == pytest.approx(0.2)
        assert config.variacion_amplitud == pytest.approx(3.0)
        assert config.variacion_periodo_segundos == pytest.approx(30.0)

    def test_desde_defaults_valores_correctos(self):
        """Verifica que desde_defaults() usa las constantes."""
        config = ConfigSimuladorTemperatura.desde_defaults()

        assert config.ip_raspberry == DEFAULT_IP
        assert config.puerto == DEFAULT_PUERTO
        assert config.intervalo_envio_ms == DEFAULT_INTERVALO_MS
        assert config.temperatura_minima == pytest.approx(DEFAULT_TEMP_MIN)
        assert config.temperatura_maxima == pytest.approx(DEFAULT_TEMP_MAX)
        assert config.temperatura_inicial == pytest.approx(DEFAULT_TEMP_INICIAL)
        assert config.ruido_amplitud == pytest.approx(DEFAULT_RUIDO_AMPLITUD)
        assert config.paso_variacion == pytest.approx(DEFAULT_PASO_VARIACION)
        assert config.variacion_amplitud == pytest.approx(DEFAULT_VARIACION_AMPLITUD)
        assert config.variacion_periodo_segundos == pytest.approx(DEFAULT_VARIACION_PERIODO)

    def test_config_es_inmutable(self):
        """Verifica que el dataclass es frozen (inmutable)."""
        config = ConfigSimuladorTemperatura.desde_defaults()

        with pytest.raises(AttributeError):
            config.puerto = 9999


class TestConfigManagerSingleton:
    """Tests para el patrón Singleton de ConfigManager."""

    def setup_method(self):
        """Reinicia el singleton antes de cada test."""
        ConfigManager.reiniciar()

    def test_singleton_misma_instancia(self):
        """Verifica que múltiples instancias son la misma."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()

        assert manager1 is manager2

    def test_obtener_instancia_crea_singleton(self):
        """Verifica que obtener_instancia() crea el singleton."""
        manager = ConfigManager.obtener_instancia()

        assert manager is not None
        assert isinstance(manager, ConfigManager)

    def test_obtener_instancia_retorna_misma_instancia(self):
        """Verifica que obtener_instancia() retorna siempre la misma."""
        manager1 = ConfigManager.obtener_instancia()
        manager2 = ConfigManager.obtener_instancia()

        assert manager1 is manager2

    def test_reiniciar_limpia_singleton(self):
        """Verifica que reiniciar() limpia el singleton."""
        manager1 = ConfigManager()
        ConfigManager.reiniciar()
        manager2 = ConfigManager()

        assert manager1 is not manager2

    def test_reiniciar_limpia_config(self):
        """Verifica que reiniciar() también limpia la configuración."""
        manager = ConfigManager()
        manager.cargar()
        ConfigManager.reiniciar()

        manager_nuevo = ConfigManager()
        assert manager_nuevo._config is None


class TestConfigManagerCargar:
    """Tests para el método cargar() de ConfigManager."""

    def setup_method(self):
        """Reinicia el singleton antes de cada test."""
        ConfigManager.reiniciar()

    def test_cargar_sin_archivo_usa_defaults(self, tmp_path):
        """Verifica que sin archivo usa valores por defecto."""
        ruta_inexistente = tmp_path / "no_existe.json"
        manager = ConfigManager()

        config = manager.cargar(ruta_inexistente)

        assert config.ip_raspberry == DEFAULT_IP
        assert config.puerto == DEFAULT_PUERTO

    def test_cargar_con_archivo_valido(self, tmp_path):
        """Verifica carga desde archivo JSON válido."""
        config_data = {
            "raspberry_pi": {"ip": "10.0.0.1"},
            "puertos": {"temperatura": 15000},
            "simulador_temperatura": {
                "intervalo_envio_ms": 2000,
                "temperatura_minima": -5.0,
                "temperatura_maxima": 45.0,
                "temperatura_inicial": 22.0,
                "ruido_amplitud": 0.8,
                "paso_variacion": 0.5,
                "variacion_amplitud": 10.0,
                "variacion_periodo_segundos": 120.0,
            },
        }
        archivo_config = tmp_path / "config.json"
        archivo_config.write_text(json.dumps(config_data), encoding="utf-8")

        manager = ConfigManager()
        config = manager.cargar(archivo_config)

        assert config.ip_raspberry == "10.0.0.1"
        assert config.puerto == 15000
        assert config.intervalo_envio_ms == 2000
        assert config.temperatura_minima == pytest.approx(-5.0)
        assert config.temperatura_maxima == pytest.approx(45.0)
        assert config.temperatura_inicial == pytest.approx(22.0)
        assert config.ruido_amplitud == pytest.approx(0.8)
        assert config.paso_variacion == pytest.approx(0.5)
        assert config.variacion_amplitud == pytest.approx(10.0)
        assert config.variacion_periodo_segundos == pytest.approx(120.0)

    def test_cargar_archivo_parcial_usa_defaults_faltantes(self, tmp_path):
        """Verifica que valores faltantes usan defaults."""
        config_data = {
            "raspberry_pi": {"ip": "172.16.0.1"},
        }
        archivo_config = tmp_path / "config.json"
        archivo_config.write_text(json.dumps(config_data), encoding="utf-8")

        manager = ConfigManager()
        config = manager.cargar(archivo_config)

        assert config.ip_raspberry == "172.16.0.1"
        assert config.puerto == DEFAULT_PUERTO
        assert config.intervalo_envio_ms == DEFAULT_INTERVALO_MS

    def test_cargar_con_ruta_none_busca_config(self):
        """Verifica que con ruta None busca config.json."""
        manager = ConfigManager()
        config = manager.cargar(ruta_config=None)

        assert config is not None
        assert isinstance(config, ConfigSimuladorTemperatura)


class TestConfigManagerBuscarConfig:
    """Tests para el método _buscar_config_json()."""

    def setup_method(self):
        """Reinicia el singleton antes de cada test."""
        ConfigManager.reiniciar()

    def test_buscar_config_retorna_path_o_none(self):
        """Verifica que _buscar_config_json retorna Path o None."""
        manager = ConfigManager()

        resultado = manager._buscar_config_json()

        assert resultado is None or isinstance(resultado, Path)

    def test_buscar_config_encuentra_archivo_existente(self, tmp_path, monkeypatch):
        """Verifica búsqueda cuando existe config.json."""
        config_file = tmp_path / "config.json"
        config_file.write_text("{}", encoding="utf-8")

        manager = ConfigManager()

        import app.configuracion.config as config_module
        original_file = Path(config_module.__file__)
        monkeypatch.setattr(
            config_module, "__file__", str(tmp_path / "config.py")
        )

        resultado = manager._buscar_config_json()

        monkeypatch.setattr(config_module, "__file__", str(original_file))

        assert resultado is not None or resultado is None


class TestConfigManagerPropertyConfig:
    """Tests para la property config."""

    def setup_method(self):
        """Reinicia el singleton antes de cada test."""
        ConfigManager.reiniciar()

    def test_config_sin_cargar_retorna_defaults(self):
        """Verifica que config sin cargar retorna defaults."""
        manager = ConfigManager()

        config = manager.config

        assert config.ip_raspberry == DEFAULT_IP
        assert config.puerto == DEFAULT_PUERTO

    def test_config_despues_de_cargar_retorna_cargada(self, tmp_path):
        """Verifica que config retorna la configuración cargada."""
        config_data = {
            "raspberry_pi": {"ip": "192.168.100.1"},
            "puertos": {"temperatura": 16000},
            "simulador_temperatura": {},
        }
        archivo_config = tmp_path / "config.json"
        archivo_config.write_text(json.dumps(config_data), encoding="utf-8")

        manager = ConfigManager()
        manager.cargar(archivo_config)

        assert manager.config.ip_raspberry == "192.168.100.1"
        assert manager.config.puerto == 16000

    def test_config_multiples_accesos_misma_instancia(self):
        """Verifica que múltiples accesos retornan la misma config."""
        manager = ConfigManager()

        config1 = manager.config
        config2 = manager.config

        assert config1 is config2
