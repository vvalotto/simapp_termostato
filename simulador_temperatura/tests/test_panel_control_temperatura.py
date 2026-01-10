"""Tests para el Panel de Control de Temperatura MVC."""

import pytest

from app.presentacion.paneles.control_temperatura import (
    ModoOperacion,
    ParametrosSenoidal,
    RangosControl,
    ParametrosControl,
    SliderConValor,
    ControlTemperaturaVista,
    ControlTemperaturaControlador,
)


class TestModoOperacion:
    """Tests para el enum ModoOperacion."""

    def test_modo_automatico(self):
        """ModoOperacion tiene valor AUTOMATICO."""
        assert ModoOperacion.AUTOMATICO.value == "automatico"

    def test_modo_manual(self):
        """ModoOperacion tiene valor MANUAL."""
        assert ModoOperacion.MANUAL.value == "manual"


class TestParametrosSenoidal:
    """Tests para ParametrosSenoidal."""

    def test_crear_por_defecto(self):
        """Crear con valores por defecto."""
        params = ParametrosSenoidal()

        assert params.temperatura_base == 22.0
        assert params.amplitud == 5.0
        assert params.periodo == 60.0

    def test_crear_con_valores(self):
        """Crear con valores personalizados."""
        params = ParametrosSenoidal(
            temperatura_base=25.0,
            amplitud=3.0,
            periodo=120.0
        )

        assert params.temperatura_base == 25.0
        assert params.amplitud == 3.0
        assert params.periodo == 120.0


class TestRangosControl:
    """Tests para RangosControl."""

    def test_rangos_por_defecto(self):
        """Rangos tienen valores por defecto sensibles."""
        rangos = RangosControl()

        assert rangos.temp_min == -10.0
        assert rangos.temp_max == 50.0
        assert rangos.amplitud_min == 0.0
        assert rangos.amplitud_max == 20.0
        assert rangos.periodo_min == 10.0
        assert rangos.periodo_max == 300.0

    def test_rangos_personalizados(self):
        """Rangos aceptan valores personalizados."""
        rangos = RangosControl(temp_min=0.0, temp_max=40.0)

        assert rangos.temp_min == 0.0
        assert rangos.temp_max == 40.0


class TestParametrosControl:
    """Tests para el modelo ParametrosControl."""

    def test_crear_por_defecto(self):
        """Crear con valores por defecto."""
        params = ParametrosControl()

        assert params.modo == ModoOperacion.AUTOMATICO
        assert params.temperatura_base == 22.0
        assert params.amplitud == 5.0
        assert params.periodo == 60.0
        assert params.temperatura_manual == 22.0

    def test_es_manual_false_por_defecto(self):
        """es_manual es False por defecto."""
        params = ParametrosControl()

        assert params.es_manual is False

    def test_cambiar_a_manual(self):
        """cambiar_a_manual cambia el modo."""
        params = ParametrosControl()

        params.cambiar_a_manual()

        assert params.modo == ModoOperacion.MANUAL
        assert params.es_manual is True

    def test_cambiar_a_automatico(self):
        """cambiar_a_automatico cambia el modo."""
        params = ParametrosControl(modo=ModoOperacion.MANUAL)

        params.cambiar_a_automatico()

        assert params.modo == ModoOperacion.AUTOMATICO
        assert params.es_manual is False

    def test_parametros_senoidal_property(self):
        """parametros_senoidal retorna dataclass correcta."""
        params = ParametrosControl(
            temperatura_base=25.0,
            amplitud=3.0,
            periodo=90.0
        )

        senoidal = params.parametros_senoidal

        assert isinstance(senoidal, ParametrosSenoidal)
        assert senoidal.temperatura_base == 25.0
        assert senoidal.amplitud == 3.0
        assert senoidal.periodo == 90.0


class TestSliderConValor:
    """Tests para SliderConValor widget."""

    def test_crear_slider(self, qtbot):
        """Crear slider con parámetros."""
        slider = SliderConValor(
            label="Test:",
            min_val=0.0,
            max_val=100.0,
            valor_inicial=50.0,
            sufijo="°C",
            decimales=1
        )
        qtbot.addWidget(slider)

        assert slider.valor == 50.0

    def test_set_valor(self, qtbot):
        """set_valor actualiza el slider."""
        slider = SliderConValor(
            label="Test:",
            min_val=0.0,
            max_val=100.0,
            valor_inicial=50.0
        )
        qtbot.addWidget(slider)

        slider.set_valor(75.0)

        assert slider.valor == 75.0

    def test_valor_cambiado_signal(self, qtbot):
        """Emite signal cuando cambia valor."""
        slider = SliderConValor(
            label="Test:",
            min_val=0.0,
            max_val=100.0,
            valor_inicial=50.0,
            decimales=0
        )
        qtbot.addWidget(slider)

        with qtbot.waitSignal(slider.valor_cambiado, timeout=1000) as blocker:
            slider._slider.setValue(70)

        assert blocker.args[0] == 70.0


