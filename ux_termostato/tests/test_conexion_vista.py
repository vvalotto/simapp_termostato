"""
Tests de la vista del panel Conexion.

Valida creación de widgets, actualización desde modelo y feedback visual.
"""

import pytest
from PyQt6.QtWidgets import QLineEdit, QPushButton

from app.presentacion.paneles.conexion import ConexionModelo, ConexionVista


class TestCreacion:
    """Tests de creación de la vista."""

    def test_creacion_exitosa(self, qapp):
        """Debe crear vista sin errores."""
        vista = ConexionVista()
        assert vista is not None

    def test_tiene_input_ip(self, qapp):
        """Debe tener input de IP."""
        vista = ConexionVista()
        assert hasattr(vista, "input_ip")
        assert isinstance(vista.input_ip, QLineEdit)

    def test_tiene_boton_aplicar(self, qapp):
        """Debe tener botón aplicar."""
        vista = ConexionVista()
        assert hasattr(vista, "boton_aplicar")
        assert isinstance(vista.boton_aplicar, QPushButton)


class TestActualizacion:
    """Tests de actualización desde modelo."""

    def test_actualizar_muestra_ip(self, qapp):
        """Debe mostrar IP del modelo."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )

        vista.actualizar(modelo)

        assert vista.input_ip.text() == "192.168.1.50"

    def test_actualizar_muestra_puertos(self, qapp):
        """Debe mostrar puertos del modelo."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )

        vista.actualizar(modelo)

        # Acceder a los QLineEdit privados directamente
        assert vista._input_puerto_recv.text() == "14001"
        assert vista._input_puerto_send.text() == "14000"

    def test_actualizar_con_ip_valida_habilita_boton(self, qapp):
        """IP válida debe habilitar botón aplicar."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=True,
            mensaje_error="",
        )

        vista.actualizar(modelo)

        assert vista.boton_aplicar.isEnabled()

    def test_actualizar_con_ip_invalida_deshabilita_boton(self, qapp):
        """IP inválida debe deshabilitar botón aplicar."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="999.999.999.999",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=False,
            mensaje_error="Octeto fuera de rango: 999",
        )

        vista.actualizar(modelo)

        assert not vista.boton_aplicar.isEnabled()

    def test_actualizar_con_ip_invalida_muestra_mensaje_error(self, qapp):
        """IP inválida debe mostrar mensaje de error."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="999.999.999.999",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=False,
            mensaje_error="Octeto fuera de rango: 999",
        )

        vista.actualizar(modelo)

        # Verificar que el label de validación contiene el mensaje
        assert "999" in vista._label_validacion.text()
        assert "❌" in vista._label_validacion.text()

    def test_actualizar_con_ip_valida_limpia_mensaje_error(self, qapp):
        """IP válida debe limpiar mensaje de error."""
        vista = ConexionVista()

        # Primero mostrar error
        modelo_invalido = ConexionModelo(
            ip="999.999.999.999",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=False,
            mensaje_error="Octeto fuera de rango: 999",
        )
        vista.actualizar(modelo_invalido)

        # Luego mostrar IP válida
        modelo_valido = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=True,
            mensaje_error="",
        )
        vista.actualizar(modelo_valido)

        assert vista._label_validacion.text() == ""


class TestEstilos:
    """Tests de aplicación de estilos."""

    def test_ip_valida_aplica_borde_verde(self, qapp):
        """IP válida debe aplicar borde verde."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=True,
            mensaje_error="",
        )

        vista.actualizar(modelo)

        # Verificar que el stylesheet contiene el color verde
        stylesheet = vista.input_ip.styleSheet()
        assert "#28a745" in stylesheet  # Verde

    def test_ip_invalida_aplica_borde_rojo(self, qapp):
        """IP inválida debe aplicar borde rojo."""
        vista = ConexionVista()
        modelo = ConexionModelo(
            ip="999.999.999.999",
            puerto_recv=14001,
            puerto_send=14000,
            ip_valida=False,
            mensaje_error="Octeto fuera de rango: 999",
        )

        vista.actualizar(modelo)

        # Verificar que el stylesheet contiene el color rojo
        stylesheet = vista.input_ip.styleSheet()
        assert "#dc3545" in stylesheet  # Rojo


class TestConfiguracion:
    """Tests de configuración inicial."""

    def test_input_ip_tiene_placeholder(self, qapp):
        """Input IP debe tener placeholder."""
        vista = ConexionVista()
        assert vista.input_ip.placeholderText() == "192.168.1.50"

    def test_input_ip_tiene_max_length(self, qapp):
        """Input IP debe tener max length de 15 caracteres."""
        vista = ConexionVista()
        assert vista.input_ip.maxLength() == 15

    def test_puertos_son_readonly(self, qapp):
        """Campos de puerto deben ser readonly."""
        vista = ConexionVista()
        assert vista._input_puerto_recv.isReadOnly()
        assert vista._input_puerto_send.isReadOnly()
