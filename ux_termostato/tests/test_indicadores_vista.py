"""
Tests unitarios para IndicadoresVista.

Este módulo contiene tests para la vista MVC del panel de indicadores,
verificando la creación de widgets, actualización visual y estilos.
"""

import pytest
from PyQt6.QtCore import QTimer

from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo
from app.presentacion.paneles.indicadores.vista import IndicadoresVista, AlertLED
from compartido.widgets.led_color_provider import LEDColor


class TestCreacion:
    """Tests de creación de la vista."""

    def test_crear_vista(self, qapp):
        """Verifica que se pueda crear la vista."""
        vista = IndicadoresVista()

        assert vista is not None
        assert vista.objectName() == "panelIndicadores"

    def test_alert_sensor_existe(self, qapp):
        """Verifica que el AlertLED del sensor existe."""
        vista = IndicadoresVista()

        assert vista.alert_sensor is not None
        assert isinstance(vista.alert_sensor, AlertLED)
        assert vista.alert_sensor.label.text() == "Sensor"

    def test_alert_bateria_existe(self, qapp):
        """Verifica que el AlertLED de batería existe."""
        vista = IndicadoresVista()

        assert vista.alert_bateria is not None
        assert isinstance(vista.alert_bateria, AlertLED)
        assert vista.alert_bateria.label.text() == "Batería"

    def test_labels_correctos(self, qapp):
        """Verifica que los labels sean correctos."""
        vista = IndicadoresVista()

        assert vista.alert_sensor.label.text() == "Sensor"
        assert vista.alert_bateria.label.text() == "Batería"


class TestAlertLED:
    """Tests del widget AlertLED."""

    def test_crear_alert_led(self, qapp):
        """Verifica que se pueda crear un AlertLED."""
        alert = AlertLED("Test", LEDColor.RED, size=24)

        assert alert is not None
        assert alert.label.text() == "Test"
        assert alert.led.color == LEDColor.RED

    def test_set_estado_inactivo(self, qapp):
        """Verifica que se pueda establecer estado inactivo."""
        alert = AlertLED("Test", LEDColor.RED)
        alert.set_estado(activo=False, pulsar=False)

        assert alert.led.state is False
        assert alert._animacion_activa is False

    def test_set_estado_activo_sin_pulsar(self, qapp):
        """Verifica que se pueda activar LED sin pulsar."""
        alert = AlertLED("Test", LEDColor.RED)
        alert.set_estado(activo=True, pulsar=False)

        assert alert.led.state is True
        assert alert._animacion_activa is False

    def test_set_estado_activo_con_pulsar(self, qapp):
        """Verifica que se pueda activar LED con pulsar."""
        alert = AlertLED("Test", LEDColor.RED)
        alert.set_estado(activo=True, pulsar=True)

        assert alert.led.state is True
        assert alert._animacion_activa is True
        assert alert._timer_pulso.isActive()

    def test_detener_pulso(self, qapp):
        """Verifica que se pueda detener la animación pulsante."""
        alert = AlertLED("Test", LEDColor.RED)

        # Iniciar pulso
        alert.set_estado(activo=True, pulsar=True)
        assert alert._animacion_activa is True

        # Detener pulso
        alert.set_estado(activo=False, pulsar=False)
        assert alert._animacion_activa is False
        assert not alert._timer_pulso.isActive()


class TestActualizacion:
    """Tests de actualización de la vista."""

    def test_actualizar_sin_alertas(self, qapp):
        """Verifica actualización sin alertas activas."""
        vista = IndicadoresVista()
        modelo = IndicadoresModelo()

        vista.actualizar(modelo)

        assert vista.alert_sensor.led.state is False
        assert vista.alert_bateria.led.state is False
        assert vista.alert_sensor._animacion_activa is False
        assert vista.alert_bateria._animacion_activa is False

    def test_actualizar_con_falla_sensor(self, qapp):
        """Verifica actualización con falla del sensor."""
        vista = IndicadoresVista()
        modelo = IndicadoresModelo(falla_sensor=True)

        vista.actualizar(modelo)

        assert vista.alert_sensor._animacion_activa is True
        assert vista.alert_bateria.led.state is False

    def test_actualizar_con_bateria_baja(self, qapp):
        """Verifica actualización con batería baja."""
        vista = IndicadoresVista()
        modelo = IndicadoresModelo(bateria_baja=True)

        vista.actualizar(modelo)

        assert vista.alert_sensor.led.state is False
        assert vista.alert_bateria._animacion_activa is True

    def test_actualizar_ambas_alertas(self, qapp):
        """Verifica actualización con ambas alertas activas."""
        vista = IndicadoresVista()
        modelo = IndicadoresModelo(falla_sensor=True, bateria_baja=True)

        vista.actualizar(modelo)

        assert vista.alert_sensor._animacion_activa is True
        assert vista.alert_bateria._animacion_activa is True

    def test_recuperacion_sensor(self, qapp):
        """Verifica que el LED sensor se apaga al recuperarse."""
        vista = IndicadoresVista()

        # Activar falla
        modelo_falla = IndicadoresModelo(falla_sensor=True)
        vista.actualizar(modelo_falla)
        assert vista.alert_sensor._animacion_activa is True

        # Recuperar
        modelo_ok = IndicadoresModelo(falla_sensor=False)
        vista.actualizar(modelo_ok)
        assert vista.alert_sensor._animacion_activa is False
        assert vista.alert_sensor.led.state is False

    def test_recuperacion_bateria(self, qapp):
        """Verifica que el LED batería se apaga al recuperarse."""
        vista = IndicadoresVista()

        # Activar batería baja
        modelo_baja = IndicadoresModelo(bateria_baja=True)
        vista.actualizar(modelo_baja)
        assert vista.alert_bateria._animacion_activa is True

        # Recuperar
        modelo_ok = IndicadoresModelo(bateria_baja=False)
        vista.actualizar(modelo_ok)
        assert vista.alert_bateria._animacion_activa is False
        assert vista.alert_bateria.led.state is False


class TestEstilos:
    """Tests de estilos y layout."""

    def test_layout_horizontal(self, qapp):
        """Verifica que el layout sea horizontal."""
        vista = IndicadoresVista()

        layout = vista.layout()
        assert layout is not None
        # El layout debe contener ambos AlertLEDs
        assert layout.count() >= 2

    def test_espaciado_apropiado(self, qapp):
        """Verifica que hay espaciado apropiado entre widgets."""
        vista = IndicadoresVista()

        layout = vista.layout()
        assert layout.spacing() == 30  # Según implementación

    def test_estilos_aplicados(self, qapp):
        """Verifica que los estilos CSS estén aplicados."""
        vista = IndicadoresVista()

        stylesheet = vista.styleSheet()
        assert "panelIndicadores" in stylesheet
        assert "background-color" in stylesheet
