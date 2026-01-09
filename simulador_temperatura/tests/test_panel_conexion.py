"""Tests para el Panel de Conexión MVC."""

import pytest

from app.presentacion.paneles.conexion import (
    EstadoConexion,
    ConfiguracionConexion,
    ConfigPanelConexionVista,
    PanelConexionVista,
    PanelConexionControlador,
)


class TestEstadoConexion:
    """Tests para el enum EstadoConexion."""

    def test_estados_disponibles(self):
        """Verificar que existen los estados esperados."""
        assert EstadoConexion.DESCONECTADO.value == "desconectado"
        assert EstadoConexion.CONECTANDO.value == "conectando"
        assert EstadoConexion.CONECTADO.value == "conectado"
        assert EstadoConexion.ERROR.value == "error"


class TestConfiguracionConexion:
    """Tests para el modelo ConfiguracionConexion."""

    def test_crear_por_defecto(self):
        """Crear modelo con valores por defecto."""
        config = ConfiguracionConexion()

        assert config.ip == "127.0.0.1"
        assert config.puerto == 14001
        assert config.estado == EstadoConexion.DESCONECTADO
        assert config.mensaje_error == ""

    def test_crear_con_valores(self):
        """Crear modelo con valores personalizados."""
        config = ConfiguracionConexion(
            ip="192.168.1.100",
            puerto=12000
        )

        assert config.ip == "192.168.1.100"
        assert config.puerto == 12000

    def test_esta_conectado_false_por_defecto(self):
        """esta_conectado es False por defecto."""
        config = ConfiguracionConexion()

        assert config.esta_conectado is False

    def test_conectar(self):
        """conectar() cambia estado a CONECTANDO."""
        config = ConfiguracionConexion()

        config.conectar()

        assert config.estado == EstadoConexion.CONECTANDO
        assert config.esta_conectando is True

    def test_confirmar_conexion(self):
        """confirmar_conexion() cambia estado a CONECTADO."""
        config = ConfiguracionConexion()
        config.conectar()

        config.confirmar_conexion()

        assert config.estado == EstadoConexion.CONECTADO
        assert config.esta_conectado is True

    def test_desconectar(self):
        """desconectar() cambia estado a DESCONECTADO."""
        config = ConfiguracionConexion(estado=EstadoConexion.CONECTADO)

        config.desconectar()

        assert config.estado == EstadoConexion.DESCONECTADO
        assert config.esta_conectado is False

    def test_registrar_error(self):
        """registrar_error() establece estado ERROR y mensaje."""
        config = ConfiguracionConexion()

        config.registrar_error("Conexión rechazada")

        assert config.estado == EstadoConexion.ERROR
        assert config.tiene_error is True
        assert config.mensaje_error == "Conexión rechazada"

    def test_direccion_completa(self):
        """direccion_completa retorna IP:puerto."""
        config = ConfiguracionConexion(
            ip="192.168.1.100",
            puerto=12000
        )

        assert config.direccion_completa == "192.168.1.100:12000"


class TestConfigPanelConexionVista:
    """Tests para ConfigPanelConexionVista."""

    def test_valores_por_defecto(self):
        """Verificar valores por defecto de configuración."""
        config = ConfigPanelConexionVista()

        assert config.ip_label == "IP Servidor:"
        assert config.puerto_label == "Puerto:"
        assert config.texto_conectar == "Conectar"
        assert config.texto_desconectar == "Desconectar"


