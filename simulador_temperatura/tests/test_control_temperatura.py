"""Tests unitarios para los widgets de control de temperatura."""
import pytest

from app.presentacion import (
    ControlTemperatura,
    SliderConValor,
    PanelParametrosSenoidal,
    PanelTemperaturaManual,
    ParametrosSenoidal,
    RangosControl,
)


class TestParametrosSenoidal:
    """Tests para el dataclass ParametrosSenoidal."""

    def test_crear_parametros(self):
        """Verifica creación de parámetros."""
        params = ParametrosSenoidal(
            temperatura_base=20.0,
            amplitud=5.0,
            periodo=60.0,
        )
        assert params.temperatura_base == 20.0
        assert params.amplitud == 5.0
        assert params.periodo == 60.0

    def test_parametros_inmutables(self):
        """Verifica que los parámetros son inmutables (frozen)."""
        params = ParametrosSenoidal(20.0, 5.0, 60.0)
        with pytest.raises(AttributeError):
            params.temperatura_base = 30.0


class TestRangosControl:
    """Tests para el dataclass RangosControl."""

    def test_rangos_por_defecto(self):
        """Verifica rangos por defecto."""
        rangos = RangosControl()
        assert rangos.temp_min == -10.0
        assert rangos.temp_max == 50.0
        assert rangos.amplitud_min == 0.0
        assert rangos.amplitud_max == 20.0
        assert rangos.periodo_min == 10.0
        assert rangos.periodo_max == 300.0

    def test_rangos_personalizados(self):
        """Verifica rangos personalizados."""
        rangos = RangosControl(temp_min=0.0, temp_max=100.0)
        assert rangos.temp_min == 0.0
        assert rangos.temp_max == 100.0


class TestSliderConValorCreacion:
    """Tests de creación del SliderConValor."""

    def test_crear_slider(self, qtbot):
        """Verifica creación básica del slider."""
        slider = SliderConValor(
            label="Test:",
            min_val=0.0,
            max_val=100.0,
            valor_inicial=50.0,
        )
        qtbot.addWidget(slider)

        assert slider is not None
        assert slider.valor == 50.0

    def test_crear_slider_con_sufijo(self, qtbot):
        """Verifica creación con sufijo."""
        slider = SliderConValor(
            label="Temp:",
            min_val=-10.0,
            max_val=50.0,
            valor_inicial=20.0,
            sufijo="°C",
        )
        qtbot.addWidget(slider)

        assert slider.valor == 20.0


class TestSliderConValorInteraccion:
    """Tests de interacción con SliderConValor."""

    def test_cambiar_valor_emite_signal(self, qtbot):
        """Verifica que cambiar el valor emite señal."""
        slider = SliderConValor(
            label="Test:",
            min_val=0.0,
            max_val=100.0,
            valor_inicial=50.0,
        )
        qtbot.addWidget(slider)

        with qtbot.waitSignal(slider.valor_cambiado, timeout=1000) as blocker:
            slider._slider.setValue(75 * 10)

        assert blocker.args[0] == 75.0

    def test_set_valor_no_emite_signal(self, qtbot):
        """Verifica que set_valor no emite señal."""
        slider = SliderConValor(
            label="Test:",
            min_val=0.0,
            max_val=100.0,
            valor_inicial=50.0,
        )
        qtbot.addWidget(slider)

        signal_emitido = False

        def on_signal(_):
            nonlocal signal_emitido
            signal_emitido = True

        slider.valor_cambiado.connect(on_signal)
        slider.set_valor(75.0)

        assert slider.valor == 75.0
        assert signal_emitido is False


class TestPanelParametrosSenoidal:
    """Tests para PanelParametrosSenoidal."""

    def test_crear_panel(self, qtbot):
        """Verifica creación del panel."""
        params = ParametrosSenoidal(20.0, 5.0, 60.0)
        rangos = RangosControl()
        panel = PanelParametrosSenoidal(params, rangos)
        qtbot.addWidget(panel)

        assert panel.parametros.temperatura_base == 20.0
        assert panel.parametros.amplitud == 5.0
        assert panel.parametros.periodo == 60.0

    def test_cambiar_parametro_emite_signal(self, qtbot):
        """Verifica que cambiar parámetro emite señal con ParametrosSenoidal."""
        params = ParametrosSenoidal(20.0, 5.0, 60.0)
        rangos = RangosControl()
        panel = PanelParametrosSenoidal(params, rangos)
        qtbot.addWidget(panel)

        with qtbot.waitSignal(panel.parametros_cambiados, timeout=1000) as blocker:
            panel._slider_temp_base._slider.setValue(30 * 10)

        resultado = blocker.args[0]
        assert isinstance(resultado, ParametrosSenoidal)
        assert resultado.temperatura_base == 30.0

    def test_set_parametros(self, qtbot):
        """Verifica set_parametros sin emitir señal."""
        params = ParametrosSenoidal(20.0, 5.0, 60.0)
        rangos = RangosControl()
        panel = PanelParametrosSenoidal(params, rangos)
        qtbot.addWidget(panel)

        nuevos = ParametrosSenoidal(30.0, 10.0, 120.0)
        panel.set_parametros(nuevos)

        assert panel.parametros.temperatura_base == 30.0
        assert panel.parametros.amplitud == 10.0
        assert panel.parametros.periodo == 120.0


