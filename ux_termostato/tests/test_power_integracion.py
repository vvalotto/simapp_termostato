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


# ========== Tests específicos para US-008: Apagar el termostato ==========


class TestUS008IntegracionDisplay:
    """
    Tests de integración Power + Display para US-008.

    Criterio de aceptación US-008:
    - El display muestra "---" al apagar el termostato
    """

    def test_display_muestra_guiones_al_apagar(self, qapp, display_controlador_custom,
                                               power_controlador_custom):
        """
        Test: Display muestra "---" cuando se apaga el termostato.

        Given: Termostato encendido con temperatura visible
        When: Se presiona el botón APAGAR
        Then: El display muestra "---"
        """
        from app.presentacion.paneles.display.modelo import DisplayModelo

        # Setup: Power encendido
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )

        # Setup: Display mostrando temperatura
        display_ctrl = display_controlador_custom(
            modelo=DisplayModelo(
                temperatura=23.5,
                modo_vista="ambiente",
                encendido=True,
                error_sensor=False
            )
        )

        # Conectar señal: cuando power cambie, actualizar display
        power_ctrl.power_cambiado.connect(display_ctrl.set_encendido)

        # Verificar estado inicial (encendido)
        assert "23.5" in display_ctrl.vista.label_temp.text()

        # WHEN: Apagar el termostato
        power_ctrl.cambiar_estado()

        # THEN: Display debe mostrar "---"
        assert "---" in display_ctrl.vista.label_temp.text()
        assert "APAGADO" in display_ctrl.vista.label_modo.text()

    def test_display_ciclo_completo_encender_apagar(self, qapp, display_controlador_custom,
                                                     power_controlador_custom):
        """
        Test: Ciclo completo encender → apagar → encender del display.

        Given: Sistema inicializado apagado
        When: Se enciende, luego se apaga, luego se enciende nuevamente
        Then: El display responde correctamente en cada transición
        """
        from app.presentacion.paneles.display.modelo import DisplayModelo

        # Setup
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=False)
        )

        display_ctrl = display_controlador_custom(
            modelo=DisplayModelo(
                temperatura=21.0,
                modo_vista="ambiente",
                encendido=False,
                error_sensor=False
            )
        )

        # Conectar señal
        power_ctrl.power_cambiado.connect(display_ctrl.set_encendido)

        # Estado inicial: APAGADO
        assert "---" in display_ctrl.vista.label_temp.text()

        # Transición 1: APAGADO → ENCENDIDO
        power_ctrl.cambiar_estado()
        assert display_ctrl.modelo.encendido is True

        # Transición 2: ENCENDIDO → APAGADO
        power_ctrl.cambiar_estado()
        assert display_ctrl.modelo.encendido is False
        assert "---" in display_ctrl.vista.label_temp.text()

        # Transición 3: APAGADO → ENCENDIDO
        power_ctrl.cambiar_estado()
        assert display_ctrl.modelo.encendido is True


