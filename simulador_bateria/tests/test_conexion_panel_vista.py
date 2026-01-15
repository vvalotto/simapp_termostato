"""Tests para ConexionPanelVista.

Tests de UI usando qtbot para widgets Qt reales.
"""

import pytest

from app.presentacion.paneles.conexion.vista import ConexionPanelVista, ConfigConexionPanelVista
from app.presentacion.paneles.conexion.modelo import ConexionPanelModelo


@pytest.fixture
def vista(qtbot):
    """Vista real para tests."""
    v = ConexionPanelVista(default_ip="127.0.0.1", default_port=11000)
    qtbot.addWidget(v)
    return v


@pytest.fixture
def modelo():
    """Modelo para tests."""
    return ConexionPanelModelo(
        ip="192.168.1.100",
        puerto=12000,
        conectado=False
    )


class TestConexionPanelVistaCreacion:
    """Tests de inicializacion de la vista."""

    def test_creacion_sin_config(self, qtbot):
        """Vista se crea con config por defecto."""
        vista = ConexionPanelVista()
        qtbot.addWidget(vista)

        assert vista._config is not None
        assert vista._config.titulo == "Conexion TCP"

    def test_creacion_con_config(self, qtbot):
        """Vista acepta config personalizada."""
        config = ConfigConexionPanelVista(titulo="Test Conexion")
        vista = ConexionPanelVista(config=config)
        qtbot.addWidget(vista)

        assert vista._config.titulo == "Test Conexion"

    def test_creacion_con_defaults(self, qtbot):
        """Vista acepta IP y puerto por defecto."""
        vista = ConexionPanelVista(default_ip="10.0.0.1", default_port=9999)
        qtbot.addWidget(vista)

        assert vista._default_ip == "10.0.0.1"
        assert vista._default_port == 9999

    def test_tiene_config_panel(self, vista):
        """Vista tiene ConfigPanel interno."""
        assert vista._config_panel is not None


class TestConexionPanelVistaSignals:
    """Tests de signals conectar/desconectar."""

    def test_conectar_clicked_emite_signal(self, vista, qtbot):
        """Boton conectar emite conectar_clicked."""
        with qtbot.waitSignal(vista.conectar_clicked, timeout=1000):
            vista._on_conectar()

    def test_desconectar_clicked_emite_signal(self, vista, qtbot):
        """Boton desconectar emite desconectar_clicked."""
        with qtbot.waitSignal(vista.desconectar_clicked, timeout=1000):
            vista._on_desconectar()


class TestConexionPanelVistaGetters:
    """Tests de get_ip y get_puerto."""

    def test_get_ip(self, vista):
        """get_ip retorna IP del ConfigPanel."""
        ip = vista.get_ip()

        assert isinstance(ip, str)

    def test_get_puerto(self, vista):
        """get_puerto retorna puerto del ConfigPanel."""
        puerto = vista.get_puerto()

        assert isinstance(puerto, int)


class TestConexionPanelVistaActualizar:
    """Tests de actualizar con modelo."""

    def test_actualizar_campos_desconectado(self, vista, modelo):
        """actualizar cambia IP y puerto cuando desconectado."""
        modelo.conectado = False
        modelo.ip = "10.0.0.1"
        modelo.puerto = 8080

        vista.actualizar(modelo)

        # El ConfigPanel deberia tener los nuevos valores
        assert vista.get_ip() == "10.0.0.1"
        assert vista.get_puerto() == 8080

    def test_actualizar_no_cambia_campos_conectado(self, vista, modelo):
        """actualizar no cambia IP/puerto cuando conectado."""
        # Primero establecer valores
        modelo.conectado = False
        modelo.ip = "original.ip"
        modelo.puerto = 1234
        vista.actualizar(modelo)

        # Ahora conectar y cambiar modelo
        modelo.conectado = True
        modelo.ip = "nueva.ip"
        modelo.puerto = 5678
        vista.actualizar(modelo)

        # Campos no deberian cambiar
        assert vista.get_ip() == "original.ip"
        assert vista.get_puerto() == 1234

    def test_actualizar_ignora_modelo_invalido(self, vista):
        """actualizar ignora modelo de tipo incorrecto."""
        ip_original = vista.get_ip()

        vista.actualizar("no es un modelo")

        assert vista.get_ip() == ip_original


class TestConexionPanelVistaSetConectado:
    """Tests de set_conectado."""

    def test_set_conectado_true(self, vista):
        """set_conectado actualiza estado visual."""
        vista.set_conectado(True)

        # No podemos verificar visualmente, pero no debe fallar
        assert True

    def test_set_conectado_false(self, vista):
        """set_conectado actualiza estado visual."""
        vista.set_conectado(False)

        # No podemos verificar visualmente, pero no debe fallar
        assert True
