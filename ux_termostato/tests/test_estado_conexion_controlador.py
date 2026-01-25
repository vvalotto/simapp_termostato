"""
Tests del controlador del panel Estado Conexion.

Valida gestión de cambios de estado y emisión de señales.
"""

import pytest

from app.presentacion.paneles.estado_conexion import (
    EstadoConexionModelo,
    EstadoConexionVista,
    EstadoConexionControlador,
)


@pytest.fixture
def modelo():
    """Fixture de modelo de estado conexión."""
    return EstadoConexionModelo(estado="desconectado")


@pytest.fixture
def vista(qapp):
    """Fixture de vista de estado conexión."""
    return EstadoConexionVista()


@pytest.fixture
def controlador(modelo, vista):
    """Fixture de controlador de estado conexión."""
    return EstadoConexionControlador(modelo, vista)


class TestCreacion:
    """Tests de creación del controlador."""

    def test_creacion_exitosa(self, controlador):
        """Debe crear controlador sin errores."""
        assert controlador is not None

    def test_creacion_inicializa_vista(self, modelo, vista, qapp):
        """Debe inicializar vista con modelo."""
        controlador = EstadoConexionControlador(modelo, vista)

        assert vista._label_estado.text() == "Desconectado"

    def test_property_modelo_retorna_modelo_actual(self, controlador, modelo):
        """Property modelo debe retornar modelo actual."""
        assert controlador.modelo == modelo


class TestActualizarEstado:
    """Tests de actualización de estado."""

    def test_actualizar_a_conectado_emite_signal(self, controlador, qtbot):
        """Actualizar a conectado debe emitir señal."""
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.actualizar_estado("conectado", "192.168.1.50")

        assert blocker.args == ["conectado"]

    def test_actualizar_a_conectado_actualiza_modelo(self, controlador):
        """Actualizar a conectado debe actualizar modelo."""
        controlador.actualizar_estado("conectado", "192.168.1.50")

        assert controlador.modelo.estado == "conectado"
        assert controlador.modelo.direccion_ip == "192.168.1.50"

    def test_actualizar_a_desconectado_emite_signal(self, controlador, qtbot):
        """Actualizar a desconectado debe emitir señal."""
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.actualizar_estado("desconectado")

        assert blocker.args == ["desconectado"]

    def test_actualizar_a_desconectado_limpia_ip(self, controlador):
        """Actualizar a desconectado debe limpiar IP."""
        # Primero conectar
        controlador.actualizar_estado("conectado", "192.168.1.50")

        # Luego desconectar
        controlador.actualizar_estado("desconectado")

        assert controlador.modelo.estado == "desconectado"
        assert controlador.modelo.direccion_ip == ""

    def test_actualizar_a_conectando_emite_signal(self, controlador, qtbot):
        """Actualizar a conectando debe emitir señal."""
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.actualizar_estado("conectando")

        assert blocker.args == ["conectando"]


class TestConexionEstablecida:
    """Tests del método conexion_establecida()."""

    def test_conexion_establecida_cambia_estado(self, controlador, vista):
        """Debe cambiar estado a conectado."""
        controlador.conexion_establecida("192.168.1.50:14001")

        assert controlador.modelo.estado == "conectado"
        assert vista._label_estado.text() == "Conectado"

    def test_conexion_establecida_extrae_ip_de_direccion(self, controlador):
        """Debe extraer IP de dirección con puerto."""
        controlador.conexion_establecida("192.168.1.50:14001")

        assert controlador.modelo.direccion_ip == "192.168.1.50"

    def test_conexion_establecida_sin_puerto(self, controlador):
        """Debe aceptar dirección sin puerto."""
        controlador.conexion_establecida("10.0.0.1")

        assert controlador.modelo.estado == "conectado"
        assert controlador.modelo.direccion_ip == "10.0.0.1"

    def test_conexion_establecida_emite_signal(self, controlador, qtbot):
        """Debe emitir señal estado_cambiado."""
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.conexion_establecida("192.168.1.50:14001")

        assert blocker.args == ["conectado"]


