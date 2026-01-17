"""
Tests unitarios para IndicadoresModelo.

Este módulo contiene tests para el modelo MVC del panel de indicadores de alerta,
verificando la creación, inmutabilidad y métodos del modelo.
"""

import pytest
from dataclasses import FrozenInstanceError

from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo


class TestCreacion:
    """Tests de creación e inicialización del modelo."""

    def test_crear_con_valores_default(self):
        """Verifica que se pueda crear un modelo con valores por defecto."""
        modelo = IndicadoresModelo()

        assert modelo.falla_sensor is False
        assert modelo.bateria_baja is False

    def test_crear_con_falla_sensor(self):
        """Verifica que se pueda crear un modelo con falla del sensor."""
        modelo = IndicadoresModelo(falla_sensor=True)

        assert modelo.falla_sensor is True
        assert modelo.bateria_baja is False

    def test_crear_con_bateria_baja(self):
        """Verifica que se pueda crear un modelo con batería baja."""
        modelo = IndicadoresModelo(bateria_baja=True)

        assert modelo.falla_sensor is False
        assert modelo.bateria_baja is True

    def test_crear_con_ambas_alertas(self):
        """Verifica que se pueda crear un modelo con ambas alertas activas."""
        modelo = IndicadoresModelo(falla_sensor=True, bateria_baja=True)

        assert modelo.falla_sensor is True
        assert modelo.bateria_baja is True


class TestInmutabilidad:
    """Tests de inmutabilidad del modelo (frozen=True)."""

    def test_es_inmutable_falla_sensor(self):
        """Verifica que no se pueda modificar falla_sensor después de creado."""
        modelo = IndicadoresModelo()

        with pytest.raises(FrozenInstanceError):
            modelo.falla_sensor = True

    def test_es_inmutable_bateria_baja(self):
        """Verifica que no se pueda modificar bateria_baja después de creado."""
        modelo = IndicadoresModelo()

        with pytest.raises(FrozenInstanceError):
            modelo.bateria_baja = True


class TestMetodos:
    """Tests de métodos del modelo."""

    def test_to_dict_sin_alertas(self):
        """Verifica conversión a diccionario sin alertas."""
        modelo = IndicadoresModelo()
        resultado = modelo.to_dict()

        assert resultado == {
            "falla_sensor": False,
            "bateria_baja": False,
        }

    def test_to_dict_con_falla_sensor(self):
        """Verifica conversión a diccionario con falla del sensor."""
        modelo = IndicadoresModelo(falla_sensor=True)
        resultado = modelo.to_dict()

        assert resultado == {
            "falla_sensor": True,
            "bateria_baja": False,
        }

    def test_to_dict_con_bateria_baja(self):
        """Verifica conversión a diccionario con batería baja."""
        modelo = IndicadoresModelo(bateria_baja=True)
        resultado = modelo.to_dict()

        assert resultado == {
            "falla_sensor": False,
            "bateria_baja": True,
        }

    def test_to_dict_con_ambas_alertas(self):
        """Verifica conversión a diccionario con ambas alertas."""
        modelo = IndicadoresModelo(falla_sensor=True, bateria_baja=True)
        resultado = modelo.to_dict()

        assert resultado == {
            "falla_sensor": True,
            "bateria_baja": True,
        }

    def test_tiene_alertas_sin_alertas(self):
        """Verifica que tiene_alertas() retorna False sin alertas."""
        modelo = IndicadoresModelo()

        assert modelo.tiene_alertas() is False

    def test_tiene_alertas_con_falla_sensor(self):
        """Verifica que tiene_alertas() retorna True con falla sensor."""
        modelo = IndicadoresModelo(falla_sensor=True)

        assert modelo.tiene_alertas() is True

    def test_tiene_alertas_con_bateria_baja(self):
        """Verifica que tiene_alertas() retorna True con batería baja."""
        modelo = IndicadoresModelo(bateria_baja=True)

        assert modelo.tiene_alertas() is True

    def test_tiene_alertas_con_ambas(self):
        """Verifica que tiene_alertas() retorna True con ambas alertas."""
        modelo = IndicadoresModelo(falla_sensor=True, bateria_baja=True)

        assert modelo.tiene_alertas() is True
