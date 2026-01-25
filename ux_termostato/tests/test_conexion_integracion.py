"""
Tests de integración del panel Conexion.

Valida flujo completo modelo → vista → controlador.
"""

import pytest

from app.presentacion.paneles.conexion import (
    ConexionModelo,
    ConexionVista,
    ConexionControlador,
)


class TestIntegracionMVC:
    """Tests de integración MVC completa."""

    def test_creacion_componentes_mvc(self, qapp):
        """Debe crear componentes MVC correctamente."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        assert modelo is not None
        assert vista is not None
        assert controlador is not None

    def test_flujo_validacion_completo(self, qapp, qtbot):
        """Flujo completo de validación en tiempo real."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        # 1. IP inicial válida
        assert vista.input_ip.text() == "192.168.1.50"
        assert vista.boton_aplicar.isEnabled()

        # 2. Cambiar a IP inválida
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "999.999.999.999")

        assert not vista.boton_aplicar.isEnabled()
        assert "999" in vista._label_validacion.text()

        # 3. Corregir a IP válida
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "10.0.0.1")

        assert vista.boton_aplicar.isEnabled()
        assert vista._label_validacion.text() == ""

    def test_flujo_aplicar_configuracion(self, qapp, qtbot):
        """Flujo completo de aplicar configuración."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        # Cambiar IP
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "172.16.0.1")

        # Aplicar
        with qtbot.waitSignal(controlador.ip_cambiada, timeout=1000) as blocker:
            vista.boton_aplicar.click()

        # Verificar señal emitida
        assert blocker.args == ["172.16.0.1"]

    def test_validacion_visual_consistente_con_modelo(self, qapp, qtbot):
        """Estado visual debe ser consistente con modelo."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        # IP válida
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "192.168.1.100")

        assert controlador.modelo.ip_valida is True
        assert "#28a745" in vista.input_ip.styleSheet()  # Verde

        # IP inválida
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "256.1.1.1")

        assert controlador.modelo.ip_valida is False
        assert "#dc3545" in vista.input_ip.styleSheet()  # Rojo

    def test_puertos_no_modificables_desde_ui(self, qapp):
        """Puertos no deben ser modificables desde la UI."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        # Intentar modificar puertos (deben ser readonly)
        assert vista._input_puerto_recv.isReadOnly()
        assert vista._input_puerto_send.isReadOnly()

        # Los valores deben mantenerse
        assert vista._input_puerto_recv.text() == "14001"
        assert vista._input_puerto_send.text() == "14000"

    def test_validacion_incremental(self, qapp, qtbot):
        """Validación debe funcionar caracter por caracter."""
        modelo = ConexionModelo(
            ip="",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        vista.input_ip.clear()

        # Escribir IP completa caracter por caracter
        for char in "192.168.1.50":
            qtbot.keyClick(vista.input_ip, char)

        # Al final debe ser válida
        assert controlador.modelo.ip == "192.168.1.50"
        assert controlador.modelo.ip_valida is True

    def test_multiples_aplicaciones(self, qapp, qtbot):
        """Debe permitir aplicar múltiples veces."""
        modelo = ConexionModelo(
            ip="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
        )
        vista = ConexionVista()
        controlador = ConexionControlador(modelo, vista)

        # Aplicar 1
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "192.168.1.100")

        with qtbot.waitSignal(controlador.ip_cambiada, timeout=1000) as blocker1:
            vista.boton_aplicar.click()

        assert blocker1.args == ["192.168.1.100"]

        # Aplicar 2
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "10.0.0.1")

        with qtbot.waitSignal(controlador.ip_cambiada, timeout=1000) as blocker2:
            vista.boton_aplicar.click()

        assert blocker2.args == ["10.0.0.1"]
