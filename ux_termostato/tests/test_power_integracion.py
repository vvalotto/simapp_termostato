"""
Tests de integración para el panel Power.

Este módulo contiene tests que validan la integración completa entre
modelo, vista y controlador del panel Power, simulando flujos end-to-end
reales de uso y la comunicación con el Raspberry Pi.
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import QTimer, Qt

from app.presentacion.paneles.power.modelo import PowerModelo
from app.presentacion.paneles.power.vista import PowerVista
from app.presentacion.paneles.power.controlador import PowerControlador


class TestIntegracionMVC:
    """Tests de integración del patrón MVC del panel power."""

    def test_flujo_completo_modelo_vista_controlador(self, qapp):
        """
        Test: Flujo completo modelo → controlador → vista.

        Given: Sistema MVC completo inicializado
        When: Se cambia el estado power varias veces
        Then: Los cambios fluyen correctamente por toda la arquitectura
        """
        # Setup
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Verificar estado inicial (apagado)
        assert controlador.modelo.encendido is False
        assert "ENCENDER" in vista.btn_power.text()

        # Encender
        controlador.cambiar_estado()
        assert controlador.modelo.encendido is True
        assert "APAGAR" in vista.btn_power.text()

        # Apagar nuevamente
        controlador.cambiar_estado()
        assert controlador.modelo.encendido is False
        assert "ENCENDER" in vista.btn_power.text()

    def test_multiples_toggles_consecutivos(self, qapp):
        """
        Test: Múltiples toggles consecutivos sin problemas.

        Given: Sistema MVC inicializado
        When: Se realizan muchos toggles rápidos
        Then: Cada cambio se procesa correctamente sin errores
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Simular 50 toggles rápidos
        for i in range(50):
            controlador.cambiar_estado()
            esperado = (i + 1) % 2 == 1  # Impar = encendido
            assert controlador.modelo.encendido == esperado

    def test_click_boton_fluye_por_arquitectura(self, qapp):
        """
        Test: Click en botón fluye por toda la arquitectura MVC.

        Given: Sistema MVC completo
        When: Usuario hace click en el botón
        Then: Modelo se actualiza, vista se re-renderiza, señales se emiten
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Spy para señales
        spy_power = Mock()
        spy_comando = Mock()
        controlador.power_cambiado.connect(spy_power)
        controlador.comando_enviado.connect(spy_comando)

        # Click en el botón
        vista.btn_power.click()

        # Verificar flujo completo
        assert controlador.modelo.encendido is True  # Modelo actualizado
        assert "APAGAR" in vista.btn_power.text()    # Vista actualizada
        spy_power.assert_called_once_with(True)       # Señal power emitida
        spy_comando.assert_called_once()              # Señal comando emitida


class TestIntegracionComandoJSON:
    """Tests de integración para generación de comandos JSON."""

    def test_comando_json_encender_estructura_completa(self, qapp):
        """
        Test: Comando JSON de encender tiene estructura completa.

        Given: Panel power apagado
        When: Se enciende el termostato
        Then: El comando JSON tiene todos los campos requeridos
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        spy_comando = Mock()
        controlador.comando_enviado.connect(spy_comando)

        # Encender
        controlador.cambiar_estado()

        # Verificar comando JSON
        comando = spy_comando.call_args[0][0]
        assert isinstance(comando, dict)
        assert "comando" in comando
        assert "estado" in comando
        assert comando["comando"] == "power"
        assert comando["estado"] == "on"

    def test_comando_json_apagar_estructura_completa(self, qapp):
        """
        Test: Comando JSON de apagar tiene estructura completa.

        Given: Panel power encendido
        When: Se apaga el termostato
        Then: El comando JSON tiene todos los campos requeridos
        """
        modelo = PowerModelo(encendido=True)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        spy_comando = Mock()
        controlador.comando_enviado.connect(spy_comando)

        # Apagar
        controlador.cambiar_estado()

        # Verificar comando JSON
        comando = spy_comando.call_args[0][0]
        assert comando == {"comando": "power", "estado": "off"}

    def test_secuencia_comandos_json(self, qapp):
        """
        Test: Secuencia de comandos JSON es correcta.

        Given: Panel power inicializado
        When: Se enciende y apaga varias veces
        Then: Los comandos JSON alternan correctamente entre on/off
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        comandos_enviados = []
        controlador.comando_enviado.connect(lambda cmd: comandos_enviados.append(cmd))

        # Toggle 4 veces
        for _ in range(4):
            controlador.cambiar_estado()

        # Verificar secuencia: on, off, on, off
        assert comandos_enviados[0]["estado"] == "on"
        assert comandos_enviados[1]["estado"] == "off"
        assert comandos_enviados[2]["estado"] == "on"
        assert comandos_enviados[3]["estado"] == "off"


class TestIntegracionConOtrosPaneles:
    """Tests de integración simulando interacción con otros paneles."""

    def test_signal_power_cambiado_notifica_otros_paneles(self, qapp):
        """
        Test: La señal power_cambiado puede notificar a otros paneles.

        Given: Panel power y componentes externos simulados
        When: Se cambia el estado del power
        Then: Los componentes externos reciben la notificación
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Simular panel Display
        mock_display = Mock()
        mock_display.set_encendido = Mock()
        controlador.power_cambiado.connect(mock_display.set_encendido)

        # Simular panel Climatizador
        mock_climatizador = Mock()
        mock_climatizador.set_encendido = Mock()
        controlador.power_cambiado.connect(mock_climatizador.set_encendido)

        # Encender
        controlador.cambiar_estado()

        # Verificar que ambos paneles fueron notificados
        mock_display.set_encendido.assert_called_once_with(True)
        mock_climatizador.set_encendido.assert_called_once_with(True)

    def test_comando_json_puede_enviarse_a_cliente(self, qapp):
        """
        Test: El comando JSON puede enviarse a un cliente de red.

        Given: Panel power y cliente de red simulado
        When: Se cambia el estado
        Then: El cliente recibe el comando para enviar al RPi
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Simular cliente de comandos
        mock_cliente = Mock()
        mock_cliente.enviar_comando = Mock()
        controlador.comando_enviado.connect(mock_cliente.enviar_comando)

        # Encender
        controlador.cambiar_estado()

        # Verificar que el cliente recibió el comando
        mock_cliente.enviar_comando.assert_called_once()
        comando = mock_cliente.enviar_comando.call_args[0][0]
        assert comando["comando"] == "power"
        assert comando["estado"] == "on"

    def test_multiples_paneles_responden_simultaneamente(self, qapp):
        """
        Test: Múltiples paneles responden simultáneamente al cambio de power.

        Given: Panel power conectado a 5 componentes externos
        When: Se cambia el estado
        Then: Todos los componentes reciben la notificación
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Simular 5 componentes externos
        componentes = [Mock() for _ in range(5)]
        for comp in componentes:
            comp.on_power_change = Mock()
            controlador.power_cambiado.connect(comp.on_power_change)

        # Encender
        controlador.cambiar_estado()

        # Verificar que todos fueron notificados
        for comp in componentes:
            comp.on_power_change.assert_called_once_with(True)


