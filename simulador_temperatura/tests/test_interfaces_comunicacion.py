"""Tests para las interfaces de comunicación del simulador de temperatura.

Demuestra uso de mocks tipados que satisfacen IClienteTemperatura sin
necesitar conexión TCP real ni instanciar ClienteTemperatura.
"""
import pytest

from app.comunicacion.interfaces import IClienteTemperatura
from app.dominio.estado_temperatura import EstadoTemperatura


class MockClienteTemperatura:
    """Mock tipado que satisface IClienteTemperatura (structural subtyping)."""

    def __init__(self) -> None:
        self.temperaturas_enviadas: list[float] = []

    def enviar_temperatura(self, temperatura: float) -> bool:
        self.temperaturas_enviadas.append(temperatura)
        return True

    def enviar_estado(self, estado: EstadoTemperatura) -> bool:
        return self.enviar_temperatura(estado.temperatura)


class TestIClienteTemperatura:
    """Tests que verifican la interfaz IClienteTemperatura con mocks tipados."""

    def test_mock_satisface_protocolo(self):
        """MockClienteTemperatura satisface IClienteTemperatura sin herencia explícita."""
        mock = MockClienteTemperatura()
        assert isinstance(mock, IClienteTemperatura)

    def test_mock_enviar_temperatura(self):
        """El mock registra las temperaturas enviadas."""
        mock = MockClienteTemperatura()
        assert mock.enviar_temperatura(23.5) is True
        assert mock.temperaturas_enviadas == [23.5]

    def test_mock_enviar_estado(self):
        """El mock delega enviar_estado a enviar_temperatura."""
        mock = MockClienteTemperatura()
        estado = EstadoTemperatura(temperatura=25.0)
        assert mock.enviar_estado(estado) is True
        assert mock.temperaturas_enviadas == [25.0]

    def test_cliente_temperatura_real_satisface_protocolo(self, qapp):
        """ClienteTemperatura concreto también satisface IClienteTemperatura."""
        from app.comunicacion.cliente_temperatura import ClienteTemperatura
        cliente = ClienteTemperatura(host="127.0.0.1", port=12000)
        assert isinstance(cliente, IClienteTemperatura)
        cliente.deleteLater()
