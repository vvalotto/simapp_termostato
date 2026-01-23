"""
Tests unitarios para los comandos del termostato.

Verifica la creación, validación y serialización de todos los comandos.
"""

import pytest
from datetime import datetime
from app.dominio import (
    ComandoTermostato,
    ComandoPower,
    ComandoSetTemp,
    ComandoSetModoDisplay,
)


class TestComandoBase:
    """Tests de la clase base abstracta ComandoTermostato."""

    def test_comando_base_es_abstracta(self):
        """No debe poder instanciarse directamente."""
        with pytest.raises(TypeError):
            ComandoTermostato()  # pylint: disable=abstract-class-instantiated

    def test_comando_base_requiere_to_json(self):
        """Subclases deben implementar to_json."""

        class ComandoSinToJson(ComandoTermostato):
            """Comando sin implementar to_json."""

        with pytest.raises(TypeError):
            ComandoSinToJson()  # pylint: disable=abstract-class-instantiated


class TestComandoPower:
    """Tests del comando de encendido/apagado."""

    def test_crear_comando_encender(self):
        """Debe crear comando para encender."""
        cmd = ComandoPower(estado=True)
        assert cmd.estado is True
        assert isinstance(cmd.timestamp, datetime)

    def test_crear_comando_apagar(self):
        """Debe crear comando para apagar."""
        cmd = ComandoPower(estado=False)
        assert cmd.estado is False
        assert isinstance(cmd.timestamp, datetime)

    def test_to_json_encender(self):
        """Debe serializar comando de encendido correctamente."""
        cmd = ComandoPower(estado=True)
        result = cmd.to_json()

        assert result["comando"] == "power"
        assert result["estado"] == "on"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)

    def test_to_json_apagar(self):
        """Debe serializar comando de apagado correctamente."""
        cmd = ComandoPower(estado=False)
        result = cmd.to_json()

        assert result["comando"] == "power"
        assert result["estado"] == "off"
        assert "timestamp" in result

    def test_timestamp_automatico(self):
        """Debe generar timestamp automáticamente si no se provee."""
        before = datetime.now()
        cmd = ComandoPower(estado=True)
        after = datetime.now()

        assert before <= cmd.timestamp <= after

    def test_timestamp_personalizado(self):
        """Debe aceptar timestamp personalizado."""
        timestamp = datetime(2026, 1, 23, 10, 30, 0)
        cmd = ComandoPower(estado=True, timestamp=timestamp)
        assert cmd.timestamp == timestamp


class TestComandoSetTemp:
    """Tests del comando de ajuste de temperatura."""

    def test_crear_comando_temperatura_valida(self):
        """Debe crear comando con temperatura válida."""
        cmd = ComandoSetTemp(valor=22.5)
        assert cmd.valor == 22.5
        assert isinstance(cmd.timestamp, datetime)

    def test_temperatura_minima_valida(self):
        """Debe aceptar temperatura en límite inferior (15°C)."""
        cmd = ComandoSetTemp(valor=15.0)
        assert cmd.valor == 15.0

    def test_temperatura_maxima_valida(self):
        """Debe aceptar temperatura en límite superior (35°C)."""
        cmd = ComandoSetTemp(valor=35.0)
        assert cmd.valor == 35.0

    def test_temperatura_por_debajo_del_minimo(self):
        """Debe rechazar temperatura menor a 15°C."""
        with pytest.raises(ValueError, match="Temperatura fuera de rango"):
            ComandoSetTemp(valor=14.9)

    def test_temperatura_por_encima_del_maximo(self):
        """Debe rechazar temperatura mayor a 35°C."""
        with pytest.raises(ValueError, match="Temperatura fuera de rango"):
            ComandoSetTemp(valor=35.1)

    def test_to_json_estructura_correcta(self):
        """Debe serializar con estructura correcta."""
        cmd = ComandoSetTemp(valor=24.5)
        result = cmd.to_json()

        assert result["comando"] == "set_temp_deseada"
        assert result["valor"] == 24.5
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)

    def test_to_json_preserva_decimales(self):
        """Debe preservar decimales en serialización."""
        cmd = ComandoSetTemp(valor=22.7)
        result = cmd.to_json()
        assert result["valor"] == 22.7


