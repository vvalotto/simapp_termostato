"""
Tests unitarios para ClienteComandos.

Verifica que el cliente adapta comandos al protocolo texto plano de ISSE_Termostato
y los envía al RPi usando EphemeralSocketClient.

Protocolo real:
  - ComandoAumentar    → "aumentar"  → puerto 13000
  - ComandoDisminuir   → "disminuir" → puerto 13000
  - ComandoSetModoDisplay(modo="ambiente") → "ambiente" → puerto 14000
  - ComandoSetModoDisplay(modo="deseada")  → "deseada"  → puerto 14000
  - ComandoPower / ComandoSetTemp: no soportados por ISSE_Termostato → retorna False
"""
from unittest.mock import Mock, patch

import pytest

from app.comunicacion import ClienteComandos
from app.dominio import ComandoPower, ComandoSetTemp, ComandoSetModoDisplay
from app.dominio.comandos import ComandoAumentar, ComandoDisminuir


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
        with pytest.raises(AttributeError):
            cliente.host = "otra_ip"

        with pytest.raises(AttributeError):
            cliente.port = 9999


# --- Tests de Envío de Comandos ---

class TestEnvioComandos:
    """Tests de envío de comandos soportados por el protocolo texto plano."""

    def test_enviar_comando_aumentar(self, cliente, mock_ephemeral_client):
        """Verifica que ComandoAumentar envía 'aumentar' correctamente."""
        exito = cliente.enviar_comando(ComandoAumentar())

        assert exito
        mock_ephemeral_client.send.assert_called_once_with("aumentar")

    def test_enviar_comando_disminuir(self, cliente, mock_ephemeral_client):
        """Verifica que ComandoDisminuir envía 'disminuir' correctamente."""
        exito = cliente.enviar_comando(ComandoDisminuir())

        assert exito
        mock_ephemeral_client.send.assert_called_once_with("disminuir")

    def test_enviar_comando_set_modo_display_ambiente(self, cliente, mock_ephemeral_client):
        """Verifica que ComandoSetModoDisplay(modo='ambiente') envía 'ambiente'."""
        exito = cliente.enviar_comando(ComandoSetModoDisplay(modo="ambiente"))

        assert exito
        mock_ephemeral_client.send.assert_called_once_with("ambiente")

    def test_enviar_comando_set_modo_display_deseada(self, cliente, mock_ephemeral_client):
        """Verifica que ComandoSetModoDisplay(modo='deseada') envía 'deseada'."""
        exito = cliente.enviar_comando(ComandoSetModoDisplay(modo="deseada"))

        assert exito
        mock_ephemeral_client.send.assert_called_once_with("deseada")

    def test_comando_power_no_soportado_retorna_false(self, cliente, mock_ephemeral_client):
        """ComandoPower no es soportado (ISSE_Termostato no tiene endpoint)."""
        exito = cliente.enviar_comando(ComandoPower(estado=True))

        assert not exito
        mock_ephemeral_client.send.assert_not_called()

    def test_comando_set_temp_no_soportado_retorna_false(self, cliente, mock_ephemeral_client):
        """ComandoSetTemp no tiene equivalente en el protocolo texto plano."""
        exito = cliente.enviar_comando(ComandoSetTemp(valor=24.5))

        assert not exito
        mock_ephemeral_client.send.assert_not_called()


# --- Tests de Protocolo Texto Plano ---

class TestProtocoloTexto:
    """Tests del formato texto plano enviado a ISSE_Termostato."""

    def test_aumentar_envia_texto_exacto(self, cliente, mock_ephemeral_client):
        """El mensaje enviado es exactamente 'aumentar' sin newline ni JSON."""
        cliente.enviar_comando(ComandoAumentar())

        mensaje = mock_ephemeral_client.send.call_args[0][0]
        assert mensaje == "aumentar"

    def test_disminuir_envia_texto_exacto(self, cliente, mock_ephemeral_client):
        """El mensaje enviado es exactamente 'disminuir'."""
        cliente.enviar_comando(ComandoDisminuir())

        mensaje = mock_ephemeral_client.send.call_args[0][0]
        assert mensaje == "disminuir"

    def test_modo_display_envia_texto_exacto(self, cliente, mock_ephemeral_client):
        """El mensaje enviado es exactamente el modo ('ambiente' o 'deseada')."""
        cliente.enviar_comando(ComandoSetModoDisplay(modo="deseada"))

        mensaje = mock_ephemeral_client.send.call_args[0][0]
        assert mensaje == "deseada"


# --- Tests de Manejo de Errores ---

class TestManejoErrores:
    """Tests de manejo de errores de conexión."""

    def test_error_envio_retorna_false(self, qapp, mock_ephemeral_client):
        """Verifica que retorna False si el envío falla."""
        mock_ephemeral_client.send.return_value = False
        cliente = ClienteComandos("192.168.1.50", 14000)

        exito = cliente.enviar_comando(ComandoAumentar())

        assert not exito

    def test_excepcion_en_send_retorna_false(self, qapp, mock_ephemeral_client):
        """Verifica que captura excepciones y retorna False."""
        mock_ephemeral_client.send.side_effect = Exception("Error de red")
        cliente = ClienteComandos("192.168.1.50", 14000)

        exito = cliente.enviar_comando(ComandoAumentar())

        assert not exito

    def test_no_lanza_excepciones_al_usuario(self, qapp, mock_ephemeral_client):
        """Verifica que nunca lanza excepciones al usuario."""
        excepciones = [
            ConnectionRefusedError("Conexión rechazada"),
            TimeoutError("Timeout"),
            OSError("Error de socket"),
            Exception("Error genérico")
        ]

        for exc in excepciones:
            mock_ephemeral_client.send.side_effect = exc
            cliente = ClienteComandos("192.168.1.50", 14000)
            exito = cliente.enviar_comando(ComandoAumentar())
            assert not exito


# --- Tests de Múltiples Envíos ---

class TestMultiplesEnvios:
    """Tests de envíos consecutivos."""

    def test_multiples_comandos_consecutivos(self, cliente, mock_ephemeral_client):
        """Verifica que puede enviar múltiples comandos consecutivamente."""
        comandos = [
            ComandoAumentar(),
            ComandoDisminuir(),
            ComandoSetModoDisplay(modo="ambiente"),
            ComandoSetModoDisplay(modo="deseada"),
            ComandoAumentar(),
        ]

        for cmd in comandos:
            exito = cliente.enviar_comando(cmd)
            assert exito

        assert mock_ephemeral_client.send.call_count == 5

    def test_comandos_diferentes_tipos_secuenciales(self, cliente, mock_ephemeral_client):
        """Verifica que puede alternar entre tipos de comandos."""
        cliente.enviar_comando(ComandoAumentar())
        cliente.enviar_comando(ComandoDisminuir())
        cliente.enviar_comando(ComandoSetModoDisplay(modo="ambiente"))
        cliente.enviar_comando(ComandoSetModoDisplay(modo="deseada"))

        assert mock_ephemeral_client.send.call_count == 4

        calls = mock_ephemeral_client.send.call_args_list
        mensajes = [call[0][0] for call in calls]
        assert mensajes == ["aumentar", "disminuir", "ambiente", "deseada"]
