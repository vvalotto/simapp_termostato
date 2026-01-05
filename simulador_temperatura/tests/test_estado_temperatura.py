"""Tests unitarios para EstadoTemperatura."""
import pytest
from datetime import datetime, timedelta

from app.dominio import EstadoTemperatura


class TestEstadoTemperaturaCreacion:
    """Tests de creación del dataclass."""

    def test_crear_estado_temperatura_basico(self):
        """Verifica creación con valores mínimos."""
        estado = EstadoTemperatura(temperatura=25.0)

        assert estado.temperatura == 25.0
        assert estado.en_rango is True
        assert isinstance(estado.timestamp, datetime)

    def test_crear_estado_temperatura_completo(self):
        """Verifica creación con todos los parámetros."""
        ts = datetime(2026, 1, 5, 12, 0, 0)
        estado = EstadoTemperatura(
            temperatura=30.5,
            timestamp=ts,
            en_rango=False
        )

        assert estado.temperatura == 30.5
        assert estado.timestamp == ts
        assert estado.en_rango is False

    def test_timestamp_automatico(self):
        """Verifica que timestamp se genera automáticamente cercano a ahora."""
        antes = datetime.now()
        estado = EstadoTemperatura(temperatura=20.0)
        despues = datetime.now()

        assert antes <= estado.timestamp <= despues


class TestEstadoTemperaturaToString:
    """Tests del método to_string()."""

    def test_to_string_formato_correcto(self):
        """Verifica formato '<float>\n'."""
        estado = EstadoTemperatura(temperatura=23.5)

        resultado = estado.to_string()

        assert resultado == "23.5\n"

    def test_to_string_precision_un_decimal(self):
        """Verifica precisión de 1 decimal."""
        estado = EstadoTemperatura(temperatura=23.456)

        resultado = estado.to_string()

        assert resultado == "23.5\n"

    def test_to_string_redondeo_hacia_arriba(self):
        """Verifica redondeo correcto hacia arriba."""
        estado = EstadoTemperatura(temperatura=23.96)

        resultado = estado.to_string()

        assert resultado == "24.0\n"

    def test_to_string_temperatura_negativa(self):
        """Verifica formato con temperaturas negativas."""
        estado = EstadoTemperatura(temperatura=-5.3)

        resultado = estado.to_string()

        assert resultado == "-5.3\n"

    def test_to_string_temperatura_cero(self):
        """Verifica formato con temperatura cero."""
        estado = EstadoTemperatura(temperatura=0.0)

        resultado = estado.to_string()

        assert resultado == "0.0\n"


class TestEstadoTemperaturaValidarRango:
    """Tests del método validar_rango()."""

    def test_validar_rango_dentro(self):
        """Temperatura dentro del rango retorna True."""
        estado = EstadoTemperatura(temperatura=25.0)

        resultado = estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert resultado is True
        assert estado.en_rango is True

    def test_validar_rango_fuera_minimo(self):
        """Temperatura por debajo del mínimo retorna False."""
        estado = EstadoTemperatura(temperatura=-15.0)

        resultado = estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert resultado is False
        assert estado.en_rango is False

    def test_validar_rango_fuera_maximo(self):
        """Temperatura por encima del máximo retorna False."""
        estado = EstadoTemperatura(temperatura=55.0)

        resultado = estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert resultado is False
        assert estado.en_rango is False

    def test_validar_rango_en_limite_minimo(self):
        """Temperatura exactamente en límite mínimo está en rango."""
        estado = EstadoTemperatura(temperatura=-10.0)

        resultado = estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert resultado is True
        assert estado.en_rango is True

    def test_validar_rango_en_limite_maximo(self):
        """Temperatura exactamente en límite máximo está en rango."""
        estado = EstadoTemperatura(temperatura=50.0)

        resultado = estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert resultado is True
        assert estado.en_rango is True

    def test_validar_rango_actualiza_estado(self):
        """Verifica que validar_rango actualiza el atributo en_rango."""
        estado = EstadoTemperatura(temperatura=25.0, en_rango=False)

        estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert estado.en_rango is True

        estado.temperatura = 100.0
        estado.validar_rango(temp_min=-10.0, temp_max=50.0)

        assert estado.en_rango is False
