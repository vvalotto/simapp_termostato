"""
Tests unitarios para EstadoTermostato.

Verifica la creación, validación, serialización y deserialización del estado
del termostato.
"""

import pytest
from datetime import datetime
from app.dominio import EstadoTermostato


class TestCreacion:
    """Tests de creación e inicialización de EstadoTermostato."""

    def test_crear_estado_valido(self):
        """Debe crear un estado con todos los parámetros válidos."""
        estado = EstadoTermostato(
            temperatura_actual=22.5,
            temperatura_deseada=24.0,
            modo_climatizador="calentando",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        assert estado.temperatura_actual == 22.5
        assert estado.temperatura_deseada == 24.0
        assert estado.modo_climatizador == "calentando"
        assert estado.falla_sensor is False
        assert estado.bateria_baja is False
        assert estado.encendido is True
        assert estado.modo_display == "ambiente"
        assert isinstance(estado.timestamp, datetime)

    def test_crear_estado_con_todos_los_modos_climatizador(self):
        """Debe aceptar todos los modos válidos de climatizador."""
        timestamp = datetime.now()

        for modo in ["calentando", "enfriando", "reposo", "apagado"]:
            estado = EstadoTermostato(
                temperatura_actual=20.0,
                temperatura_deseada=22.0,
                modo_climatizador=modo,
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="ambiente",
                timestamp=timestamp,
            )
            assert estado.modo_climatizador == modo

    def test_crear_estado_con_todos_los_modos_display(self):
        """Debe aceptar todos los modos válidos de display."""
        timestamp = datetime.now()

        for modo in ["ambiente", "deseada"]:
            estado = EstadoTermostato(
                temperatura_actual=20.0,
                temperatura_deseada=22.0,
                modo_climatizador="reposo",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display=modo,
                timestamp=timestamp,
            )
            assert estado.modo_display == modo


class TestValidaciones:
    """Tests de validaciones de rangos y valores."""

    def test_temperatura_actual_minima_valida(self):
        """Debe aceptar temperatura actual en límite inferior (-40°C)."""
        estado = EstadoTermostato(
            temperatura_actual=-40.0,
            temperatura_deseada=20.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )
        assert estado.temperatura_actual == -40.0

    def test_temperatura_actual_maxima_valida(self):
        """Debe aceptar temperatura actual en límite superior (85°C)."""
        estado = EstadoTermostato(
            temperatura_actual=85.0,
            temperatura_deseada=20.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )
        assert estado.temperatura_actual == 85.0

    def test_temperatura_actual_por_debajo_del_minimo(self):
        """Debe rechazar temperatura actual menor a -40°C."""
        with pytest.raises(ValueError, match="temperatura_actual fuera de rango"):
            EstadoTermostato(
                temperatura_actual=-40.1,
                temperatura_deseada=20.0,
                modo_climatizador="reposo",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="ambiente",
                timestamp=datetime.now(),
            )

    def test_temperatura_actual_por_encima_del_maximo(self):
        """Debe rechazar temperatura actual mayor a 85°C."""
        with pytest.raises(ValueError, match="temperatura_actual fuera de rango"):
            EstadoTermostato(
                temperatura_actual=85.1,
                temperatura_deseada=20.0,
                modo_climatizador="reposo",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="ambiente",
                timestamp=datetime.now(),
            )

    def test_temperatura_deseada_minima_valida(self):
        """Debe aceptar temperatura deseada en límite inferior (15°C)."""
        estado = EstadoTermostato(
            temperatura_actual=20.0,
            temperatura_deseada=15.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )
        assert estado.temperatura_deseada == 15.0

    def test_temperatura_deseada_maxima_valida(self):
        """Debe aceptar temperatura deseada en límite superior (35°C)."""
        estado = EstadoTermostato(
            temperatura_actual=20.0,
            temperatura_deseada=35.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )
        assert estado.temperatura_deseada == 35.0

    def test_temperatura_deseada_por_debajo_del_minimo(self):
        """Debe rechazar temperatura deseada menor a 15°C."""
        with pytest.raises(ValueError, match="temperatura_deseada fuera de rango"):
            EstadoTermostato(
                temperatura_actual=20.0,
                temperatura_deseada=14.9,
                modo_climatizador="reposo",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="ambiente",
                timestamp=datetime.now(),
            )

    def test_temperatura_deseada_por_encima_del_maximo(self):
        """Debe rechazar temperatura deseada mayor a 35°C."""
        with pytest.raises(ValueError, match="temperatura_deseada fuera de rango"):
            EstadoTermostato(
                temperatura_actual=20.0,
                temperatura_deseada=35.1,
                modo_climatizador="reposo",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="ambiente",
                timestamp=datetime.now(),
            )

    def test_modo_climatizador_invalido(self):
        """Debe rechazar modo climatizador no válido."""
        with pytest.raises(ValueError, match="modo_climatizador inválido"):
            EstadoTermostato(
                temperatura_actual=20.0,
                temperatura_deseada=22.0,
                modo_climatizador="modo_invalido",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="ambiente",
                timestamp=datetime.now(),
            )

    def test_modo_display_invalido(self):
        """Debe rechazar modo display no válido."""
        with pytest.raises(ValueError, match="modo_display inválido"):
            EstadoTermostato(
                temperatura_actual=20.0,
                temperatura_deseada=22.0,
                modo_climatizador="reposo",
                falla_sensor=False,
                bateria_baja=False,
                encendido=True,
                modo_display="modo_invalido",
                timestamp=datetime.now(),
            )


class TestFromJson:
    """Tests de deserialización desde JSON."""

    def test_from_json_completo(self):
        """Debe crear estado desde JSON completo."""
        data = {
            "temperatura_actual": 22.5,
            "temperatura_deseada": 24.0,
            "modo_climatizador": "calentando",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": "2026-01-23T10:30:00Z",
        }

        estado = EstadoTermostato.from_json(data)

        assert estado.temperatura_actual == 22.5
        assert estado.temperatura_deseada == 24.0
        assert estado.modo_climatizador == "calentando"
        assert estado.falla_sensor is False
        assert estado.bateria_baja is False
        assert estado.encendido is True
        assert estado.modo_display == "ambiente"
        assert isinstance(estado.timestamp, datetime)

    def test_from_json_con_timestamp_datetime(self):
        """Debe aceptar timestamp como objeto datetime."""
        timestamp = datetime.now()
        data = {
            "temperatura_actual": 22.5,
            "temperatura_deseada": 24.0,
            "modo_climatizador": "reposo",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": timestamp,
        }

        estado = EstadoTermostato.from_json(data)
        assert estado.timestamp == timestamp

    def test_from_json_con_conversiones_de_tipo(self):
        """Debe convertir tipos apropiadamente."""
        data = {
            "temperatura_actual": "22.5",  # String → float
            "temperatura_deseada": "24",    # String → float
            "modo_climatizador": "reposo",
            "falla_sensor": 0,              # 0 → False
            "bateria_baja": 1,              # 1 → True
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": datetime.now(),
        }

        estado = EstadoTermostato.from_json(data)
        assert estado.temperatura_actual == 22.5
        assert estado.temperatura_deseada == 24.0
        assert estado.falla_sensor is False
        assert estado.bateria_baja is True

    def test_from_json_con_campo_faltante(self):
        """Debe lanzar KeyError si falta un campo requerido."""
        data = {
            "temperatura_actual": 22.5,
            # Falta temperatura_deseada
            "modo_climatizador": "reposo",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": datetime.now(),
        }

        with pytest.raises(KeyError):
            EstadoTermostato.from_json(data)

    def test_from_json_con_validacion_fallida(self):
        """Debe lanzar ValueError si los valores no pasan validación."""
        data = {
            "temperatura_actual": 100.0,  # Fuera de rango
            "temperatura_deseada": 24.0,
            "modo_climatizador": "reposo",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": datetime.now(),
        }

        with pytest.raises(ValueError, match="temperatura_actual fuera de rango"):
            EstadoTermostato.from_json(data)


class TestToDict:
    """Tests de serialización a diccionario."""

    def test_to_dict_estructura_completa(self):
        """Debe generar diccionario con todos los campos."""
        timestamp = datetime.now()
        estado = EstadoTermostato(
            temperatura_actual=22.5,
            temperatura_deseada=24.0,
            modo_climatizador="calentando",
            falla_sensor=False,
            bateria_baja=True,
            encendido=True,
            modo_display="ambiente",
            timestamp=timestamp,
        )

        result = estado.to_dict()

        assert result["temperatura_actual"] == 22.5
        assert result["temperatura_deseada"] == 24.0
        assert result["modo_climatizador"] == "calentando"
        assert result["falla_sensor"] is False
        assert result["bateria_baja"] is True
        assert result["encendido"] is True
        assert result["modo_display"] == "ambiente"
        assert result["timestamp"] == timestamp.isoformat()

    def test_to_dict_timestamp_es_string(self):
        """Debe serializar timestamp como string ISO."""
        estado = EstadoTermostato(
            temperatura_actual=20.0,
            temperatura_deseada=22.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        result = estado.to_dict()
        assert isinstance(result["timestamp"], str)
        # Debe poder parsearse de vuelta
        datetime.fromisoformat(result["timestamp"])


class TestInmutabilidad:
    """Tests de inmutabilidad del estado."""

    def test_estado_es_frozen(self):
        """Debe ser inmutable (frozen=True)."""
        estado = EstadoTermostato(
            temperatura_actual=20.0,
            temperatura_deseada=22.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        with pytest.raises(AttributeError):
            estado.temperatura_actual = 25.0

    def test_estado_es_hashable(self):
        """Debe ser hasheable para uso en sets/dicts."""
        estado = EstadoTermostato(
            temperatura_actual=20.0,
            temperatura_deseada=22.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        # Debe poder ser usado en un set
        estado_set = {estado}
        assert estado in estado_set
