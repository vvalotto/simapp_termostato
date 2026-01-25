"""
Tests del modelo del panel Conexion.

Valida la creación, inmutabilidad, validación de IP y puertos.
"""

import pytest

from app.presentacion.paneles.conexion import ConexionModelo


class TestCreacion:
    """Tests de creación del modelo."""

    def test_creacion_con_valores_validos(self):
        """Debe crear modelo con valores válidos."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )

        assert modelo.ip == "192.168.1.50"
        assert modelo.puerto_recv == 14001
        assert modelo.puerto_send == 14000
        assert modelo.ip_valida is True
        assert modelo.mensaje_error == ""

    def test_creacion_con_ip_valida_defaults(self):
        """Debe usar defaults correctos."""
        modelo = ConexionModelo(
            ip="127.0.0.1",
            puerto_recv=14001,
            puerto_send=14000,
        )

        assert modelo.ip_valida is True
        assert modelo.mensaje_error == ""


class TestInmutabilidad:
    """Tests de inmutabilidad del modelo."""

    def test_modelo_es_frozen(self):
        """Modelo debe ser inmutable (frozen=True)."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )

        with pytest.raises(AttributeError):
            modelo.ip = "10.0.0.1"  # type: ignore


class TestValidacionPuertos:
    """Tests de validación de puertos."""

    def test_puerto_recv_menor_a_1024_falla(self):
        """Puerto recv < 1024 debe fallar."""
        with pytest.raises(ValueError, match="Puerto recv inválido"):
            ConexionModelo(
                ip="192.168.1.50",
                puerto_recv=80,
                puerto_send=14000,
            )

    def test_puerto_recv_mayor_a_65535_falla(self):
        """Puerto recv > 65535 debe fallar."""
        with pytest.raises(ValueError, match="Puerto recv inválido"):
            ConexionModelo(
                ip="192.168.1.50",
                puerto_recv=70000,
                puerto_send=14000,
            )

    def test_puerto_send_menor_a_1024_falla(self):
        """Puerto send < 1024 debe fallar."""
        with pytest.raises(ValueError, match="Puerto send inválido"):
            ConexionModelo(
                ip="192.168.1.50",
                puerto_recv=14001,
                puerto_send=80,
            )

    def test_puerto_send_mayor_a_65535_falla(self):
        """Puerto send > 65535 debe fallar."""
        with pytest.raises(ValueError, match="Puerto send inválido"):
            ConexionModelo(
                ip="192.168.1.50",
                puerto_recv=14001,
                puerto_send=70000,
            )

    def test_puertos_en_limites_validos(self):
        """Puertos en límites 1024 y 65535 deben ser válidos."""
        # Límite inferior
        modelo1 = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=1024,
            puerto_send=1024,
        )
        assert modelo1.puerto_recv == 1024
        assert modelo1.puerto_send == 1024

        # Límite superior
        modelo2 = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=65535,
            puerto_send=65535,
        )
        assert modelo2.puerto_recv == 65535
        assert modelo2.puerto_send == 65535


class TestValidarIPMetodo:
    """Tests del método estático validar_ip()."""

    def test_ip_valida_retorna_true(self):
        """IP válida debe retornar (True, '')."""
        valida, mensaje = ConexionModelo.validar_ip("192.168.1.50")
        assert valida is True
        assert mensaje == ""

    def test_localhost_es_valida(self):
        """Localhost debe ser válida."""
        valida, mensaje = ConexionModelo.validar_ip("127.0.0.1")
        assert valida is True
        assert mensaje == ""

    def test_ip_privada_clase_a_es_valida(self):
        """IP privada clase A debe ser válida."""
        valida, mensaje = ConexionModelo.validar_ip("10.0.0.1")
        assert valida is True
        assert mensaje == ""

    def test_formato_invalido_sin_octetos_suficientes(self):
        """IP con menos de 4 octetos debe ser inválida."""
        valida, mensaje = ConexionModelo.validar_ip("192.168.1")
        assert valida is False
        assert "Formato inválido" in mensaje

    def test_formato_invalido_con_mas_octetos(self):
        """IP con más de 4 octetos debe ser inválida."""
        valida, mensaje = ConexionModelo.validar_ip("192.168.1.1.1")
        assert valida is False
        assert "Formato inválido" in mensaje

    def test_octeto_fuera_de_rango_mayor_255(self):
        """Octeto > 255 debe ser inválido."""
        valida, mensaje = ConexionModelo.validar_ip("192.168.1.256")
        assert valida is False
        assert "fuera de rango" in mensaje
        assert "256" in mensaje

    def test_octeto_fuera_de_rango_999(self):
        """Octeto 999 debe ser inválido."""
        valida, mensaje = ConexionModelo.validar_ip("999.999.999.999")
        assert valida is False
        assert "fuera de rango" in mensaje

    def test_octeto_negativo(self):
        """Octeto negativo debe ser inválido (no cumple regex)."""
        valida, mensaje = ConexionModelo.validar_ip("192.168.1.-1")
        assert valida is False
        assert "Formato inválido" in mensaje

    def test_ip_vacia_es_invalida(self):
        """IP vacía debe ser inválida."""
        valida, mensaje = ConexionModelo.validar_ip("")
        assert valida is False
        assert "Formato inválido" in mensaje

    def test_ip_con_letras_es_invalida(self):
        """IP con letras debe ser inválida."""
        valida, mensaje = ConexionModelo.validar_ip("192.168.a.1")
        assert valida is False
        assert "Formato inválido" in mensaje

    def test_ip_con_espacios_es_invalida(self):
        """IP con espacios debe ser inválida."""
        valida, mensaje = ConexionModelo.validar_ip("192.168. 1.1")
        assert valida is False
        assert "Formato inválido" in mensaje

    def test_ip_limite_inferior_valida(self):
        """0.0.0.0 debe ser válida."""
        valida, mensaje = ConexionModelo.validar_ip("0.0.0.0")
        assert valida is True
        assert mensaje == ""

    def test_ip_limite_superior_valida(self):
        """255.255.255.255 debe ser válida."""
        valida, mensaje = ConexionModelo.validar_ip("255.255.255.255")
        assert valida is True
        assert mensaje == ""