class TestIntegracionEstadosTransiciones:
    """Tests de integración para transiciones de estado."""

    def test_transicion_apagado_encendido_apagado(self, qapp):
        """
        Test: Transición completa OFF → ON → OFF.

        Given: Panel power apagado
        When: Se enciende y luego se apaga
        Then: Todas las transiciones se manejan correctamente
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Estado inicial
        assert "ENCENDER" in vista.btn_power.text()

        # OFF → ON
        controlador.cambiar_estado()
        assert controlador.modelo.encendido is True
        assert "APAGAR" in vista.btn_power.text()

        # ON → OFF
        controlador.cambiar_estado()
        assert controlador.modelo.encendido is False
        assert "ENCENDER" in vista.btn_power.text()

    def test_actualizacion_modelo_externa_sincroniza_vista(self, qapp):
        """
        Test: Actualización externa del modelo sincroniza la vista.

        Given: Panel power apagado
        When: Se actualiza el modelo externamente (ej: desde servidor)
        Then: La vista se sincroniza correctamente
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Actualización externa (simulando confirmación del RPi)
        controlador.actualizar_modelo(True)

        assert controlador.modelo.encendido is True
        assert "APAGAR" in vista.btn_power.text()

    def test_modelo_inmutable_se_preserva_en_transiciones(self, qapp):
        """
        Test: La inmutabilidad del modelo se preserva durante transiciones.

        Given: Panel power con modelo inicial
        When: Se realizan múltiples cambios de estado
        Then: El modelo original nunca se muta
        """
        modelo_inicial = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo_inicial, vista)

        # Realizar múltiples cambios
        controlador.cambiar_estado()  # ON
        controlador.cambiar_estado()  # OFF
        controlador.actualizar_modelo(True)  # ON

        # El modelo inicial debe permanecer inalterado
        assert modelo_inicial.encendido is False

        # El controlador debe tener un nuevo modelo
        assert controlador.modelo.encendido is True


class TestIntegracionSignals:
    """Tests de integración para señales PyQt."""

    def test_ambas_senales_se_emiten_en_cambiar_estado(self, qapp):
        """
        Test: Ambas señales se emiten al cambiar estado.

        Given: Panel power con listeners en ambas señales
        When: Se cambia el estado
        Then: Ambas señales se emiten correctamente
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        spy_power = Mock()
        spy_comando = Mock()
        controlador.power_cambiado.connect(spy_power)
        controlador.comando_enviado.connect(spy_comando)

        controlador.cambiar_estado()

        spy_power.assert_called_once_with(True)
        spy_comando.assert_called_once()

    def test_actualizar_modelo_solo_emite_power_cambiado(self, qapp):
        """
        Test: actualizar_modelo solo emite power_cambiado (no comando).

        Given: Panel power con listeners
        When: Se llama a actualizar_modelo
        Then: Solo se emite power_cambiado (viene del exterior)
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        spy_power = Mock()
        spy_comando = Mock()
        controlador.power_cambiado.connect(spy_power)
        controlador.comando_enviado.connect(spy_comando)

        controlador.actualizar_modelo(True)

        spy_power.assert_called_once_with(True)
        spy_comando.assert_not_called()  # NO debe emitirse


