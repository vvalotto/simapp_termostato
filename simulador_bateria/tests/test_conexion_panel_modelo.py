"""Tests para ConexionPanelModelo.

Cubre: set_ip (strip), set_puerto (validacion 1-65535), set_conectado.
"""

import pytest

from app.presentacion.paneles.conexion.modelo import ConexionPanelModelo


class TestConexionPanelModeloCreacion:
    """Tests de inicializacion del modelo."""

    def test_valores_por_defecto(self):
        """El modelo inicia con valores por defecto."""
        modelo = ConexionPanelModelo()

        assert modelo.ip == "localhost"
        assert modelo.puerto == 11000
        assert modelo.conectado is False

    def test_valores_personalizados(self):
        """El modelo acepta valores personalizados."""
        modelo = ConexionPanelModelo(
            ip="192.168.1.100",
            puerto=12000,
            conectado=True
        )

        assert modelo.ip == "192.168.1.100"
        assert modelo.puerto == 12000
        assert modelo.conectado is True


class TestConexionPanelModeloSetIp:
    """Tests de set_ip con strip."""

    def test_set_ip_simple(self):
        """set_ip establece IP correctamente."""
        modelo = ConexionPanelModelo()

        modelo.set_ip("192.168.1.1")

        assert modelo.ip == "192.168.1.1"

    def test_set_ip_con_espacios_inicio(self):
        """set_ip elimina espacios al inicio."""
        modelo = ConexionPanelModelo()

        modelo.set_ip("  192.168.1.1")

        assert modelo.ip == "192.168.1.1"

    def test_set_ip_con_espacios_fin(self):
        """set_ip elimina espacios al final."""
        modelo = ConexionPanelModelo()

        modelo.set_ip("192.168.1.1  ")

        assert modelo.ip == "192.168.1.1"

    def test_set_ip_con_espacios_ambos(self):
        """set_ip elimina espacios en ambos extremos."""
        modelo = ConexionPanelModelo()

        modelo.set_ip("  192.168.1.1  ")

        assert modelo.ip == "192.168.1.1"

    def test_set_ip_localhost(self):
        """set_ip acepta localhost."""
        modelo = ConexionPanelModelo()

        modelo.set_ip("localhost")

        assert modelo.ip == "localhost"

    def test_set_ip_vacio(self):
        """set_ip acepta string vacio (despues de strip)."""
        modelo = ConexionPanelModelo()

        modelo.set_ip("   ")

        assert modelo.ip == ""


class TestConexionPanelModeloSetPuerto:
    """Tests de set_puerto con validacion de rango."""

    def test_set_puerto_valido(self):
        """set_puerto acepta puerto valido."""
        modelo = ConexionPanelModelo()

        modelo.set_puerto(8080)

        assert modelo.puerto == 8080

    def test_set_puerto_minimo(self):
        """set_puerto acepta puerto 1."""
        modelo = ConexionPanelModelo()

        modelo.set_puerto(1)

        assert modelo.puerto == 1

    def test_set_puerto_maximo(self):
        """set_puerto acepta puerto 65535."""
        modelo = ConexionPanelModelo()

        modelo.set_puerto(65535)

        assert modelo.puerto == 65535

    def test_set_puerto_clamp_inferior(self):
        """set_puerto limita a 1 si es menor."""
        modelo = ConexionPanelModelo()

        modelo.set_puerto(0)

        assert modelo.puerto == 1

    def test_set_puerto_clamp_inferior_negativo(self):
        """set_puerto limita a 1 si es negativo."""
        modelo = ConexionPanelModelo()

        modelo.set_puerto(-100)

        assert modelo.puerto == 1

    def test_set_puerto_clamp_superior(self):
        """set_puerto limita a 65535 si es mayor."""
        modelo = ConexionPanelModelo()

        modelo.set_puerto(70000)

        assert modelo.puerto == 65535


class TestConexionPanelModeloSetConectado:
    """Tests de set_conectado."""

    def test_set_conectado_true(self):
        """set_conectado establece True."""
        modelo = ConexionPanelModelo(conectado=False)

        modelo.set_conectado(True)

        assert modelo.conectado is True

    def test_set_conectado_false(self):
        """set_conectado establece False."""
        modelo = ConexionPanelModelo(conectado=True)

        modelo.set_conectado(False)

        assert modelo.conectado is False

    def test_set_conectado_idempotente(self):
        """set_conectado es idempotente."""
        modelo = ConexionPanelModelo(conectado=True)

        modelo.set_conectado(True)
        modelo.set_conectado(True)

        assert modelo.conectado is True
