"""
Tests unitarios para ClienteComandos.

Verifica que el cliente serializa comandos correctamente y los envía
al RPi usando EphemeralSocketClient.
"""
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest

from app.comunicacion import ClienteComandos
from app.dominio import ComandoPower, ComandoSetTemp, ComandoSetModoDisplay


# --- Fixtures ---

@pytest.fixture
def mock_ephemeral_client():
    """Mock de EphemeralSocketClient."""
    with patch('app.comunicacion.cliente_comandos.EphemeralSocketClient') as mock:
        instance = mock.return_value
        instance.send = Mock(return_value=True)
        yield instance


@pytest.fixture
def cliente(qapp, mock_ephemeral_client):
    """Crea una instancia de ClienteComandos con EphemeralSocketClient mockeado."""
    return ClienteComandos("192.168.1.50", 14000)


# --- Tests de Creación ---

class TestCreacion:
    """Tests de inicialización del cliente."""

    def test_creacion_con_parametros(self, qapp, mock_ephemeral_client):
        """Verifica que se puede crear cliente con parámetros."""
        cliente = ClienteComandos("10.0.0.1", 15000)

        assert cliente.host == "10.0.0.1"
        assert cliente.port == 15000

    def test_creacion_con_puerto_default(self, qapp, mock_ephemeral_client):
        """Verifica que usa puerto por defecto 14000."""
        cliente = ClienteComandos("192.168.1.50")

        assert cliente.host == "192.168.1.50"
        assert cliente.port == 14000

    def test_propiedades_son_readonly(self, cliente):
        """Verifica que host y port son propiedades de solo lectura."""
        # Intentar asignar debe fallar (no hay setter)
        with pytest.raises(AttributeError):
            cliente.host = "otra_ip"

        with pytest.raises(AttributeError):
            cliente.port = 9999


# --- Tests de Envío de Comandos ---

class TestEnvioComandos:
    """Tests de envío de diferentes tipos de comandos."""

    def test_enviar_comando_power_on(self, cliente, mock_ephemeral_client):
        """Verifica que envía ComandoPower(estado=True) correctamente."""
        cmd = ComandoPower(estado=True)

        exito = cliente.enviar_comando(cmd)

        assert exito
        mock_ephemeral_client.send.assert_called_once()

        # Verificar el mensaje enviado
        mensaje_enviado = mock_ephemeral_client.send.call_args[0][0]
        assert mensaje_enviado.endswith("\n")

        # Parsear JSON enviado
        json_enviado = json.loads(mensaje_enviado.strip())
        assert json_enviado["comando"] == "power"
        assert json_enviado["estado"] == "on"
        assert "timestamp" in json_enviado

    def test_enviar_comando_power_off(self, cliente, mock_ephemeral_client):
        """Verifica que envía ComandoPower(estado=False) correctamente."""
        cmd = ComandoPower(estado=False)

        exito = cliente.enviar_comando(cmd)

        assert exito

        mensaje_enviado = mock_ephemeral_client.send.call_args[0][0]
        json_enviado = json.loads(mensaje_enviado.strip())
        assert json_enviado["comando"] == "power"
        assert json_enviado["estado"] == "off"

    def test_enviar_comando_set_temp(self, cliente, mock_ephemeral_client):
        """Verifica que envía ComandoSetTemp correctamente."""
        cmd = ComandoSetTemp(valor=24.5)

        exito = cliente.enviar_comando(cmd)

        assert exito

        mensaje_enviado = mock_ephemeral_client.send.call_args[0][0]
        json_enviado = json.loads(mensaje_enviado.strip())
        assert json_enviado["comando"] == "set_temp_deseada"
        assert json_enviado["valor"] == 24.5
        assert "timestamp" in json_enviado

    def test_enviar_comando_set_modo_display_ambiente(self, cliente, mock_ephemeral_client):
        """Verifica que envía ComandoSetModoDisplay(modo='ambiente')."""
        cmd = ComandoSetModoDisplay(modo="ambiente")

        exito = cliente.enviar_comando(cmd)

        assert exito

        mensaje_enviado = mock_ephemeral_client.send.call_args[0][0]
        json_enviado = json.loads(mensaje_enviado.strip())
        assert json_enviado["comando"] == "set_modo_display"
        assert json_enviado["modo"] == "ambiente"

    def test_enviar_comando_set_modo_display_deseada(self, cliente, mock_ephemeral_client):
        """Verifica que envía ComandoSetModoDisplay(modo='deseada')."""
        cmd = ComandoSetModoDisplay(modo="deseada")

        exito = cliente.enviar_comando(cmd)

        assert exito

        mensaje_enviado = mock_ephemeral_client.send.call_args[0][0]
        json_enviado = json.loads(mensaje_enviado.strip())
        assert json_enviado["comando"] == "set_modo_display"
        assert json_enviado["modo"] == "deseada"