class TestIntegracionRobustez:
    """Tests de integración para robustez y casos extremos."""

    def test_toggles_rapidos_sin_errores(self, qapp):
        """
        Test: Toggles muy rápidos no causan errores.

        Given: Panel power inicializado
        When: Se realizan 100 toggles consecutivos
        Then: El sistema permanece estable y consistente
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # 100 toggles rápidos
        for _ in range(100):
            controlador.cambiar_estado()

        # Sistema debe estar consistente
        assert controlador.modelo is not None
        assert vista.btn_power is not None

    def test_multiples_conexiones_desconexiones_signals(self, qapp):
        """
        Test: Múltiples conexiones/desconexiones de señales.

        Given: Panel power inicializado
        When: Se conectan y desconectan múltiples listeners
        Then: El sistema maneja correctamente las conexiones
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        controlador = PowerControlador(modelo, vista)

        # Conectar múltiples listeners
        listeners = [Mock() for _ in range(10)]
        for listener in listeners:
            listener.on_change = Mock()
            controlador.power_cambiado.connect(listener.on_change)

        # Emitir señal
        controlador.cambiar_estado()

        # Todos deben haber sido notificados
        for listener in listeners:
            listener.on_change.assert_called_once()

    def test_panel_power_responde_a_clicks_de_usuario_real(self, qapp, qtbot):
        """
        Test: Panel responde a clicks de usuario real simulados con qtbot.

        Given: Panel power completamente configurado
        When: Usuario hace clicks reales en el botón
        Then: El sistema responde correctamente a cada click
        """
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Click 1: Encender
        with qtbot.waitSignal(controlador.power_cambiado, timeout=1000) as blocker:
            qtbot.mouseClick(vista.btn_power, Qt.MouseButton.LeftButton)
        assert blocker.args == [True]
        assert "APAGAR" in vista.btn_power.text()

        # Click 2: Apagar
        with qtbot.waitSignal(controlador.power_cambiado, timeout=1000) as blocker:
            qtbot.mouseClick(vista.btn_power, Qt.MouseButton.LeftButton)
        assert blocker.args == [False]
        assert "ENCENDER" in vista.btn_power.text()


class TestIntegracionFlujoCompleto:
    """Test del flujo completo end-to-end del panel power."""

    def test_flujo_end_to_end_completo(self, qapp, qtbot):
        """
        Test: Flujo end-to-end completo desde UI hasta comando RPi.

        Given: Panel power configurado con todos los componentes
        When: Usuario interactúa con la UI
        Then: El flujo completo funciona: UI → Modelo → Señales → Comando JSON
        """
        # Setup completo
        modelo = PowerModelo(encendido=False)
        vista = PowerVista()
        vista.show()
        controlador = PowerControlador(modelo, vista)

        # Simular componentes externos
        mock_display = Mock()
        mock_cliente = Mock()

        controlador.power_cambiado.connect(lambda enc: mock_display.set_encendido(enc))
        controlador.comando_enviado.connect(lambda cmd: mock_cliente.enviar(cmd))

        # Flujo 1: Usuario hace click para ENCENDER
        qtbot.mouseClick(vista.btn_power, Qt.MouseButton.LeftButton)

        # Verificar flujo completo
        assert controlador.modelo.encendido is True          # 1. Modelo actualizado
        assert "APAGAR" in vista.btn_power.text()            # 2. Vista actualizada
        mock_display.set_encendido.assert_called_with(True)  # 3. Display notificado
        mock_cliente.enviar.assert_called_once()             # 4. Comando enviado
        comando1 = mock_cliente.enviar.call_args[0][0]
        assert comando1 == {"comando": "power", "estado": "on"}

        # Reset mocks
        mock_display.reset_mock()
        mock_cliente.reset_mock()

        # Flujo 2: Usuario hace click para APAGAR
        qtbot.mouseClick(vista.btn_power, Qt.MouseButton.LeftButton)

        # Verificar flujo completo
        assert controlador.modelo.encendido is False          # 1. Modelo actualizado
        assert "ENCENDER" in vista.btn_power.text()           # 2. Vista actualizada
        mock_display.set_encendido.assert_called_with(False)  # 3. Display notificado
        mock_cliente.enviar.assert_called_once()              # 4. Comando enviado
        comando2 = mock_cliente.enviar.call_args[0][0]
        assert comando2 == {"comando": "power", "estado": "off"}