class TestPanelConexionVista:
    """Tests para PanelConexionVista."""

    def test_crear_vista(self, qtbot):
        """Crear vista con valores por defecto."""
        vista = PanelConexionVista()
        qtbot.addWidget(vista)

        assert vista is not None
        assert vista.ip == "127.0.0.1"
        assert vista.puerto == 14001

    def test_crear_con_valores_iniciales(self, qtbot):
        """Crear vista con valores iniciales personalizados."""
        vista = PanelConexionVista(
            ip_inicial="192.168.1.100",
            puerto_inicial=12000
        )
        qtbot.addWidget(vista)

        assert vista.ip == "192.168.1.100"
        assert vista.puerto == 12000

    def test_set_ip(self, qtbot):
        """set_ip actualiza la IP."""
        vista = PanelConexionVista()
        qtbot.addWidget(vista)

        vista.set_ip("10.0.0.1")

        assert vista.ip == "10.0.0.1"

    def test_set_puerto(self, qtbot):
        """set_puerto actualiza el puerto."""
        vista = PanelConexionVista()
        qtbot.addWidget(vista)

        vista.set_puerto(8080)

        assert vista.puerto == 8080

    def test_conexion_solicitada_signal(self, qtbot):
        """Emite signal cuando se solicita conexión."""
        vista = PanelConexionVista()
        qtbot.addWidget(vista)

        with qtbot.waitSignal(vista.conexion_solicitada, timeout=1000):
            # Simular clic en botón conectar
            vista._config_panel._connect_button.click()

    def test_actualizar_con_modelo(self, qtbot):
        """actualizar() sincroniza la vista con el modelo."""
        vista = PanelConexionVista()
        qtbot.addWidget(vista)
        modelo = ConfiguracionConexion(
            ip="10.0.0.1",
            puerto=8080,
            estado=EstadoConexion.CONECTADO
        )

        vista.actualizar(modelo)

        assert vista.ip == "10.0.0.1"
        assert vista.puerto == 8080
        assert vista.esta_conectado is True


class TestPanelConexionControlador:
    """Tests para PanelConexionControlador."""

    def test_crear_controlador(self, qtbot):
        """Crear controlador sin argumentos."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        assert controlador.modelo is not None
        assert controlador.vista is not None
        assert controlador.ip == "127.0.0.1"
        assert controlador.puerto == 14001

    def test_crear_con_valores_iniciales(self, qtbot):
        """Crear controlador con valores iniciales."""
        controlador = PanelConexionControlador(
            ip_inicial="192.168.1.100",
            puerto_inicial=12000
        )
        qtbot.addWidget(controlador.vista)

        assert controlador.ip == "192.168.1.100"
        assert controlador.puerto == 12000

    def test_confirmar_conexion(self, qtbot):
        """confirmar_conexion() actualiza estado."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        controlador.confirmar_conexion()

        assert controlador.esta_conectado is True
        assert controlador.estado == EstadoConexion.CONECTADO

    def test_confirmar_conexion_emite_signal(self, qtbot):
        """confirmar_conexion() emite signal."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.confirmar_conexion()

        assert blocker.args[0] is True

    def test_registrar_error(self, qtbot):
        """registrar_error() actualiza estado y mensaje."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        controlador.registrar_error("Error de conexión")

        assert controlador.estado == EstadoConexion.ERROR
        assert controlador.mensaje_error == "Error de conexión"

    def test_desconectar(self, qtbot):
        """desconectar() actualiza estado."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)
        controlador.confirmar_conexion()

        controlador.desconectar()

        assert controlador.esta_conectado is False
        assert controlador.estado == EstadoConexion.DESCONECTADO

    def test_set_ip(self, qtbot):
        """set_ip actualiza IP sin emitir signal."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        controlador.set_ip("10.0.0.1")

        assert controlador.ip == "10.0.0.1"

    def test_set_puerto(self, qtbot):
        """set_puerto actualiza puerto sin emitir signal."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        controlador.set_puerto(8080)

        assert controlador.puerto == 8080

    def test_direccion_completa(self, qtbot):
        """direccion_completa retorna formato correcto."""
        controlador = PanelConexionControlador(
            ip_inicial="192.168.1.100",
            puerto_inicial=12000
        )
        qtbot.addWidget(controlador.vista)

        assert controlador.direccion_completa == "192.168.1.100:12000"

    def test_conexion_solicitada_signal(self, qtbot):
        """Vista emite signal que controlador propaga."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.conexion_solicitada, timeout=1000):
            controlador.vista._config_panel._connect_button.click()

    def test_ciclo_conexion_completo(self, qtbot):
        """Ciclo completo: conectar -> confirmar -> desconectar."""
        controlador = PanelConexionControlador()
        qtbot.addWidget(controlador.vista)

        # Inicialmente desconectado
        assert controlador.esta_conectado is False

        # Confirmar conexión
        controlador.confirmar_conexion()
        assert controlador.esta_conectado is True

        # Desconectar
        controlador.desconectar()
        assert controlador.esta_conectado is False
