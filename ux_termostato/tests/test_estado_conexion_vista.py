"""
Tests de la vista del panel Estado Conexion.

Valida creación de widgets, actualización desde modelo y animaciones.
"""

import pytest
from PyQt6.QtCore import QTimer

from compartido.widgets.led_indicator import LEDIndicator
from compartido.widgets.led_color_provider import LEDColor
from app.presentacion.paneles.estado_conexion import (
    EstadoConexionModelo,
    EstadoConexionVista,
)


class TestCreacion:
    """Tests de creación de la vista."""

    def test_creacion_exitosa(self, qapp):
        """Debe crear vista sin errores."""
        vista = EstadoConexionVista()
        assert vista is not None

    def test_tiene_led_indicator(self, qapp):
        """Debe tener LED indicator."""
        vista = EstadoConexionVista()
        assert hasattr(vista, "_led")
        assert isinstance(vista._led, LEDIndicator)

    def test_led_tiene_tamano_correcto(self, qapp):
        """LED debe tener tamaño 16x16."""
        vista = EstadoConexionVista()
        assert vista._led.width() == 16
        assert vista._led.height() == 16


class TestActualizacionConectado:
    """Tests de actualización con estado 'conectado'."""

    def test_actualizar_estado_conectado_led_verde(self, qapp):
        """Estado conectado debe mostrar LED verde."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectado", direccion_ip="192.168.1.50")

        vista.actualizar(modelo)

        assert vista._led.color == LEDColor.GREEN
        assert vista._led.state is True

    def test_actualizar_estado_conectado_texto(self, qapp):
        """Estado conectado debe mostrar texto 'Conectado'."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectado", direccion_ip="192.168.1.50")

        vista.actualizar(modelo)

        assert vista._label_estado.text() == "Conectado"

    def test_actualizar_estado_conectado_color_texto(self, qapp):
        """Estado conectado debe mostrar texto en verde."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectado", direccion_ip="192.168.1.50")

        vista.actualizar(modelo)

        # Verificar que el stylesheet contiene el color verde
        stylesheet = vista._label_estado.styleSheet()
        assert "#28a745" in stylesheet  # Verde


class TestActualizacionDesconectado:
    """Tests de actualización con estado 'desconectado'."""

    def test_actualizar_estado_desconectado_led_rojo(self, qapp):
        """Estado desconectado debe mostrar LED rojo apagado."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="desconectado")

        vista.actualizar(modelo)

        assert vista._led.color == LEDColor.RED
        assert vista._led.state is False

    def test_actualizar_estado_desconectado_texto(self, qapp):
        """Estado desconectado debe mostrar texto 'Desconectado'."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="desconectado")

        vista.actualizar(modelo)

        assert vista._label_estado.text() == "Desconectado"

    def test_actualizar_estado_desconectado_color_texto(self, qapp):
        """Estado desconectado debe mostrar texto en rojo."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="desconectado")

        vista.actualizar(modelo)

        # Verificar que el stylesheet contiene el color rojo
        stylesheet = vista._label_estado.styleSheet()
        assert "#dc3545" in stylesheet  # Rojo


class TestActualizacionConectando:
    """Tests de actualización con estado 'conectando'."""

    def test_actualizar_estado_conectando_led_amarillo(self, qapp):
        """Estado conectando debe mostrar LED amarillo."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectando")

        vista.actualizar(modelo)

        assert vista._led.color == LEDColor.YELLOW

    def test_actualizar_estado_conectando_texto(self, qapp):
        """Estado conectando debe mostrar texto 'Conectando...'."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectando")

        vista.actualizar(modelo)

        assert vista._label_estado.text() == "Conectando..."

    def test_actualizar_estado_conectando_color_texto(self, qapp):
        """Estado conectando debe mostrar texto en amarillo."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectando")

        vista.actualizar(modelo)

        # Verificar que el stylesheet contiene el color amarillo
        stylesheet = vista._label_estado.styleSheet()
        assert "#ffc107" in stylesheet  # Amarillo

    def test_actualizar_estado_conectando_inicia_pulso(self, qapp):
        """Estado conectando debe iniciar animación de pulso."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectando")

        vista.actualizar(modelo)

        assert vista._pulso_activo is True
        assert vista._timer_pulso is not None
        assert vista._timer_pulso.isActive()

        # Limpiar
        vista._detener_pulso()


class TestAnimacionPulso:
    """Tests de animación de pulso."""

    def test_iniciar_pulso_crea_timer(self, qapp):
        """Iniciar pulso debe crear timer."""
        vista = EstadoConexionVista()

        vista._iniciar_pulso()

        assert vista._timer_pulso is not None
        assert isinstance(vista._timer_pulso, QTimer)
        assert vista._timer_pulso.isActive()

        # Limpiar
        vista._detener_pulso()

    def test_detener_pulso_para_timer(self, qapp):
        """Detener pulso debe parar timer."""
        vista = EstadoConexionVista()

        vista._iniciar_pulso()
        vista._detener_pulso()

        assert vista._pulso_activo is False
        assert vista._timer_pulso is None

    def test_cambio_a_conectado_detiene_pulso(self, qapp):
        """Cambio de conectando a conectado debe detener pulso."""
        vista = EstadoConexionVista()

        # Iniciar con conectando (inicia pulso)
        modelo_conectando = EstadoConexionModelo(estado="conectando")
        vista.actualizar(modelo_conectando)
        assert vista._pulso_activo is True

        # Cambiar a conectado (debe detener pulso)
        modelo_conectado = EstadoConexionModelo(estado="conectado")
        vista.actualizar(modelo_conectado)
        assert vista._pulso_activo is False
        assert vista._timer_pulso is None

    def test_toggle_pulso_cambia_estado_led(self, qapp, qtbot):
        """Toggle pulso debe cambiar estado del LED."""
        vista = EstadoConexionVista()
        modelo = EstadoConexionModelo(estado="conectando")

        vista.actualizar(modelo)

        # Guardar estado inicial
        estado_inicial = vista._led.state

        # Esperar un toggle (500ms)
        qtbot.wait(600)

        # Estado debe haber cambiado
        assert vista._led.state != estado_inicial

        # Limpiar
        vista._detener_pulso()


class TestCambiosEstado:
    """Tests de cambios entre estados."""

    def test_cambio_desconectado_a_conectado(self, qapp):
        """Cambio de desconectado a conectado."""
        vista = EstadoConexionVista()

        # Desconectado
        modelo1 = EstadoConexionModelo(estado="desconectado")
        vista.actualizar(modelo1)
        assert vista._led.color == LEDColor.RED

        # Conectado
        modelo2 = EstadoConexionModelo(estado="conectado")
        vista.actualizar(modelo2)
        assert vista._led.color == LEDColor.GREEN
        assert vista._label_estado.text() == "Conectado"

    def test_cambio_conectando_a_desconectado(self, qapp):
        """Cambio de conectando a desconectado."""
        vista = EstadoConexionVista()

        # Conectando
        modelo1 = EstadoConexionModelo(estado="conectando")
        vista.actualizar(modelo1)
        assert vista._pulso_activo is True

        # Desconectado
        modelo2 = EstadoConexionModelo(estado="desconectado")
        vista.actualizar(modelo2)
        assert vista._pulso_activo is False
        assert vista._led.color == LEDColor.RED
