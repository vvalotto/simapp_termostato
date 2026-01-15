"""Tests para ControlPanelVista.

Tests de UI usando qtbot para widgets Qt reales.
"""

import pytest

from app.presentacion.paneles.control.vista import ControlPanelVista, ConfigControlPanelVista
from app.presentacion.paneles.control.modelo import ControlPanelModelo


@pytest.fixture
def vista(qtbot):
    """Vista real para tests."""
    v = ControlPanelVista()
    qtbot.addWidget(v)
    return v


@pytest.fixture
def modelo():
    """Modelo para tests."""
    return ControlPanelModelo(
        voltaje=2.5,
        voltaje_minimo=0.0,
        voltaje_maximo=5.0,
        precision=0.1
    )


class TestControlPanelVistaCreacion:
    """Tests de inicializacion de la vista."""

    def test_creacion_sin_config(self, qtbot):
        """Vista se crea con config por defecto."""
        vista = ControlPanelVista()
        qtbot.addWidget(vista)

        assert vista._config is not None
        assert vista._config.titulo == "Control de Voltaje"

    def test_creacion_con_config(self, qtbot):
        """Vista acepta config personalizada."""
        config = ConfigControlPanelVista(titulo="Test Control")
        vista = ControlPanelVista(config=config)
        qtbot.addWidget(vista)

        assert vista._config.titulo == "Test Control"

    def test_tiene_slider(self, vista):
        """Vista tiene slider."""
        assert vista._slider is not None

    def test_tiene_labels(self, vista):
        """Vista tiene labels de valor y limites."""
        assert vista._label_valor is not None
        assert vista._label_min is not None
        assert vista._label_max is not None

    def test_slider_rango_inicial(self, vista):
        """Slider tiene rango correcto inicial."""
        assert vista._slider.minimum() == 0
        assert vista._slider.maximum() == 50


class TestControlPanelVistaSlider:
    """Tests del slider y signal."""

    def test_slider_cambiado_emite_signal(self, vista, qtbot):
        """Mover slider emite slider_cambiado."""
        with qtbot.waitSignal(vista.slider_cambiado, timeout=1000) as blocker:
            vista._slider.setValue(30)

        assert blocker.args[0] == 30

    def test_get_slider_value(self, vista):
        """get_slider_value retorna valor actual."""
        vista._slider.setValue(25)

        assert vista.get_slider_value() == 25


class TestControlPanelVistaActualizar:
    """Tests de actualizar con modelo."""

    def test_actualizar_slider_valor(self, vista, modelo):
        """actualizar posiciona slider correctamente."""
        modelo.voltaje = 3.0  # paso 30

        vista.actualizar(modelo)

        assert vista._slider.value() == 30

    def test_actualizar_no_emite_signal(self, vista, modelo, qtbot):
        """actualizar no emite slider_cambiado (blockSignals)."""
        signal_spy = []
        vista.slider_cambiado.connect(lambda v: signal_spy.append(v))

        modelo.voltaje = 4.0
        vista.actualizar(modelo)

        assert len(signal_spy) == 0

    def test_actualizar_label_valor(self, vista, modelo):
        """actualizar muestra voltaje en label."""
        modelo.voltaje = 3.5

        vista.actualizar(modelo)

        assert "3.5" in vista._label_valor.text()

    def test_actualizar_labels_limites(self, vista, modelo):
        """actualizar muestra limites en labels."""
        modelo.voltaje_minimo = 1.0
        modelo.voltaje_maximo = 4.0

        vista.actualizar(modelo)

        assert "1.0" in vista._label_min.text()
        assert "4.0" in vista._label_max.text()

    def test_actualizar_ignora_modelo_invalido(self, vista):
        """actualizar ignora modelo de tipo incorrecto."""
        valor_original = vista._slider.value()

        vista.actualizar("no es un modelo")

        assert vista._slider.value() == valor_original
