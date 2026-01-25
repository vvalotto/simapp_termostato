"""
Tests del modelo del panel Estado Conexion.

Valida la creación, inmutabilidad y validación de estados.
"""

import pytest

from app.presentacion.paneles.estado_conexion import EstadoConexionModelo


class TestCreacion:
    """Tests de creación del modelo."""

    def test_creacion_con_estado_conectado(self):
        """Debe crear modelo con estado 'conectado'."""
        modelo = EstadoConexionModelo(
            estado="conectado",
            direccion_ip="192.168.1.50"
        )

        assert modelo.estado == "conectado"
        assert modelo.direccion_ip == "192.168.1.50"

    def test_creacion_con_estado_desconectado(self):
        """Debe crear modelo con estado 'desconectado'."""
        modelo = EstadoConexionModelo(
            estado="desconectado",
            direccion_ip=""
        )

        assert modelo.estado == "desconectado"
        assert modelo.direccion_ip == ""

    def test_creacion_con_estado_conectando(self):
        """Debe crear modelo con estado 'conectando'."""
        modelo = EstadoConexionModelo(
            estado="conectando"
        )

        assert modelo.estado == "conectando"
        assert modelo.direccion_ip == ""

    def test_creacion_sin_direccion_ip_usa_default(self):
        """Debe usar string vacío como default para direccion_ip."""
        modelo = EstadoConexionModelo(estado="desconectado")

        assert modelo.direccion_ip == ""


class TestInmutabilidad:
    """Tests de inmutabilidad del modelo."""

    def test_modelo_es_frozen(self):
        """Modelo debe ser inmutable (frozen=True)."""
        modelo = EstadoConexionModelo(estado="conectado", direccion_ip="192.168.1.50")

        with pytest.raises(AttributeError):
            modelo.estado = "desconectado"  # type: ignore


class TestValidacionEstado:
    """Tests de validación de estado."""

    def test_estado_conectado_es_valido(self):
        """Estado 'conectado' debe ser válido."""
        modelo = EstadoConexionModelo(estado="conectado")
        assert modelo.estado == "conectado"

    def test_estado_desconectado_es_valido(self):
        """Estado 'desconectado' debe ser válido."""
        modelo = EstadoConexionModelo(estado="desconectado")
        assert modelo.estado == "desconectado"

    def test_estado_conectando_es_valido(self):
        """Estado 'conectando' debe ser válido."""
        modelo = EstadoConexionModelo(estado="conectando")
        assert modelo.estado == "conectando"

    def test_estado_invalido_falla(self):
        """Estado inválido debe lanzar ValueError."""
        with pytest.raises(ValueError, match="Estado inválido"):
            EstadoConexionModelo(estado="invalid")

    def test_estado_vacio_falla(self):
        """Estado vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="Estado inválido"):
            EstadoConexionModelo(estado="")

    def test_estado_con_mayusculas_falla(self):
        """Estado con mayúsculas debe fallar (case-sensitive)."""
        with pytest.raises(ValueError, match="Estado inválido"):
            EstadoConexionModelo(estado="Conectado")