# --- Tests de Serialización JSON ---

class TestSerializacionJSON:
    """Tests de formato JSON generado."""

    def test_json_termina_con_newline(self, cliente, mock_ephemeral_client):
        """Verifica que el mensaje JSON termina con newline (protocolo)."""
        cmd = ComandoPower(estado=True)

        cliente.enviar_comando(cmd)

        mensaje = mock_ephemeral_client.send.call_args[0][0]
        assert mensaje.endswith("\n")

    def test_json_es_valido(self, cliente, mock_ephemeral_client):
        """Verifica que el JSON generado es válido."""
        cmd = ComandoSetTemp(valor=22.0)

        cliente.enviar_comando(cmd)

        mensaje = mock_ephemeral_client.send.call_args[0][0]
        # No debe lanzar excepción
        datos = json.loads(mensaje.strip())
        assert isinstance(datos, dict)

    def test_json_incluye_timestamp_iso(self, cliente, mock_ephemeral_client):
        """Verifica que el timestamp está en formato ISO."""
        cmd = ComandoPower(estado=True)

        cliente.enviar_comando(cmd)

        mensaje = mock_ephemeral_client.send.call_args[0][0]
        datos = json.loads(mensaje.strip())

        timestamp_str = datos["timestamp"]
        # Debe poder parsearse como ISO
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)


# --- Tests de Manejo de Errores ---

class TestManejoErrores:
    """Tests de manejo de errores de conexión."""

    def test_error_envio_retorna_false(self, qapp, mock_ephemeral_client):
        """Verifica que retorna False si el envío falla."""
        mock_ephemeral_client.send.return_value = False
        cliente = ClienteComandos("192.168.1.50", 14000)

        cmd = ComandoPower(estado=True)
        exito = cliente.enviar_comando(cmd)

        assert not exito

    def test_excepcion_en_send_retorna_false(self, qapp, mock_ephemeral_client):
        """Verifica que captura excepciones y retorna False."""
        mock_ephemeral_client.send.side_effect = Exception("Error de red")
        cliente = ClienteComandos("192.168.1.50", 14000)

        cmd = ComandoPower(estado=True)
        exito = cliente.enviar_comando(cmd)

        assert not exito

    def test_no_lanza_excepciones_al_usuario(self, qapp, mock_ephemeral_client):
        """Verifica que nunca lanza excepciones al usuario."""
        # Configurar para lanzar diferentes tipos de excepciones
        excepciones = [
            ConnectionRefusedError("Conexión rechazada"),
            TimeoutError("Timeout"),
            OSError("Error de socket"),
            Exception("Error genérico")
        ]

        for exc in excepciones:
            mock_ephemeral_client.send.side_effect = exc
            cliente = ClienteComandos("192.168.1.50", 14000)

            cmd = ComandoPower(estado=True)
            # No debe lanzar excepción, solo retornar False
            exito = cliente.enviar_comando(cmd)
            assert not exito


# --- Tests de Múltiples Envíos ---

class TestMultiplesEnvios:
    """Tests de envíos consecutivos."""

    def test_multiples_comandos_consecutivos(self, cliente, mock_ephemeral_client):
        """Verifica que puede enviar múltiples comandos consecutivamente."""
        comandos = [
            ComandoPower(estado=True),
            ComandoSetTemp(valor=22.0),
            ComandoSetTemp(valor=23.5),
            ComandoSetModoDisplay(modo="deseada"),
            ComandoPower(estado=False)
        ]

        for cmd in comandos:
            exito = cliente.enviar_comando(cmd)
            assert exito

        # Verificar que se llamó send() 5 veces
        assert mock_ephemeral_client.send.call_count == 5

    def test_comandos_diferentes_tipos_secuenciales(self, cliente, mock_ephemeral_client):
        """Verifica que puede alternar entre tipos de comandos."""
        # Alternar entre diferentes tipos
        cliente.enviar_comando(ComandoPower(estado=True))
        cliente.enviar_comando(ComandoSetTemp(valor=20.0))
        cliente.enviar_comando(ComandoSetModoDisplay(modo="ambiente"))
        cliente.enviar_comando(ComandoPower(estado=False))

        assert mock_ephemeral_client.send.call_count == 4

        # Verificar que los JSON son diferentes
        calls = mock_ephemeral_client.send.call_args_list
        json_enviados = [json.loads(call[0][0].strip()) for call in calls]

        assert json_enviados[0]["comando"] == "power"
        assert json_enviados[1]["comando"] == "set_temp_deseada"
        assert json_enviados[2]["comando"] == "set_modo_display"
        assert json_enviados[3]["comando"] == "power"