class TestConexionPerdida:
    """Tests del método conexion_perdida()."""

    def test_conexion_perdida_cambia_estado(self, controlador, vista):
        """Debe cambiar estado a desconectado."""
        # Primero conectar
        controlador.conexion_establecida("192.168.1.50")

        # Luego perder conexión
        controlador.conexion_perdida()

        assert controlador.modelo.estado == "desconectado"
        assert vista._label_estado.text() == "Desconectado"

    def test_conexion_perdida_limpia_ip(self, controlador):
        """Debe limpiar dirección IP."""
        # Primero conectar
        controlador.conexion_establecida("192.168.1.50")

        # Luego perder conexión
        controlador.conexion_perdida()

        assert controlador.modelo.direccion_ip == ""

    def test_conexion_perdida_emite_signal(self, controlador, qtbot):
        """Debe emitir señal estado_cambiado."""
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.conexion_perdida()

        assert blocker.args == ["desconectado"]


class TestConectando:
    """Tests del método conectando()."""

    def test_conectando_cambia_estado(self, controlador, vista):
        """Debe cambiar estado a conectando."""
        controlador.conectando()

        assert controlador.modelo.estado == "conectando"
        assert vista._label_estado.text() == "Conectando..."

    def test_conectando_inicia_animacion(self, controlador, vista):
        """Debe iniciar animación de pulso."""
        controlador.conectando()

        assert vista._pulso_activo is True

        # Limpiar
        vista._detener_pulso()

    def test_conectando_emite_signal(self, controlador, qtbot):
        """Debe emitir señal estado_cambiado."""
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000) as blocker:
            controlador.conectando()

        assert blocker.args == ["conectando"]


class TestFlujos:
    """Tests de flujos completos."""

    def test_flujo_conectando_a_conectado(self, controlador, vista, qtbot):
        """Flujo: conectando → conectado."""
        # 1. Conectando
        controlador.conectando()
        assert controlador.modelo.estado == "conectando"
        assert vista._pulso_activo is True

        # 2. Conectado
        controlador.conexion_establecida("192.168.1.50:14001")
        assert controlador.modelo.estado == "conectado"
        assert vista._pulso_activo is False  # Pulso detenido

    def test_flujo_conectando_a_desconectado(self, controlador, vista):
        """Flujo: conectando → desconectado (falla conexión)."""
        # 1. Conectando
        controlador.conectando()
        assert controlador.modelo.estado == "conectando"

        # 2. Falla conexión
        controlador.conexion_perdida()
        assert controlador.modelo.estado == "desconectado"

    def test_flujo_conectado_a_desconectado(self, controlador, qtbot):
        """Flujo: conectado → desconectado."""
        # 1. Conectar
        controlador.conexion_establecida("192.168.1.50")
        assert controlador.modelo.direccion_ip == "192.168.1.50"

        # 2. Desconectar
        with qtbot.waitSignal(controlador.estado_cambiado, timeout=1000):
            controlador.conexion_perdida()

        assert controlador.modelo.estado == "desconectado"
        assert controlador.modelo.direccion_ip == ""

    def test_multiple_cambios_estado(self, controlador, qtbot):
        """Múltiples cambios de estado."""
        # Desconectado → Conectando
        controlador.conectando()
        assert controlador.modelo.estado == "conectando"

        # Conectando → Conectado
        controlador.conexion_establecida("192.168.1.50")
        assert controlador.modelo.estado == "conectado"

        # Conectado → Desconectado
        controlador.conexion_perdida()
        assert controlador.modelo.estado == "desconectado"

        # Desconectado → Conectando
        controlador.conectando()
        assert controlador.modelo.estado == "conectando"

        # Conectando → Conectado
        controlador.conexion_establecida("10.0.0.1")
        assert controlador.modelo.estado == "conectado"
        assert controlador.modelo.direccion_ip == "10.0.0.1"