class TestUS008IntegracionClimatizador:
    """
    Tests de integración Power + Climatizador para US-008.

    Criterio de aceptación US-008:
    - El climatizador muestra estado "apagado" (todo gris) al apagar
    """

    def test_climatizador_se_apaga_con_termostato(self, qapp, climatizador_controlador_custom,
                                                    power_controlador_custom):
        """
        Test: Climatizador se apaga cuando se apaga el termostato.

        Given: Termostato encendido con climatizador activo
        When: Se presiona el botón APAGAR
        Then: El climatizador muestra estado "apagado"
        """
        from app.presentacion.paneles.climatizador.modelo import ClimatizadorModelo

        # Setup: Power encendido
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )

        # Setup: Climatizador en modo "calor"
        climatizador_ctrl = climatizador_controlador_custom(
            modelo=ClimatizadorModelo(
                modo="calentando",
                encendido=True
            )
        )

        # Conectar señal
        power_ctrl.power_cambiado.connect(climatizador_ctrl.set_encendido)

        # Verificar estado inicial (calentando activo)
        assert climatizador_ctrl.modelo.encendido is True
        assert climatizador_ctrl.modelo.modo == "calentando"

        # WHEN: Apagar el termostato
        power_ctrl.cambiar_estado()

        # THEN: Climatizador debe estar apagado
        assert climatizador_ctrl.modelo.encendido is False

    def test_climatizador_diferentes_modos_al_apagar(self, qapp, climatizador_controlador_custom,
                                                      power_controlador_custom):
        """
        Test: Climatizador se apaga correctamente desde cualquier modo.

        Given: Termostato encendido en diferentes modos (calor, frío, reposo)
        When: Se apaga el termostato
        Then: El climatizador siempre se apaga correctamente
        """
        from app.presentacion.paneles.climatizador.modelo import ClimatizadorModelo

        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )

        modos_test = ["calentando", "enfriando", "reposo"]

        for modo in modos_test:
            # Setup: Climatizador en modo específico
            climatizador_ctrl = climatizador_controlador_custom(
                modelo=ClimatizadorModelo(
                    modo=modo,
                    encendido=True
                )
            )

            # Conectar señal
            power_ctrl.power_cambiado.connect(climatizador_ctrl.set_encendido)

            # Verificar estado inicial
            assert climatizador_ctrl.modelo.encendido is True
            assert climatizador_ctrl.modelo.modo == modo

            # Apagar
            power_ctrl.cambiar_estado()

            # Verificar que se apagó correctamente
            assert climatizador_ctrl.modelo.encendido is False

            # Re-encender para próximo test
            power_ctrl.cambiar_estado()

    def test_climatizador_ciclo_completo(self, qapp, climatizador_controlador_custom,
                                          power_controlador_custom):
        """
        Test: Ciclo completo encender → apagar → encender del climatizador.

        Given: Sistema inicializado apagado
        When: Se realizan múltiples toggles de power
        Then: El climatizador responde correctamente a cada cambio
        """
        from app.presentacion.paneles.climatizador.modelo import ClimatizadorModelo

        # Setup
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=False)
        )

        climatizador_ctrl = climatizador_controlador_custom(
            modelo=ClimatizadorModelo(
                modo="reposo",
                encendido=False
            )
        )

        # Conectar señal
        power_ctrl.power_cambiado.connect(climatizador_ctrl.set_encendido)

        # Estado inicial: APAGADO
        assert climatizador_ctrl.modelo.encendido is False

        # Transición 1: APAGADO → ENCENDIDO
        power_ctrl.cambiar_estado()
        assert climatizador_ctrl.modelo.encendido is True

        # Transición 2: ENCENDIDO → APAGADO
        power_ctrl.cambiar_estado()
        assert climatizador_ctrl.modelo.encendido is False

        # Transición 3: APAGADO → ENCENDIDO
        power_ctrl.cambiar_estado()
        assert climatizador_ctrl.modelo.encendido is True


class TestUS008IntegracionIndicadores:
    """
    Tests de integración Power + Indicadores para US-008.

    Los indicadores de alerta deben funcionar independientemente del estado power.
    """

    def test_indicadores_independientes_de_power(self, qapp, indicadores_controlador_custom,
                                                   power_controlador_custom):
        """
        Test: Indicadores funcionan independientemente del estado power.

        Given: Termostato apagado
        When: Se activa una alerta (ej: falla de sensor)
        Then: El indicador LED se enciende correctamente
        """
        from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo

        # Setup: Power apagado
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=False)
        )

        # Setup: Indicadores sin alertas
        indicadores_ctrl = indicadores_controlador_custom(
            modelo=IndicadoresModelo(
                falla_sensor=False,
                bateria_baja=False
            )
        )

        # Verificar estado inicial
        assert power_ctrl.modelo.encendido is False
        assert indicadores_ctrl.modelo.falla_sensor is False

        # WHEN: Activar alerta de sensor (incluso con termostato apagado)
        indicadores_ctrl.actualizar_falla_sensor(True)

        # THEN: El LED debe encenderse independientemente del estado power
        assert indicadores_ctrl.modelo.falla_sensor is True

    def test_apagar_no_afecta_alertas_activas(self, qapp, indicadores_controlador_custom,
                                                power_controlador_custom):
        """
        Test: Apagar el termostato no desactiva indicadores de alerta activos.

        Given: Termostato encendido con alerta de batería activa
        When: Se apaga el termostato
        Then: La alerta de batería permanece activa
        """
        from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo

        # Setup: Power encendido
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )

        # Setup: Indicadores con batería baja
        indicadores_ctrl = indicadores_controlador_custom(
            modelo=IndicadoresModelo(
                falla_sensor=False,
                bateria_baja=True
            )
        )

        # Verificar estado inicial
        assert indicadores_ctrl.modelo.bateria_baja is True

        # WHEN: Apagar el termostato
        power_ctrl.cambiar_estado()

        # THEN: La alerta de batería debe permanecer activa
        assert indicadores_ctrl.modelo.bateria_baja is True


