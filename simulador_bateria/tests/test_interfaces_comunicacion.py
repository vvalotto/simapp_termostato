"""Tests para las interfaces de comunicación del simulador de batería.

Demuestra uso de mocks tipados que satisfacen IClienteBateria sin
necesitar conexión TCP real ni instanciar ClienteBateria.
"""
from unittest.mock import MagicMock

import pytest

from app.comunicacion.interfaces import IClienteBateria
from app.dominio.estado_bateria import EstadoBateria


class MockClienteBateria:
    """Mock tipado que satisface IClienteBateria (structural subtyping)."""

    def __init__(self) -> None:
        self.voltajes_enviados: list[float] = []

    def enviar_voltaje(self, voltaje: float) -> bool:
        self.voltajes_enviados.append(voltaje)
        return True

    def enviar_estado(self, estado: EstadoBateria) -> bool:
        return self.enviar_voltaje(estado.voltaje)


class TestIClienteBateria:
    """Tests que verifican la interfaz IClienteBateria con mocks tipados."""

    def test_mock_satisface_protocolo(self):
        """MockClienteBateria satisface IClienteBateria sin herencia explícita."""
        mock = MockClienteBateria()
        assert isinstance(mock, IClienteBateria)

    def test_mock_enviar_voltaje(self):
        """El mock registra los voltajes enviados."""
        mock = MockClienteBateria()
        assert mock.enviar_voltaje(3.7) is True
        assert mock.voltajes_enviados == [3.7]

    def test_mock_enviar_estado(self):
        """El mock delega enviar_estado a enviar_voltaje."""
        mock = MockClienteBateria()
        estado = EstadoBateria(voltaje=4.2)
        assert mock.enviar_estado(estado) is True
        assert mock.voltajes_enviados == [4.2]

    def test_cliente_bateria_real_satisface_protocolo(self, qapp):
        """ClienteBateria concreto también satisface IClienteBateria."""
        from app.comunicacion.cliente_bateria import ClienteBateria
        cliente = ClienteBateria(host="127.0.0.1", port=11000)
        assert isinstance(cliente, IClienteBateria)
        cliente.deleteLater()