class TestControlTemperaturaVista:
    """Tests para ControlTemperaturaVista."""

    def test_crear_vista(self, qtbot):
        """Crear vista con valores por defecto."""
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)

        assert vista is not None
        assert vista.es_modo_manual is False

    def test_crear_vista_con_rangos(self, qtbot):
        """Crear vista con rangos personalizados."""
        rangos = RangosControl(temp_min=0.0, temp_max=40.0)
        vista = ControlTemperaturaVista(rangos=rangos)
        qtbot.addWidget(vista)

        assert vista is not None

    def test_propiedades_valores(self, qtbot):
        """Las propiedades retornan valores iniciales."""
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)

        assert vista.temperatura_base == 22.0
        assert vista.amplitud == 5.0
        assert vista.periodo == 60.0
        assert vista.temperatura_manual == 22.0

    def test_modo_cambiado_signal(self, qtbot):
        """Emite signal cuando cambia modo."""
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)

        with qtbot.waitSignal(vista.modo_cambiado, timeout=1000) as blocker:
            vista._modo_combo.setCurrentIndex(1)

        assert blocker.args[0] is True

    def test_temperatura_base_cambiada_signal(self, qtbot):
        """Emite signal cuando cambia temperatura base."""
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)

        with qtbot.waitSignal(vista.temperatura_base_cambiada, timeout=1000) as blocker:
            vista._slider_temp_base._slider.setValue(250)

        assert blocker.args[0] == 25.0

    def test_amplitud_cambiada_signal(self, qtbot):
        """Emite signal cuando cambia amplitud."""
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)

        with qtbot.waitSignal(vista.amplitud_cambiada, timeout=1000) as blocker:
            vista._slider_amplitud._slider.setValue(80)

        assert blocker.args[0] == 8.0

    def test_actualizar_con_modelo(self, qtbot):
        """actualizar() actualiza la vista."""
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)
        modelo = ParametrosControl(
            modo=ModoOperacion.MANUAL,
            temperatura_base=25.0,
            amplitud=8.0,
            periodo=90.0,
            temperatura_manual=30.0
        )

        vista.actualizar(modelo)

        assert vista.es_modo_manual is True
        assert vista.temperatura_base == 25.0
        assert vista.amplitud == 8.0
        assert vista.periodo == 90.0
        assert vista.temperatura_manual == 30.0


class TestControlTemperaturaControlador:
    """Tests para ControlTemperaturaControlador."""

    def test_crear_controlador(self, qtbot):
        """Crear controlador sin argumentos."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        assert controlador.modelo is not None
        assert controlador.vista is not None

    def test_crear_con_modelo_y_vista(self, qtbot):
        """Crear controlador con modelo y vista existentes."""
        modelo = ParametrosControl(temperatura_base=25.0)
        vista = ControlTemperaturaVista()
        qtbot.addWidget(vista)

        controlador = ControlTemperaturaControlador(modelo=modelo, vista=vista)

        assert controlador.modelo is modelo
        assert controlador.vista is vista

    def test_propiedades(self, qtbot):
        """Las propiedades delegan al modelo."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        assert controlador.es_modo_manual is False
        assert controlador.temperatura_base == 22.0
        assert controlador.amplitud == 5.0
        assert controlador.periodo == 60.0
        assert controlador.temperatura_manual == 22.0

    def test_set_modo_manual(self, qtbot):
        """set_modo cambia el modo sin emitir signal."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        controlador.set_modo(True)

        assert controlador.es_modo_manual is True

    def test_set_modo_automatico(self, qtbot):
        """set_modo puede volver a automático."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)
        controlador.set_modo(True)

        controlador.set_modo(False)

        assert controlador.es_modo_manual is False

    def test_set_parametros_senoidal(self, qtbot):
        """set_parametros_senoidal actualiza valores."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)
        params = ParametrosSenoidal(
            temperatura_base=25.0,
            amplitud=8.0,
            periodo=120.0
        )

        controlador.set_parametros_senoidal(params)

        assert controlador.temperatura_base == 25.0
        assert controlador.amplitud == 8.0
        assert controlador.periodo == 120.0

    def test_set_temperatura_manual(self, qtbot):
        """set_temperatura_manual actualiza el valor."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        controlador.set_temperatura_manual(30.0)

        assert controlador.temperatura_manual == 30.0

    def test_modo_cambiado_signal(self, qtbot):
        """Vista emite signal que controlador propaga."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            controlador.vista._modo_combo.setCurrentIndex(1)

        assert blocker.args[0] is True
        assert controlador.es_modo_manual is True

    def test_parametros_cambiados_signal(self, qtbot):
        """Cambios en parámetros emiten signal."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.parametros_cambiados, timeout=1000) as blocker:
            controlador.vista._slider_temp_base._slider.setValue(250)

        params = blocker.args[0]
        assert isinstance(params, ParametrosSenoidal)
        assert params.temperatura_base == 25.0

    def test_temperatura_manual_cambiada_signal(self, qtbot):
        """Cambios en temp manual emiten signal."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.temperatura_manual_cambiada, timeout=1000) as blocker:
            controlador.vista._slider_manual._slider.setValue(300)

        assert blocker.args[0] == 30.0

    def test_parametros_senoidal_property(self, qtbot):
        """parametros_senoidal retorna ParametrosSenoidal."""
        controlador = ControlTemperaturaControlador()
        qtbot.addWidget(controlador.vista)

        params = controlador.parametros_senoidal

        assert isinstance(params, ParametrosSenoidal)
        assert params.temperatura_base == 22.0
        assert params.amplitud == 5.0
        assert params.periodo == 60.0
