"""
Tests de integración del panel Estado Conexion.

Valida flujo completo modelo → vista → controlador.
"""

import pytest

from compartido.widgets.led_color_provider import LEDColor
from app.presentacion.paneles.estado_conexion import (
    EstadoConexionModelo,
    EstadoConexionVista,
    EstadoConexionControlador,
)


class TestIntegracionMVC:
    """Tests de integración MVC completa."""

    def test_creacion_componentes_mvc(self, qapp):
        """Debe crear componentes MVC correctamente."""
        modelo = EstadoConexionModelo(estado="desconectado")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        assert modelo is not None
        assert vista is not None
        assert controlador is not None

    def test_flujo_completo_conexion(self, qapp, qtbot):
        """Flujo completo de establecer conexión."""
        modelo = EstadoConexionModelo(estado="desconectado")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        # Estado inicial: desconectado
        assert vista._label_estado.text() == "Desconectado"
        assert vista._led.color == LEDColor.RED

        # Intentar conectar
        controlador.conectando()
        assert vista._label_estado.text() == "Conectando..."
        assert vista._led.color == LEDColor.YELLOW
        assert vista._pulso_activo is True

        # Conexión exitosa
        controlador.conexion_establecida("192.168.1.50:14001")
        assert vista._label_estado.text() == "Conectado"
        assert vista._led.color == LEDColor.GREEN
        assert vista._pulso_activo is False

        # Limpiar
        vista._detener_pulso()

    def test_flujo_falla_conexion(self, qapp, qtbot):
        """Flujo de falla en conexión."""
        modelo = EstadoConexionModelo(estado="desconectado")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        # Intentar conectar
        controlador.conectando()
        assert vista._pulso_activo is True

        # Falla conexión
        controlador.conexion_perdida()
        assert vista._label_estado.text() == "Desconectado"
        assert vista._led.color == LEDColor.RED
        assert vista._pulso_activo is False

    def test_flujo_perdida_conexion(self, qapp, qtbot):
        """Flujo de pérdida de conexión establecida."""
        modelo = EstadoConexionModelo(estado="conectado", direccion_ip="192.168.1.50")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        # Estado inicial: conectado
        assert vista._label_estado.text() == "Conectado"
        assert vista._led.color == LEDColor.GREEN

        # Perder conexión
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000):
            controlador.conexion_perdida("192.168.1.50")

        assert vista._label_estado.text() == "Desconectado"
        assert vista._led.color == LEDColor.RED
        assert controlador.modelo.direccion_ip == ""

    def test_signals_consistentes_con_vista(self, qapp, qtbot):
        """Señales emitidas deben ser consistentes con vista."""
        modelo = EstadoConexionModelo(estado="desconectado")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        # Cambio a conectando
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker1:
            controlador.conectando()

        assert blocker1.args == ["conectando"]
        assert vista._label_estado.text() == "Conectando..."

        # Cambio a conectado
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker2:
            controlador.conexion_establecida("192.168.1.50")

        assert blocker2.args == ["conectado"]
        assert vista._label_estado.text() == "Conectado"

        # Limpiar
        vista._detener_pulso()

    def test_animacion_se_detiene_correctamente(self, qapp, qtbot):
        """Animación de pulso debe detenerse al cambiar estado."""
        modelo = EstadoConexionModelo(estado="desconectado")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        # Iniciar pulso
        controlador.conectando()
        assert vista._pulso_activo is True
        assert vista._timer_pulso is not None

        # Cambiar a conectado (debe detener pulso)
        controlador.conexion_establecida("192.168.1.50")
        assert vista._pulso_activo is False
        assert vista._timer_pulso is None

    def test_multiples_reconexiones(self, qapp, qtbot):
        """Múltiples ciclos de conexión/desconexión."""
        modelo = EstadoConexionModelo(estado="desconectado")
        vista = EstadoConexionVista()
        controlador = EstadoConexionControlador(modelo, vista)

        # Ciclo 1
        controlador.conectando()
        controlador.conexion_establecida("192.168.1.50")
        assert vista._label_estado.text() == "Conectado"

        controlador.conexion_perdida()
        assert vista._label_estado.text() == "Desconectado"

        # Ciclo 2
        controlador.conectando()
        controlador.conexion_establecida("10.0.0.1")
        assert vista._label_estado.text() == "Conectado"
        assert controlador.modelo.direccion_ip == "10.0.0.1"

        controlador.conexion_perdida()
        assert vista._label_estado.text() == "Desconectado"
        assert controlador.modelo.direccion_ip == ""

        # Limpiar
        vista._detener_pulso()
