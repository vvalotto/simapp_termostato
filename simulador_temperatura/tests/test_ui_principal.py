"""Tests unitarios para UIPrincipal."""
import pytest

from app.presentacion import (
    UIPrincipal,
    ConfigVentana,
    PanelEstado,
    ConfigPanelEstado,
    ConfigTemaOscuro,
    ControlTemperatura,
    GraficoTemperatura,
    ParametrosSenoidal,
    RangosControl,
    ConfigGrafico,
)


class TestConfigVentana:
    """Tests para el dataclass ConfigVentana."""

    def test_config_por_defecto(self):
        """Verifica configuracion por defecto."""
        config = ConfigVentana()
        assert config.titulo == "Simulador de Temperatura"
        assert config.ancho == 1200
        assert config.alto == 700

    def test_config_personalizada(self):
        """Verifica configuracion personalizada."""
        config = ConfigVentana(
            titulo="Test App",
            ancho=800,
            alto=600,
        )
        assert config.titulo == "Test App"
        assert config.ancho == 800
        assert config.alto == 600


class TestConfigPanelEstado:
    """Tests para el dataclass ConfigPanelEstado."""

    def test_config_por_defecto(self):
        """Verifica configuracion por defecto."""
        config = ConfigPanelEstado()
        assert config.titulo == "Estado Actual"
        assert config.texto_conectado == "Conectado"
        assert config.texto_desconectado == "Desconectado"
        assert config.color_temperatura == "#4fc3f7"

    def test_config_personalizada(self):
        """Verifica configuracion personalizada."""
        config = ConfigPanelEstado(
            titulo="Mi Estado",
            color_conectado="#00ff00",
        )
        assert config.titulo == "Mi Estado"
        assert config.color_conectado == "#00ff00"


class TestConfigTemaOscuro:
    """Tests para el dataclass ConfigTemaOscuro."""

    def test_config_por_defecto(self):
        """Verifica configuracion por defecto."""
        tema = ConfigTemaOscuro()
        assert tema.color_fondo == "#1e1e1e"
        assert tema.color_texto == "#d4d4d4"


class TestPanelEstado:
    """Tests para PanelEstado."""

    def test_crear_panel(self, qtbot):
        """Verifica creacion del panel."""
        panel = PanelEstado()
        qtbot.addWidget(panel)
        assert panel is not None

    def test_crear_panel_con_config(self, qtbot):
        """Verifica creacion del panel con configuracion."""
        config = ConfigPanelEstado(titulo="Test Panel")
        panel = PanelEstado(config=config)
        qtbot.addWidget(panel)
        assert panel._config.titulo == "Test Panel"

    def test_actualizar_temperatura(self, qtbot):
        """Verifica actualizacion de temperatura."""
        panel = PanelEstado()
        qtbot.addWidget(panel)

        panel.actualizar_temperatura(25.5)

        assert "25.5" in panel._label_temperatura.text()

    def test_actualizar_estado_conectado(self, qtbot):
        """Verifica actualizacion de estado conectado."""
        panel = PanelEstado()
        qtbot.addWidget(panel)

        panel.actualizar_estado_conexion(True)

        assert panel._label_conexion.text() == "Conectado"

    def test_actualizar_estado_desconectado(self, qtbot):
        """Verifica actualizacion de estado desconectado."""
        panel = PanelEstado()
        qtbot.addWidget(panel)

        panel.actualizar_estado_conexion(False)

        assert panel._label_conexion.text() == "Desconectado"


class TestUIPrincipalCreacion:
    """Tests de creacion de UIPrincipal."""

    def test_crear_ventana(self, qtbot):
        """Verifica creacion basica de la ventana."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        assert ventana is not None
        assert ventana.windowTitle() == "Simulador de Temperatura"

    def test_crear_ventana_con_config(self, qtbot):
        """Verifica creacion con configuracion personalizada."""
        config = ConfigVentana(titulo="Test Window", ancho=800, alto=600)
        ventana = UIPrincipal(config=config)
        qtbot.addWidget(ventana)

        assert ventana.windowTitle() == "Test Window"

    def test_crear_ventana_con_rangos(self, qtbot):
        """Verifica creacion con rangos personalizados."""
        rangos = RangosControl(temp_min=0.0, temp_max=100.0)
        ventana = UIPrincipal(rangos_control=rangos)
        qtbot.addWidget(ventana)

        assert ventana is not None

    def test_crear_ventana_con_config_grafico(self, qtbot):
        """Verifica creacion con configuracion de grafico."""
        config_grafico = ConfigGrafico(ventana_segundos=120)
        ventana = UIPrincipal(config_grafico=config_grafico)
        qtbot.addWidget(ventana)

        assert ventana is not None


class TestUIPrincipalComponentes:
    """Tests de componentes de UIPrincipal."""

    def test_tiene_control_temperatura(self, qtbot):
        """Verifica que tiene widget de control."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        assert isinstance(ventana.control_temperatura, ControlTemperatura)

    def test_tiene_grafico(self, qtbot):
        """Verifica que tiene widget de grafico."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        assert isinstance(ventana.grafico, GraficoTemperatura)

    def test_tiene_panel_estado(self, qtbot):
        """Verifica que tiene panel de estado."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        assert isinstance(ventana.panel_estado, PanelEstado)


class TestUIPrincipalGrafico:
    """Tests de interaccion con el grafico."""

    def test_agregar_punto_grafico(self, qtbot):
        """Verifica agregar punto al grafico."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        ventana.agregar_punto_grafico(25.0)

        assert ventana.grafico.cantidad_puntos == 1
        assert ventana.grafico.ultima_temperatura == 25.0

    def test_actualizar_temperatura_display(self, qtbot):
        """Verifica actualizar temperatura en panel de estado."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        ventana.actualizar_temperatura_display(30.5)

        assert "30.5" in ventana.panel_estado._label_temperatura.text()

    def test_limpiar_grafico(self, qtbot):
        """Verifica limpiar el grafico."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        ventana.agregar_punto_grafico(25.0)
        ventana.limpiar_grafico()

        assert ventana.grafico.cantidad_puntos == 0


class TestUIPrincipalEstadoConexion:
    """Tests de estado de conexion."""

    def test_actualizar_estado_conectado(self, qtbot):
        """Verifica actualizar estado a conectado."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        ventana.actualizar_estado_conexion(True)

        assert ventana.panel_estado._label_conexion.text() == "Conectado"

    def test_actualizar_estado_desconectado(self, qtbot):
        """Verifica actualizar estado a desconectado."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        ventana.actualizar_estado_conexion(False)

        assert ventana.panel_estado._label_conexion.text() == "Desconectado"


class TestUIPrincipalSignals:
    """Tests de signals de UIPrincipal."""

    def test_signal_parametros_cambiados(self, qtbot):
        """Verifica que emite signal de parametros."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        with qtbot.waitSignal(ventana.parametros_cambiados, timeout=1000):
            # Simular cambio en el slider interno
            ventana.control_temperatura._panel_senoidal._slider_temp_base._slider.setValue(
                30 * 10
            )

    def test_signal_temperatura_manual_cambiada(self, qtbot):
        """Verifica que emite signal de temperatura manual."""
        ventana = UIPrincipal()
        qtbot.addWidget(ventana)

        with qtbot.waitSignal(ventana.temperatura_manual_cambiada, timeout=1000):
            # Simular cambio en el slider interno
            ventana.control_temperatura._panel_manual._slider._slider.setValue(35 * 10)
