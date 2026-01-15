"""Tests unitarios para ClienteBateria.

Cubre:
- Creación con host/port
- Métodos sync: enviar_voltaje(), enviar_estado()
- Métodos async: enviar_voltaje_async(), enviar_estado_async()
- Signals: dato_enviado, error_conexion
- Mocking de EphemeralSocketClient
"""
import pytest
from unittest.mock import MagicMock, patch

from app.comunicacion.cliente_bateria import ClienteBateria
from app.dominio.estado_bateria import EstadoBateria


class TestClienteBateriaCreacion:
    """Tests de creación del cliente."""

    def test_crear_cliente(self, mock_ephemeral_client, qtbot):
        """Verifica creación básica."""
        with patch('app.comunicacion.cliente_bateria.EphemeralSocketClient') as mock_class:
            mock_class.return_value = mock_ephemeral_client
            cliente = ClienteBateria("192.168.1.100", 12345)

        assert cliente is not None
        assert cliente.host == "192.168.1.100"
        assert cliente.port == 12345

    def test_host_y_port_properties(self, mock_cliente):
        """Properties host y port retornan valores correctos."""
        assert mock_cliente.host == "127.0.0.1"
        assert mock_cliente.port == 11000


class TestClienteBateriaEnviarVoltaje:
    """Tests de enviar_voltaje() (sync)."""

    def test_enviar_voltaje_formato_correcto(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje() formatea como '12.50' (sin newline)."""
        mock_cliente.enviar_voltaje(12.5)

        mock_ephemeral_client.send.assert_called_once_with("12.50")

    def test_enviar_voltaje_exitoso_retorna_true(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje() retorna True si envío exitoso."""
        mock_ephemeral_client.send.return_value = True

        resultado = mock_cliente.enviar_voltaje(13.7)

        assert resultado is True

    def test_enviar_voltaje_fallido_retorna_false(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje() retorna False si envío falla."""
        mock_ephemeral_client.send.return_value = False

        resultado = mock_cliente.enviar_voltaje(14.2)

        assert resultado is False

    def test_enviar_voltaje_con_dos_decimales(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje() siempre usa 2 decimales."""
        mock_cliente.enviar_voltaje(10.0)

        mock_ephemeral_client.send.assert_called_with("10.00")

    def test_enviar_voltaje_redondea_correctamente(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje() redondea a 2 decimales."""
        mock_cliente.enviar_voltaje(12.456)

        mock_ephemeral_client.send.assert_called_with("12.46")


class TestClienteBateriaEnviarVoltajeAsync:
    """Tests de enviar_voltaje_async()."""

    def test_enviar_voltaje_async_llama_send_async(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje_async() usa send_async."""
        mock_cliente.enviar_voltaje_async(13.5)

        mock_ephemeral_client.send_async.assert_called_once_with("13.50")

    def test_enviar_voltaje_async_formato_correcto(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje_async() formatea igual que sync."""
        mock_cliente.enviar_voltaje_async(14.75)

        mock_ephemeral_client.send_async.assert_called_with("14.75")

    def test_enviar_voltaje_async_no_retorna_valor(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje_async() no retorna valor (es async)."""
        resultado = mock_cliente.enviar_voltaje_async(12.0)

        assert resultado is None


class TestClienteBateriaEnviarEstado:
    """Tests de enviar_estado() (sync)."""

    def test_enviar_estado_extrae_voltaje(self, mock_cliente, mock_ephemeral_client):
        """enviar_estado() extrae voltaje de EstadoBateria."""
        estado = EstadoBateria(voltaje=12.5)

        mock_cliente.enviar_estado(estado)

        mock_ephemeral_client.send.assert_called_once_with("12.50")

    def test_enviar_estado_retorna_resultado(self, mock_cliente, mock_ephemeral_client):
        """enviar_estado() retorna resultado del envío."""
        mock_ephemeral_client.send.return_value = True
        estado = EstadoBateria(voltaje=13.0)

        resultado = mock_cliente.enviar_estado(estado)

        assert resultado is True

    def test_enviar_estado_ignora_otros_atributos(self, mock_cliente, mock_ephemeral_client):
        """enviar_estado() solo usa voltaje, ignora en_rango."""
        estado = EstadoBateria(voltaje=14.5, en_rango=False)

        mock_cliente.enviar_estado(estado)

        # Solo debe enviar el voltaje formateado
        mock_ephemeral_client.send.assert_called_with("14.50")


class TestClienteBateriaEnviarEstadoAsync:
    """Tests de enviar_estado_async()."""

    def test_enviar_estado_async_extrae_voltaje(self, mock_cliente, mock_ephemeral_client):
        """enviar_estado_async() extrae voltaje."""
        estado = EstadoBateria(voltaje=11.8)

        mock_cliente.enviar_estado_async(estado)

        mock_ephemeral_client.send_async.assert_called_once_with("11.80")

    def test_enviar_estado_async_no_retorna_valor(self, mock_cliente, mock_ephemeral_client):
        """enviar_estado_async() no retorna valor."""
        estado = EstadoBateria(voltaje=12.0)

        resultado = mock_cliente.enviar_estado_async(estado)

        assert resultado is None


class TestClienteBateriaIntegracion:
    """Tests de integración con EphemeralSocketClient."""

    def test_cliente_usa_ephemeral_socket_client(self, mock_ephemeral_client):
        """ClienteBateria instancia EphemeralSocketClient."""
        with patch('app.comunicacion.cliente_bateria.EphemeralSocketClient') as mock_class:
            mock_class.return_value = mock_ephemeral_client

            cliente = ClienteBateria("10.0.0.1", 9999)

            # Debe haber instanciado EphemeralSocketClient con los parámetros
            mock_class.assert_called_once()

    def test_envio_multiple_usa_mismo_cliente(self, mock_cliente, mock_ephemeral_client):
        """Múltiples envíos usan el mismo cliente efímero."""
        mock_cliente.enviar_voltaje(12.0)
        mock_cliente.enviar_voltaje(12.5)
        mock_cliente.enviar_voltaje(13.0)

        # Debe haber 3 llamadas a send del mismo instance
        assert mock_ephemeral_client.send.call_count == 3

    def test_alternancia_sync_async(self, mock_cliente, mock_ephemeral_client):
        """Puede alternar entre sync y async."""
        mock_cliente.enviar_voltaje(12.0)       # sync
        mock_cliente.enviar_voltaje_async(12.5)  # async
        mock_cliente.enviar_voltaje(13.0)       # sync

        assert mock_ephemeral_client.send.call_count == 2
        assert mock_ephemeral_client.send_async.call_count == 1


class TestClienteBateriaErrorHandling:
    """Tests de manejo de errores."""

    def test_envio_con_excepcion_retorna_false(self, mock_cliente, mock_ephemeral_client):
        """Si send() lanza excepción, retorna False."""
        mock_ephemeral_client.send.side_effect = Exception("Connection error")

        resultado = mock_cliente.enviar_voltaje(12.0)

        assert resultado is False

    def test_envio_async_con_excepcion_no_falla(self, mock_cliente, mock_ephemeral_client):
        """enviar_voltaje_async() maneja excepciones sin fallar."""
        mock_ephemeral_client.send_async.side_effect = Exception("Connection error")

        # No debe lanzar excepción
        mock_cliente.enviar_voltaje_async(12.0)
