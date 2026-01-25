"""
Tests del controlador del panel Conexion.

Valida gestión de validación en tiempo real y emisión de señales.
"""

import pytest

from app.presentacion.paneles.conexion import (
    ConexionModelo,
    ConexionVista,
    ConexionControlador,
)


@pytest.fixture
def modelo():
    """Fixture de modelo de conexión."""
    return ConexionModelo(
        ip="192.168.1.50",
        puerto_recv=14001,
        puerto_send=14000,
    )


@pytest.fixture
def vista(qapp):
    """Fixture de vista de conexión."""
    return ConexionVista()


@pytest.fixture
def controlador(modelo, vista):
    """Fixture de controlador de conexión."""
    return ConexionControlador(modelo, vista)


class TestCreacion:
    """Tests de creación del controlador."""

    def test_creacion_exitosa(self, controlador):
        """Debe crear controlador sin errores."""
        assert controlador is not None

    def test_creacion_conecta_signals(self, modelo, vista, qapp):
        """Debe conectar señales de la vista."""
        controlador = ConexionControlador(modelo, vista)

        # Verificar que las señales están conectadas (no crashea al emitir)
        vista.input_ip.setText("192.168.1.100")
        vista.boton_aplicar.click()

    def test_creacion_inicializa_vista(self, modelo, vista, qapp):
        """Debe inicializar vista con modelo."""
        controlador = ConexionControlador(modelo, vista)

        assert vista.input_ip.text() == "192.168.1.50"


class TestValidacionTiempoReal:
    """Tests de validación en tiempo real de IP."""

    def test_cambio_a_ip_valida_actualiza_modelo(self, controlador, vista, qtbot):
        """Cambio a IP válida debe actualizar modelo."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "10.0.0.1")

        assert controlador.modelo.ip == "10.0.0.1"
        assert controlador.modelo.ip_valida is True

    def test_cambio_a_ip_invalida_actualiza_modelo(self, controlador, vista, qtbot):
        """Cambio a IP inválida debe actualizar modelo."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "999.999.999.999")

        assert controlador.modelo.ip == "999.999.999.999"
        assert controlador.modelo.ip_valida is False

    def test_cambio_a_ip_invalida_muestra_mensaje(self, controlador, vista, qtbot):
        """Cambio a IP inválida debe mostrar mensaje de error."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "999.999.999.999")

        assert "999" in controlador.modelo.mensaje_error

    def test_validacion_formato_incorrecto(self, controlador, vista, qtbot):
        """IP con formato incorrecto debe marcar como inválida."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "192.168.1")

        assert controlador.modelo.ip_valida is False
        assert "Formato inválido" in controlador.modelo.mensaje_error

    def test_validacion_habilita_boton_con_ip_valida(self, controlador, vista, qtbot):
        """IP válida debe habilitar botón aplicar."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "192.168.1.100")

        assert vista.boton_aplicar.isEnabled()

    def test_validacion_deshabilita_boton_con_ip_invalida(
        self, controlador, vista, qtbot
    ):
        """IP inválida debe deshabilitar botón aplicar."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "999.999.999.999")

        assert not vista.boton_aplicar.isEnabled()


class TestAplicarConfiguracion:
    """Tests de aplicación de configuración."""

    def test_aplicar_con_ip_valida_emite_signal(self, controlador, vista, qtbot):
        """Aplicar con IP válida debe emitir señal ip_cambiada."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "10.0.0.1")

        with qtbot.waitSignal(controlador.ip_cambiada, timeout=1000) as blocker:
            vista.boton_aplicar.click()

        assert blocker.args == ["10.0.0.1"]

    def test_aplicar_con_ip_invalida_no_emite_signal(
        self, controlador, vista, qtbot
    ):
        """Aplicar con IP inválida no debe emitir señal."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "999.999.999.999")

        # El botón está deshabilitado, pero forzamos el click
        vista.boton_aplicar.setEnabled(True)

        # No debe emitir señal
        with qtbot.assertNotEmitted(controlador.ip_cambiada):
            vista.boton_aplicar.click()

    def test_aplicar_actualiza_ip_en_modelo(self, controlador, vista, qtbot):
        """Aplicar debe mantener IP en el modelo."""
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "192.168.100.1")

        vista.boton_aplicar.click()

        assert controlador.modelo.ip == "192.168.100.1"


class TestPropiedades:
    """Tests de propiedades del controlador."""

    def test_property_modelo_retorna_modelo_actual(self, controlador, modelo):
        """Property modelo debe retornar modelo actual."""
        assert controlador.modelo == modelo

    def test_modelo_se_actualiza_con_cambios(self, controlador, vista, qtbot):
        """Modelo debe reflejar cambios en IP."""
        ip_inicial = controlador.modelo.ip

        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "10.10.10.10")

        assert controlador.modelo.ip != ip_inicial
        assert controlador.modelo.ip == "10.10.10.10"


class TestEscenarios:
    """Tests de escenarios completos."""

    def test_flujo_completo_ip_valida(self, controlador, vista, qtbot):
        """Flujo completo: cambiar IP válida y aplicar."""
        # 1. Cambiar IP
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "172.16.0.1")

        # 2. Verificar validación
        assert controlador.modelo.ip_valida is True
        assert vista.boton_aplicar.isEnabled()

        # 3. Aplicar
        with qtbot.waitSignal(controlador.ip_cambiada, timeout=1000) as blocker:
            vista.boton_aplicar.click()

        # 4. Verificar señal
        assert blocker.args == ["172.16.0.1"]

    def test_flujo_completo_ip_invalida(self, controlador, vista, qtbot):
        """Flujo completo: cambiar IP inválida no permite aplicar."""
        # 1. Cambiar IP a inválida
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "256.256.256.256")

        # 2. Verificar validación
        assert controlador.modelo.ip_valida is False
        assert not vista.boton_aplicar.isEnabled()

        # 3. Verificar mensaje de error visible
        assert "256" in vista._label_validacion.text()

    def test_flujo_correccion_ip(self, controlador, vista, qtbot):
        """Flujo: IP inválida → corregir → aplicar."""
        # 1. IP inválida
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "999.1.1.1")
        assert not vista.boton_aplicar.isEnabled()

        # 2. Corregir IP
        vista.input_ip.clear()
        qtbot.keyClicks(vista.input_ip, "192.168.1.1")
        assert vista.boton_aplicar.isEnabled()

        # 3. Aplicar
        with qtbot.waitSignal(controlador.ip_cambiada, timeout=1000) as blocker:
            vista.boton_aplicar.click()

        assert blocker.args == ["192.168.1.1"]
