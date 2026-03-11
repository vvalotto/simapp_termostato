"""Tests para las interfaces de comunicación de la UX del termostato.

Demuestra uso de mocks tipados que satisfacen IServidorEstado e IClienteComandos
sin necesitar TCP real ni instanciar las clases concretas.
"""
import pytest

from app.comunicacion.interfaces import IServidorEstado, IClienteComandos
from app.dominio import ComandoTermostato


class MockServidorEstado:
    """Mock tipado que satisface IServidorEstado (structural subtyping)."""

    def __init__(self) -> None:
        self._activo = False

    def iniciar(self) -> bool:
        self._activo = True
        return True

    def detener(self) -> None:
        self._activo = False

    def esta_activo(self) -> bool:
        return self._activo


class MockClienteComandos:
    """Mock tipado que satisface IClienteComandos (structural subtyping)."""

    def __init__(self) -> None:
        self.comandos_enviados: list[ComandoTermostato] = []

    def enviar_comando(self, cmd: ComandoTermostato) -> bool:
        self.comandos_enviados.append(cmd)
        return True


class TestIServidorEstado:
    """Tests que verifican la interfaz IServidorEstado con mocks tipados."""

    def test_mock_satisface_protocolo(self):
        """MockServidorEstado satisface IServidorEstado sin herencia explícita."""
        mock = MockServidorEstado()
        assert isinstance(mock, IServidorEstado)

    def test_mock_ciclo_vida(self):
        """El mock gestiona el estado activo/inactivo correctamente."""
        mock = MockServidorEstado()
        assert not mock.esta_activo()
        assert mock.iniciar() is True
        assert mock.esta_activo()
        mock.detener()
        assert not mock.esta_activo()

    def test_servidor_real_satisface_protocolo(self, qapp):
        """ServidorEstado concreto también satisface IServidorEstado."""
        from app.comunicacion.servidor_estado import ServidorEstado
        servidor = ServidorEstado(host="127.0.0.1", port=19999)
        assert isinstance(servidor, IServidorEstado)
        servidor.deleteLater()


class TestIClienteComandos:
    """Tests que verifican la interfaz IClienteComandos con mocks tipados."""

    def test_mock_satisface_protocolo(self):
        """MockClienteComandos satisface IClienteComandos sin herencia explícita."""
        mock = MockClienteComandos()
        assert isinstance(mock, IClienteComandos)

    def test_mock_registra_comandos(self):
        """El mock registra los comandos enviados."""
        from app.dominio.comandos import ComandoAumentar
        mock = MockClienteComandos()
        cmd = ComandoAumentar()
        assert mock.enviar_comando(cmd) is True
        assert len(mock.comandos_enviados) == 1

    def test_cliente_real_satisface_protocolo(self, qapp):
        """ClienteComandos concreto también satisface IClienteComandos."""
        from app.comunicacion.cliente_comandos import ClienteComandos
        cliente = ClienteComandos(host="127.0.0.1", port=14000)
        assert isinstance(cliente, IClienteComandos)
        cliente.deleteLater()
