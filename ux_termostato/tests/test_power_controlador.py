"""
Tests unitarios para PowerControlador.

Este módulo contiene los tests que validan el comportamiento del controlador
del panel Power, incluyendo métodos, señales y generación de comandos JSON.
"""

import pytest
from PyQt6.QtCore import QObject

from app.presentacion.paneles.power.modelo import PowerModelo
from app.presentacion.paneles.power.vista import PowerVista
from app.presentacion.paneles.power.controlador import PowerControlador


class TestCreacion:
    """Tests de creación del controlador PowerControlador."""

    def test_crear_controlador(self, qapp):
        """
        Test: Crear controlador sin errores.

        Given: Modelo y vista válidos
        When: Se crea una instancia de PowerControlador
        Then: El controlador se crea correctamente
        """
        modelo = PowerModelo()
        vista = PowerVista()

        controlador = PowerControlador(modelo, vista)

        assert controlador is not None
        assert isinstance(controlador, QObject)

    def test_modelo_inicial(self, qapp):
        """
        Test: El modelo inicial se almacena correctamente.

        Given: Modelo con encendido=False
        When: Se crea el controlador
        Then: El controlador retorna el modelo correcto
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()

        controlador = PowerControlador(modelo, vista)

        assert controlador.modelo == modelo
        assert controlador.modelo.encendido is False

    def test_vista_asociada(self, qapp):
        """
        Test: La vista se asocia correctamente.

        Given: Vista creada
        When: Se crea el controlador
        Then: El controlador retorna la vista correcta
        """
        modelo = PowerModelo()
        vista = PowerVista()

        controlador = PowerControlador(modelo, vista)

        assert controlador.vista == vista

    def test_vista_se_actualiza_en_init(self, qapp):
        """
        Test: La vista se actualiza al crear el controlador.

        Given: Modelo con encendido=True
        When: Se crea el controlador
        Then: La vista refleja el estado inicial
        """
        modelo = PowerModelo(encendido=True)
        vista = PowerVista()

        controlador = PowerControlador(modelo, vista)

        # La vista debe mostrar "APAGAR" porque está encendido
        assert "APAGAR" in vista.btn_power.text()


class TestMetodos:
    """Tests de métodos del controlador."""

    def test_cambiar_estado_de_apagado_a_encendido(self, qapp):
        """
        Test: Cambiar estado de apagado a encendido.

        Given: Controlador con estado apagado
        When: Se llama a cambiar_estado()
        Then: El modelo cambia a encendido=True
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        controlador.cambiar_estado()

        assert controlador.modelo.encendido is True

    def test_cambiar_estado_de_encendido_a_apagado(self, qapp):
        """
        Test: Cambiar estado de encendido a apagado.

        Given: Controlador con estado encendido
        When: Se llama a cambiar_estado()
        Then: El modelo cambia a encendido=False
        """
        modelo = PowerModelo(encendido=True)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        controlador.cambiar_estado()

        assert controlador.modelo.encendido is False

    def test_cambiar_estado_actualiza_vista(self, qapp):
        """
        Test: Cambiar estado actualiza la vista.

        Given: Controlador con estado apagado
        When: Se llama a cambiar_estado()
        Then: La vista muestra "APAGAR"
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        controlador.cambiar_estado()

        assert "APAGAR" in vista.btn_power.text()

    def test_actualizar_modelo_a_encendido(self, qapp):
        """
        Test: Actualizar modelo externamente a encendido.

        Given: Controlador con estado apagado
        When: Se llama a actualizar_modelo(True)
        Then: El modelo cambia a encendido=True
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        controlador.actualizar_modelo(True)

        assert controlador.modelo.encendido is True

    def test_actualizar_modelo_a_apagado(self, qapp):
        """
        Test: Actualizar modelo externamente a apagado.

        Given: Controlador con estado encendido
        When: Se llama a actualizar_modelo(False)
        Then: El modelo cambia a encendido=False
        """
        modelo = PowerModelo(encendido=True)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        controlador.actualizar_modelo(False)

        assert controlador.modelo.encendido is False

    def test_actualizar_modelo_actualiza_vista(self, qapp):
        """
        Test: actualizar_modelo actualiza la vista.

        Given: Controlador con estado apagado
        When: Se llama a actualizar_modelo(True)
        Then: La vista muestra "APAGAR"
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        controlador.actualizar_modelo(True)

        assert "APAGAR" in vista.btn_power.text()


class TestSignals:
    """Tests de señales PyQt del controlador."""

    def test_signal_power_cambiado_existe(self, qapp):
        """
        Test: La señal power_cambiado existe.

        Given: Controlador creado
        When: Se verifica el atributo
        Then: La señal power_cambiado existe
        """
        modelo = PowerModelo()
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        assert hasattr(controlador, "power_cambiado")

    def test_signal_comando_enviado_existe(self, qapp):
        """
        Test: La señal comando_enviado existe.

        Given: Controlador creado
        When: Se verifica el atributo
        Then: La señal comando_enviado existe
        """
        modelo = PowerModelo()
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        assert hasattr(controlador, "comando_enviado")

    def test_cambiar_estado_emite_power_cambiado(self, qapp, qtbot):
        """
        Test: cambiar_estado emite señal power_cambiado.

        Given: Controlador con estado apagado
        When: Se llama a cambiar_estado()
        Then: La señal power_cambiado se emite con True
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        with qtbot.waitSignal(controlador.power_cambiado, timeout=1000) as blocker:
            controlador.cambiar_estado()

        # Verificar que la señal se emitió con el valor correcto
        assert blocker.args == [True]

    def test_cambiar_estado_emite_comando_enviado(self, qapp, qtbot):
        """
        Test: cambiar_estado emite señal comando_enviado.

        Given: Controlador con estado apagado
        When: Se llama a cambiar_estado()
        Then: La señal comando_enviado se emite con comando JSON
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        with qtbot.waitSignal(controlador.comando_enviado, timeout=1000) as blocker:
            controlador.cambiar_estado()

        # Verificar que la señal se emitió con un dict
        assert isinstance(blocker.args[0], dict)

    def test_actualizar_modelo_emite_power_cambiado(self, qapp, qtbot):
        """
        Test: actualizar_modelo emite señal power_cambiado.

        Given: Controlador con estado apagado
        When: Se llama a actualizar_modelo(True)
        Then: La señal power_cambiado se emite con True
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        with qtbot.waitSignal(controlador.power_cambiado, timeout=1000) as blocker:
            controlador.actualizar_modelo(True)

        assert blocker.args == [True]

    def test_actualizar_modelo_no_emite_comando_enviado(self, qapp, qtbot):
        """
        Test: actualizar_modelo NO emite comando_enviado.

        Given: Controlador con estado apagado
        When: Se llama a actualizar_modelo(True)
        Then: La señal comando_enviado NO se emite (viene del exterior)
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Conectar un spy para contar emisiones
        signal_emitted = []
        controlador.comando_enviado.connect(lambda cmd: signal_emitted.append(cmd))

        controlador.actualizar_modelo(True)

        # No debe haberse emitido comando_enviado
        assert len(signal_emitted) == 0


class TestComandoJSON:
    """Tests de generación de comandos JSON."""

    def test_generar_comando_encender(self, qapp, qtbot):
        """
        Test: Generar comando JSON para encender.

        Given: Controlador con estado apagado
        When: Se llama a cambiar_estado()
        Then: El comando JSON es {"comando": "power", "estado": "on"}
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        with qtbot.waitSignal(controlador.comando_enviado, timeout=1000) as blocker:
            controlador.cambiar_estado()

        comando = blocker.args[0]
        assert comando == {"comando": "power", "estado": "on"}

    def test_generar_comando_apagar(self, qapp, qtbot):
        """
        Test: Generar comando JSON para apagar.

        Given: Controlador con estado encendido
        When: Se llama a cambiar_estado()
        Then: El comando JSON es {"comando": "power", "estado": "off"}
        """
        modelo = PowerModelo(encendido=True)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        with qtbot.waitSignal(controlador.comando_enviado, timeout=1000) as blocker:
            controlador.cambiar_estado()

        comando = blocker.args[0]
        assert comando == {"comando": "power", "estado": "off"}

    def test_comando_tiene_estructura_correcta(self, qapp, qtbot):
        """
        Test: El comando JSON tiene la estructura correcta.

        Given: Controlador creado
        When: Se llama a cambiar_estado()
        Then: El comando tiene claves "comando" y "estado"
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        with qtbot.waitSignal(controlador.comando_enviado, timeout=1000) as blocker:
            controlador.cambiar_estado()

        comando = blocker.args[0]
        assert "comando" in comando
        assert "estado" in comando
        assert comando["comando"] == "power"
        assert comando["estado"] in ("on", "off")


class TestIntegracionBoton:
    """Tests de integración entre botón y controlador."""

    def test_click_boton_cambia_estado(self, qapp, qtbot):
        """
        Test: Click en el botón cambia el estado.

        Given: Controlador con estado apagado
        When: Se hace click en el botón
        Then: El estado cambia a encendido
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Click en el botón
        vista.btn_power.click()

        # El modelo debe haber cambiado
        assert controlador.modelo.encendido is True

    def test_click_boton_emite_senales(self, qapp, qtbot):
        """
        Test: Click en el botón emite todas las señales.

        Given: Controlador con estado apagado
        When: Se hace click en el botón
        Then: Se emiten power_cambiado y comando_enviado
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Esperar ambas señales
        with qtbot.waitSignal(controlador.power_cambiado, timeout=1000):
            with qtbot.waitSignal(controlador.comando_enviado, timeout=1000):
                vista.btn_power.click()

    def test_doble_click_toggle_correcto(self, qapp):
        """
        Test: Doble click hace toggle correcto.

        Given: Controlador con estado apagado
        When: Se hace click dos veces
        Then: El estado vuelve a apagado
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Primer click: apagado -> encendido
        vista.btn_power.click()
        assert controlador.modelo.encendido is True

        # Segundo click: encendido -> apagado
        vista.btn_power.click()
        assert controlador.modelo.encendido is False