class TestPanelTemperaturaManual:
    """Tests para PanelTemperaturaManual."""

    def test_crear_panel(self, qtbot):
        """Verifica creación del panel."""
        rangos = RangosControl()
        panel = PanelTemperaturaManual(25.0, rangos)
        qtbot.addWidget(panel)

        assert panel.temperatura == 25.0

    def test_cambiar_temperatura_emite_signal(self, qtbot):
        """Verifica que cambiar temperatura emite señal."""
        rangos = RangosControl()
        panel = PanelTemperaturaManual(25.0, rangos)
        qtbot.addWidget(panel)

        with qtbot.waitSignal(panel.temperatura_cambiada, timeout=1000) as blocker:
            panel._slider._slider.setValue(35 * 10)

        assert blocker.args[0] == 35.0

    def test_set_temperatura(self, qtbot):
        """Verifica set_temperatura sin emitir señal."""
        rangos = RangosControl()
        panel = PanelTemperaturaManual(25.0, rangos)
        qtbot.addWidget(panel)

        panel.set_temperatura(35.0)
        assert panel.temperatura == 35.0


class TestControlTemperaturaCreacion:
    """Tests de creación del ControlTemperatura."""

    def test_crear_control(self, qtbot):
        """Verifica creación básica del control."""
        control = ControlTemperatura()
        qtbot.addWidget(control)

        assert control is not None
        assert control.es_modo_manual is False

    def test_crear_control_con_valores_iniciales(self, qtbot):
        """Verifica creación con valores iniciales personalizados."""
        control = ControlTemperatura(
            temperatura_inicial=25.0,
            amplitud_inicial=10.0,
            periodo_inicial=120.0,
        )
        qtbot.addWidget(control)

        assert control.temperatura_base == 25.0
        assert control.amplitud == 10.0
        assert control.periodo == 120.0

    def test_crear_control_con_rangos_personalizados(self, qtbot):
        """Verifica creación con rangos personalizados."""
        rangos = RangosControl(temp_min=0.0, temp_max=100.0)
        control = ControlTemperatura(rangos=rangos)
        qtbot.addWidget(control)

        assert control is not None


class TestControlTemperaturaModo:
    """Tests de cambio de modo."""

    def test_cambiar_a_modo_manual(self, qtbot):
        """Verifica cambio a modo manual."""
        control = ControlTemperatura()
        qtbot.addWidget(control)

        with qtbot.waitSignal(control.modo_cambiado, timeout=1000) as blocker:
            control._modo_combo.setCurrentIndex(1)

        assert blocker.args[0] is True
        assert control.es_modo_manual is True

    def test_cambiar_a_modo_automatico(self, qtbot):
        """Verifica cambio a modo automático."""
        control = ControlTemperatura()
        qtbot.addWidget(control)
        control._modo_combo.setCurrentIndex(1)

        with qtbot.waitSignal(control.modo_cambiado, timeout=1000) as blocker:
            control._modo_combo.setCurrentIndex(0)

        assert blocker.args[0] is False
        assert control.es_modo_manual is False

    def test_set_modo_no_emite_signal(self, qtbot):
        """Verifica que set_modo no emite señal."""
        control = ControlTemperatura()
        qtbot.addWidget(control)

        signal_emitido = False

        def on_signal(_):
            nonlocal signal_emitido
            signal_emitido = True

        control.modo_cambiado.connect(on_signal)
        control.set_modo(True)

        assert control.es_modo_manual is True
        assert signal_emitido is False


class TestControlTemperaturaParametrosSenoidal:
    """Tests de parámetros senoidales."""

    def test_cambiar_parametro_emite_signal_con_dataclass(self, qtbot):
        """Verifica que cambiar parámetro emite ParametrosSenoidal."""
        control = ControlTemperatura(temperatura_inicial=20.0)
        qtbot.addWidget(control)

        with qtbot.waitSignal(
            control.parametros_senoidal_cambiados, timeout=1000
        ) as blocker:
            control._panel_senoidal._slider_temp_base._slider.setValue(30 * 10)

        resultado = blocker.args[0]
        assert isinstance(resultado, ParametrosSenoidal)
        assert resultado.temperatura_base == 30.0

    def test_parametros_senoidal_property(self, qtbot):
        """Verifica property parametros_senoidal."""
        control = ControlTemperatura(
            temperatura_inicial=25.0,
            amplitud_inicial=10.0,
            periodo_inicial=90.0,
        )
        qtbot.addWidget(control)

        params = control.parametros_senoidal
        assert params.temperatura_base == 25.0
        assert params.amplitud == 10.0
        assert params.periodo == 90.0

    def test_set_parametros_senoidal(self, qtbot):
        """Verifica set_parametros_senoidal."""
        control = ControlTemperatura()
        qtbot.addWidget(control)

        nuevos = ParametrosSenoidal(30.0, 15.0, 180.0)
        control.set_parametros_senoidal(nuevos)

        assert control.temperatura_base == 30.0
        assert control.amplitud == 15.0
        assert control.periodo == 180.0


class TestControlTemperaturaModoManual:
    """Tests del modo manual."""

    def test_cambiar_temperatura_manual(self, qtbot):
        """Verifica cambio de temperatura en modo manual."""
        control = ControlTemperatura()
        qtbot.addWidget(control)
        control.set_modo(True)

        with qtbot.waitSignal(
            control.temperatura_manual_cambiada, timeout=1000
        ) as blocker:
            control._panel_manual._slider._slider.setValue(35 * 10)

        assert blocker.args[0] == 35.0

    def test_temperatura_manual_property(self, qtbot):
        """Verifica property de temperatura manual."""
        control = ControlTemperatura(temperatura_inicial=20.0)
        qtbot.addWidget(control)

        assert control.temperatura_manual == 20.0

    def test_set_temperatura_manual(self, qtbot):
        """Verifica set_temperatura_manual."""
        control = ControlTemperatura()
        qtbot.addWidget(control)

        control.set_temperatura_manual(35.0)
        assert control.temperatura_manual == 35.0