class TestUS008ComandoApagar:
    """
    Tests del comando JSON de apagar para US-008.

    Criterio de aceptación US-008:
    - Envía comando {"comando": "power", "estado": "off"}
    """

    def test_comando_apagar_estructura_correcta(self, qapp, qtbot, power_controlador_custom):
        """
        Test: El comando de apagar tiene la estructura JSON correcta.

        Given: Termostato encendido
        When: Se presiona el botón APAGAR
        Then: El comando enviado es {"comando": "power", "estado": "off"}
        """
        # Setup: Power encendido
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )

        # Spy para capturar comando
        comandos_enviados = []
        power_ctrl.comando_enviado.connect(lambda cmd: comandos_enviados.append(cmd))

        # WHEN: Apagar
        power_ctrl.cambiar_estado()

        # THEN: Comando debe ser correcto
        assert len(comandos_enviados) == 1
        comando = comandos_enviados[0]
        assert comando == {"comando": "power", "estado": "off"}

    def test_comando_apagar_inmediato(self, qapp, qtbot, power_controlador_custom):
        """
        Test: El comando de apagar se envía inmediatamente (fire and forget).

        Given: Termostato encendido
        When: Se presiona el botón APAGAR
        Then: El comando se envía sin esperar confirmación
        """
        # Setup
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )

        # Spy
        mock_cliente = Mock()
        mock_cliente.enviar = Mock()
        power_ctrl.comando_enviado.connect(mock_cliente.enviar)

        # WHEN: Click en botón APAGAR
        with qtbot.waitSignal(power_ctrl.comando_enviado, timeout=1000):
            qtbot.mouseClick(power_ctrl.vista.btn_power, Qt.MouseButton.LeftButton)

        # THEN: Cliente debe haber recibido el comando inmediatamente
        mock_cliente.enviar.assert_called_once()
        comando = mock_cliente.enviar.call_args[0][0]
        assert comando["estado"] == "off"


