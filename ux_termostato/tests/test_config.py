"""
Tests del módulo de configuración ConfigUX.

Valida la creación, parsing desde dict, validaciones y valores por defecto
de la configuración de la aplicación UX Termostato.
"""

import pytest

from app.configuracion import ConfigUX


class TestCreacion:
    """Tests de creación de ConfigUX."""

    def test_creacion_con_valores_validos(self):
        """Debe crear config con todos los valores válidos."""
        config = ConfigUX(
            ip_raspberry="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
            intervalo_recepcion_ms=500,
            intervalo_actualizacion_ui_ms=100,
            temperatura_min_setpoint=15.0,
            temperatura_max_setpoint=30.0,
            temperatura_setpoint_inicial=22.0,
        )

        assert config.ip_raspberry == "192.168.1.50"
        assert config.puerto_recv == 14001
        assert config.puerto_send == 14000
        assert config.intervalo_recepcion_ms == 500
        assert config.intervalo_actualizacion_ui_ms == 100
        assert config.temperatura_min_setpoint == 15.0
        assert config.temperatura_max_setpoint == 30.0
        assert config.temperatura_setpoint_inicial == 22.0

    def test_creacion_con_defaults(self):
        """Debe crear config con valores por defecto."""
        config = ConfigUX.defaults()

        assert config.ip_raspberry == "127.0.0.1"
        assert config.puerto_recv == 14001
        assert config.puerto_send == 14000
        assert config.intervalo_recepcion_ms == 500
        assert config.temperatura_setpoint_inicial == 22.0


class TestFromDict:
    """Tests de parsing desde diccionario."""

    def test_from_dict_con_estructura_completa(self):
        """Debe parsear correctamente config.json completo."""
        data = {
            "raspberry_pi": {"ip": "192.168.1.100"},
            "puertos": {"visualizador_temperatura": 14001, "selector_temperatura": 14000},
            "ux_termostato": {
                "intervalo_recepcion_ms": 1000,
                "intervalo_actualizacion_ui_ms": 200,
                "temperatura_minima_setpoint": 10.0,
                "temperatura_maxima_setpoint": 35.0,
                "temperatura_setpoint_inicial": 25.0,
            },
        }

        config = ConfigUX.from_dict(data)

        assert config.ip_raspberry == "192.168.1.100"
        assert config.puerto_recv == 14001
        assert config.puerto_send == 14000
        assert config.intervalo_recepcion_ms == 1000
        assert config.temperatura_min_setpoint == 10.0
        assert config.temperatura_max_setpoint == 35.0
        assert config.temperatura_setpoint_inicial == 25.0

    def test_from_dict_con_estructura_real_config_json(self):
        """Debe parsear estructura real de config.json del proyecto."""
        data = {
            "raspberry_pi": {"ip": "127.0.0.1", "descripcion": "..."},
            "puertos": {
                "temperatura": 12000,
                "bateria": 11000,
                "seteo_temperatura": 13000,
                "selector_temperatura": 14000,
                "visualizador_temperatura": 14001,
                "visualizador_bateria": 14002,
            },
            "ux_termostato": {
                "intervalo_recepcion_ms": 500,
                "intervalo_actualizacion_ui_ms": 100,
                "temperatura_minima_setpoint": 15.0,
                "temperatura_maxima_setpoint": 30.0,
                "temperatura_setpoint_inicial": 22.0,
                "historial_max_puntos": 100,
            },
        }

        config = ConfigUX.from_dict(data)

        assert config.ip_raspberry == "127.0.0.1"
        assert config.puerto_recv == 14001
        assert config.puerto_send == 14000


class TestValidaciones:
    """Tests de validaciones de rangos y valores."""

    def test_puerto_recv_fuera_de_rango_bajo(self):
        """Debe lanzar ValueError si puerto_recv < 1."""
        with pytest.raises(ValueError, match="puerto_recv fuera de rango"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=0,
                puerto_send=14000,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=22.0,
            )

    def test_puerto_recv_fuera_de_rango_alto(self):
        """Debe lanzar ValueError si puerto_recv > 65535."""
        with pytest.raises(ValueError, match="puerto_recv fuera de rango"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=70000,
                puerto_send=14000,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=22.0,
            )

    def test_puerto_send_fuera_de_rango(self):
        """Debe lanzar ValueError si puerto_send está fuera de rango."""
        with pytest.raises(ValueError, match="puerto_send fuera de rango"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=14001,
                puerto_send=-1,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=22.0,
            )

    def test_intervalo_recepcion_ms_negativo(self):
        """Debe lanzar ValueError si intervalo_recepcion_ms <= 0."""
        with pytest.raises(ValueError, match="intervalo_recepcion_ms debe ser positivo"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=14001,
                puerto_send=14000,
                intervalo_recepcion_ms=-100,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=22.0,
            )

    def test_intervalo_actualizacion_ui_ms_cero(self):
        """Debe lanzar ValueError si intervalo_actualizacion_ui_ms <= 0."""
        with pytest.raises(ValueError, match="intervalo_actualizacion_ui_ms debe ser positivo"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=14001,
                puerto_send=14000,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=0,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=22.0,
            )

    def test_temperatura_min_mayor_que_max(self):
        """Debe lanzar ValueError si temp_min >= temp_max."""
        with pytest.raises(ValueError, match="temperatura_min_setpoint.*debe ser menor que"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=14001,
                puerto_send=14000,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=30.0,
                temperatura_max_setpoint=15.0,
                temperatura_setpoint_inicial=22.0,
            )

    def test_temperatura_inicial_fuera_de_rango_bajo(self):
        """Debe lanzar ValueError si temp_inicial < temp_min."""
        with pytest.raises(ValueError, match="temperatura_setpoint_inicial.*debe estar entre"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=14001,
                puerto_send=14000,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=10.0,
            )

    def test_temperatura_inicial_fuera_de_rango_alto(self):
        """Debe lanzar ValueError si temp_inicial > temp_max."""
        with pytest.raises(ValueError, match="temperatura_setpoint_inicial.*debe estar entre"):
            ConfigUX(
                ip_raspberry="127.0.0.1",
                puerto_recv=14001,
                puerto_send=14000,
                intervalo_recepcion_ms=500,
                intervalo_actualizacion_ui_ms=100,
                temperatura_min_setpoint=15.0,
                temperatura_max_setpoint=30.0,
                temperatura_setpoint_inicial=35.0,
            )


class TestDefaults:
    """Tests de valores por defecto."""

    def test_defaults_tiene_valores_esperados(self):
        """Debe tener valores por defecto razonables."""
        config = ConfigUX.defaults()

        assert isinstance(config.ip_raspberry, str)
        assert 1 <= config.puerto_recv <= 65535
        assert 1 <= config.puerto_send <= 65535
        assert config.intervalo_recepcion_ms > 0
        assert config.intervalo_actualizacion_ui_ms > 0
        assert config.temperatura_min_setpoint < config.temperatura_max_setpoint
        assert (
            config.temperatura_min_setpoint
            <= config.temperatura_setpoint_inicial
            <= config.temperatura_max_setpoint
        )

    def test_defaults_es_inmutable(self):
        """Debe ser inmutable (frozen dataclass)."""
        config = ConfigUX.defaults()

        with pytest.raises(AttributeError):
            config.ip_raspberry = "10.0.0.1"  # type: ignore
