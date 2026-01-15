"""Tests para ConexionPanelControlador.

Cubre: conectar/desconectar callbacks, signals, actualizar_conexion.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.presentacion.paneles.conexion.modelo import ConexionPanelModelo
from app.presentacion.paneles.conexion.controlador import ConexionPanelControlador


@pytest.fixture
def mock_vista():
    """Mock de ConexionPanelVista para evitar crear UI."""
    with patch('app.presentacion.paneles.conexion.controlador.ConexionPanelVista') as mock_class:
        mock_instance = MagicMock()
        mock_instance.conectar_clicked = MagicMock()
        mock_instance.conectar_clicked.connect = MagicMock()
        mock_instance.desconectar_clicked = MagicMock()
        mock_instance.desconectar_clicked.connect = MagicMock()
        mock_instance.get_ip.return_value = "192.168.1.100"
        mock_instance.get_puerto.return_value = 11000
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def modelo():
    """Modelo de conexion para tests."""
    return ConexionPanelModelo(
        ip="127.0.0.1",
        puerto=11000,
        conectado=False
    )


@pytest.fixture
def controlador(modelo, mock_vista, qtbot):
    """Controlador con modelo y vista mockeada."""
    ctrl = ConexionPanelControlador(modelo=modelo, vista=mock_vista)
    return ctrl


class TestConexionPanelControladorCreacion:
    """Tests de inicializacion del controlador."""

    def test_creacion_con_modelo_y_vista(self, modelo, mock_vista, qtbot):
        """Controlador acepta modelo y vista."""
        ctrl = ConexionPanelControlador(modelo=modelo, vista=mock_vista)

        assert ctrl.modelo is modelo
        assert ctrl.vista is mock_vista

    def test_creacion_crea_modelo_por_defecto(self, mock_vista, qtbot):
        """Controlador crea modelo si no se provee."""
        ctrl = ConexionPanelControlador(vista=mock_vista)

        assert ctrl.modelo is not None
        assert isinstance(ctrl.modelo, ConexionPanelModelo)

    def test_creacion_conecta_signals(self, modelo, mock_vista, qtbot):
        """Controlador conecta signals de botones."""
        ctrl = ConexionPanelControlador(modelo=modelo, vista=mock_vista)

        mock_vista.conectar_clicked.connect.assert_called_once()
        mock_vista.desconectar_clicked.connect.assert_called_once()

    def test_creacion_actualiza_vista(self, modelo, mock_vista, qtbot):
        """Controlador actualiza vista en inicializacion."""
        ctrl = ConexionPanelControlador(modelo=modelo, vista=mock_vista)

        mock_vista.actualizar.assert_called()


class TestConexionPanelControladorConectar:
    """Tests de _on_conectar callback."""

    def test_on_conectar_obtiene_ip_de_vista(self, controlador, mock_vista):
        """_on_conectar lee IP de la vista."""
        controlador._on_conectar()

        mock_vista.get_ip.assert_called_once()

    def test_on_conectar_obtiene_puerto_de_vista(self, controlador, mock_vista):
        """_on_conectar lee puerto de la vista."""
        controlador._on_conectar()

        mock_vista.get_puerto.assert_called_once()

    def test_on_conectar_actualiza_modelo(self, controlador, mock_vista):
        """_on_conectar actualiza IP y puerto en modelo."""
        mock_vista.get_ip.return_value = "10.0.0.1"
        mock_vista.get_puerto.return_value = 12000

        controlador._on_conectar()

        assert controlador.ip == "10.0.0.1"
        assert controlador.puerto == 12000

    def test_on_conectar_emite_signal(self, controlador, mock_vista, qtbot):
        """_on_conectar emite conectar_solicitado con IP y puerto."""
        mock_vista.get_ip.return_value = "192.168.1.50"
        mock_vista.get_puerto.return_value = 8080

        with qtbot.waitSignal(controlador.conectar_solicitado, timeout=1000) as blocker:
            controlador._on_conectar()

        assert blocker.args == ["192.168.1.50", 8080]


class TestConexionPanelControladorDesconectar:
    """Tests de _on_desconectar callback."""

    def test_on_desconectar_emite_signal(self, controlador, qtbot):
        """_on_desconectar emite desconectar_solicitado."""
        with qtbot.waitSignal(controlador.desconectar_solicitado, timeout=1000):
            controlador._on_desconectar()


class TestConexionPanelControladorActualizarConexion:
    """Tests de actualizar_conexion."""

    def test_actualizar_conexion_true(self, controlador):
        """actualizar_conexion establece True."""
        controlador.actualizar_conexion(True)

        assert controlador.conectado is True

    def test_actualizar_conexion_false(self, controlador):
        """actualizar_conexion establece False."""
        controlador.actualizar_conexion(True)
        controlador.actualizar_conexion(False)

        assert controlador.conectado is False

    def test_actualizar_conexion_actualiza_vista(self, controlador, mock_vista):
        """actualizar_conexion llama actualizar en vista."""
        mock_vista.actualizar.reset_mock()

        controlador.actualizar_conexion(True)

        mock_vista.actualizar.assert_called()


class TestConexionPanelControladorSetters:
    """Tests de set_ip y set_puerto."""

    def test_set_ip(self, controlador, mock_vista):
        """set_ip actualiza modelo y vista."""
        mock_vista.actualizar.reset_mock()

        controlador.set_ip("10.0.0.1")

        assert controlador.ip == "10.0.0.1"
        mock_vista.actualizar.assert_called()

    def test_set_ip_strip(self, controlador):
        """set_ip aplica strip a la IP."""
        controlador.set_ip("  192.168.1.1  ")

        assert controlador.ip == "192.168.1.1"

    def test_set_puerto(self, controlador, mock_vista):
        """set_puerto actualiza modelo y vista."""
        mock_vista.actualizar.reset_mock()

        controlador.set_puerto(9999)

        assert controlador.puerto == 9999
        mock_vista.actualizar.assert_called()

    def test_set_puerto_clamp(self, controlador):
        """set_puerto limita al rango valido."""
        controlador.set_puerto(0)
        assert controlador.puerto == 1

        controlador.set_puerto(70000)
        assert controlador.puerto == 65535


class TestConexionPanelControladorProperties:
    """Tests de propiedades de solo lectura."""

    def test_ip(self, controlador):
        """ip retorna valor del modelo."""
        controlador.set_ip("10.0.0.1")

        assert controlador.ip == "10.0.0.1"

    def test_puerto(self, controlador):
        """puerto retorna valor del modelo."""
        controlador.set_puerto(8080)

        assert controlador.puerto == 8080

    def test_conectado(self, controlador):
        """conectado retorna valor del modelo."""
        controlador.actualizar_conexion(True)

        assert controlador.conectado is True