class TestUS008FlujoCompletoApagar:
    """
    Test del flujo completo end-to-end al apagar el termostato (US-008).
    """

    def test_flujo_end_to_end_apagar_todos_paneles(self, qapp, qtbot,
                                                     power_controlador_custom,
                                                     display_controlador_custom,
                                                     climatizador_controlador_custom):
        """
        Test: Flujo end-to-end completo al apagar el termostato.

        Given: Sistema completo encendido (power, display, climatizador)
        When: Usuario hace click en el botón APAGAR
        Then:
          - Power cambia a apagado
          - Display muestra "---"
          - Climatizador muestra estado apagado
          - Comando JSON se envía al RPi
        """
        from app.presentacion.paneles.display.modelo import DisplayModelo
        from app.presentacion.paneles.climatizador.modelo import ClimatizadorModelo

        # Setup: Power encendido
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=True)
        )
        power_ctrl.vista.show()

        # Setup: Display encendido
        display_ctrl = display_controlador_custom(
            modelo=DisplayModelo(
                temperatura=24.0,
                modo_vista="ambiente",
                encendido=True,
                error_sensor=False
            )
        )

        # Setup: Climatizador encendido en modo calor
        climatizador_ctrl = climatizador_controlador_custom(
            modelo=ClimatizadorModelo(
                modo="calentando",
                encendido=True
            )
        )

        # Setup: Cliente de comandos simulado
        mock_cliente = Mock()
        mock_cliente.enviar_comando = Mock()

        # Conectar señales (simulando coordinador)
        power_ctrl.power_cambiado.connect(display_ctrl.set_encendido)
        power_ctrl.power_cambiado.connect(climatizador_ctrl.set_encendido)
        power_ctrl.comando_enviado.connect(mock_cliente.enviar_comando)

        # Verificar estado inicial (ENCENDIDO)
        assert power_ctrl.modelo.encendido is True
        assert display_ctrl.modelo.encendido is True
        assert climatizador_ctrl.modelo.encendido is True
        assert "APAGAR" in power_ctrl.vista.btn_power.text()

        # WHEN: Usuario hace click en el botón APAGAR
        with qtbot.waitSignal(power_ctrl.power_cambiado, timeout=1000) as blocker:
            qtbot.mouseClick(power_ctrl.vista.btn_power, Qt.MouseButton.LeftButton)

        # THEN: Verificar flujo completo

        # 1. Power cambió a apagado
        assert power_ctrl.modelo.encendido is False
        assert blocker.args == [False]
        assert "ENCENDER" in power_ctrl.vista.btn_power.text()

        # 2. Display muestra "---"
        assert display_ctrl.modelo.encendido is False
        assert "---" in display_ctrl.vista.label_temp.text()

        # 3. Climatizador está apagado
        assert climatizador_ctrl.modelo.encendido is False

        # 4. Comando JSON se envió al RPi
        mock_cliente.enviar_comando.assert_called_once()
        comando = mock_cliente.enviar_comando.call_args[0][0]
        assert comando == {"comando": "power", "estado": "off"}

    def test_ciclo_completo_multiples_paneles(self, qapp, qtbot,
                                               power_controlador_custom,
                                               display_controlador_custom,
                                               climatizador_controlador_custom):
        """
        Test: Ciclo completo encender → apagar → encender con múltiples paneles.

        Given: Sistema inicializado apagado
        When: Se enciende, luego se apaga, luego se enciende nuevamente
        Then: Todos los paneles responden correctamente en cada transición
        """
        from app.presentacion.paneles.display.modelo import DisplayModelo
        from app.presentacion.paneles.climatizador.modelo import ClimatizadorModelo

        # Setup todos los paneles (apagados)
        power_ctrl = power_controlador_custom(
            modelo=PowerModelo(encendido=False)
        )
        power_ctrl.vista.show()

        display_ctrl = display_controlador_custom(
            modelo=DisplayModelo(
                temperatura=20.0,
                modo_vista="ambiente",
                encendido=False,
                error_sensor=False
            )
        )

        climatizador_ctrl = climatizador_controlador_custom(
            modelo=ClimatizadorModelo(
                modo="reposo",
                encendido=False
            )
        )

        # Conectar señales
        power_ctrl.power_cambiado.connect(display_ctrl.set_encendido)
        power_ctrl.power_cambiado.connect(climatizador_ctrl.set_encendido)

        # Estado inicial: APAGADO
        assert power_ctrl.modelo.encendido is False
        assert display_ctrl.modelo.encendido is False
        assert climatizador_ctrl.modelo.encendido is False

        # CICLO 1: APAGADO → ENCENDIDO
        qtbot.mouseClick(power_ctrl.vista.btn_power, Qt.MouseButton.LeftButton)
        assert power_ctrl.modelo.encendido is True
        assert display_ctrl.modelo.encendido is True
        assert climatizador_ctrl.modelo.encendido is True

        # CICLO 2: ENCENDIDO → APAGADO (US-008 focus)
        qtbot.mouseClick(power_ctrl.vista.btn_power, Qt.MouseButton.LeftButton)
        assert power_ctrl.modelo.encendido is False
        assert display_ctrl.modelo.encendido is False
        assert climatizador_ctrl.modelo.encendido is False

        # CICLO 3: APAGADO → ENCENDIDO
        qtbot.mouseClick(power_ctrl.vista.btn_power, Qt.MouseButton.LeftButton)
        assert power_ctrl.modelo.encendido is True
        assert display_ctrl.modelo.encendido is True
        assert climatizador_ctrl.modelo.encendido is True