class TestComandoSetModoDisplay:
    """Tests del comando de cambio de modo display."""

    def test_crear_comando_modo_ambiente(self):
        """Debe crear comando para modo ambiente."""
        cmd = ComandoSetModoDisplay(modo="ambiente")
        assert cmd.modo == "ambiente"
        assert isinstance(cmd.timestamp, datetime)

    def test_crear_comando_modo_deseada(self):
        """Debe crear comando para modo deseada."""
        cmd = ComandoSetModoDisplay(modo="deseada")
        assert cmd.modo == "deseada"
        assert isinstance(cmd.timestamp, datetime)

    def test_modo_invalido(self):
        """Debe rechazar modo no válido."""
        with pytest.raises(ValueError, match="Modo inválido"):
            ComandoSetModoDisplay(modo="modo_invalido")

    def test_to_json_modo_ambiente(self):
        """Debe serializar comando de modo ambiente."""
        cmd = ComandoSetModoDisplay(modo="ambiente")
        result = cmd.to_json()

        assert result["comando"] == "set_modo_display"
        assert result["modo"] == "ambiente"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)

    def test_to_json_modo_deseada(self):
        """Debe serializar comando de modo deseada."""
        cmd = ComandoSetModoDisplay(modo="deseada")
        result = cmd.to_json()

        assert result["comando"] == "set_modo_display"
        assert result["modo"] == "deseada"
        assert "timestamp" in result


class TestInmutabilidadComandos:
    """Tests de inmutabilidad de todos los comandos."""

    def test_comando_power_es_frozen(self):
        """ComandoPower debe ser inmutable."""
        cmd = ComandoPower(estado=True)
        with pytest.raises(AttributeError):
            cmd.estado = False

    def test_comando_set_temp_es_frozen(self):
        """ComandoSetTemp debe ser inmutable."""
        cmd = ComandoSetTemp(valor=22.0)
        with pytest.raises(AttributeError):
            cmd.valor = 25.0

    def test_comando_set_modo_display_es_frozen(self):
        """ComandoSetModoDisplay debe ser inmutable."""
        cmd = ComandoSetModoDisplay(modo="ambiente")
        with pytest.raises(AttributeError):
            cmd.modo = "deseada"

    def test_timestamp_es_frozen(self):
        """Timestamp debe ser inmutable en todos los comandos."""
        cmd = ComandoPower(estado=True)
        with pytest.raises(AttributeError):
            cmd.timestamp = datetime.now()

    def test_comandos_son_hashables(self):
        """Todos los comandos deben ser hasheables."""
        cmd1 = ComandoPower(estado=True)
        cmd2 = ComandoSetTemp(valor=22.0)
        cmd3 = ComandoSetModoDisplay(modo="ambiente")

        # Deben poder ser usados en sets
        comandos_set = {cmd1, cmd2, cmd3}
        assert len(comandos_set) == 3


class TestTimestampISO:
    """Tests de serialización de timestamp en formato ISO."""

    def test_timestamp_es_iso_format(self):
        """Timestamp debe serializarse en formato ISO."""
        cmd = ComandoPower(estado=True)
        result = cmd.to_json()

        # Debe poder parsearse de vuelta
        timestamp_str = result["timestamp"]
        datetime.fromisoformat(timestamp_str)

    def test_timestamp_iso_en_todos_los_comandos(self):
        """Todos los comandos deben usar formato ISO para timestamp."""
        comandos = [
            ComandoPower(estado=True),
            ComandoSetTemp(valor=22.0),
            ComandoSetModoDisplay(modo="ambiente"),
        ]

        for cmd in comandos:
            result = cmd.to_json()
            assert isinstance(result["timestamp"], str)
            # Verificar que es parseable
            datetime.fromisoformat(result["timestamp"])
