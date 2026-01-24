"""
Tests de integración para el panel SelectorVista.

Este módulo contiene tests que validan la integración completa entre
modelo, vista y controlador del panel SelectorVista, simulando flujos
end-to-end reales de uso.
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import Qt

from app.presentacion.paneles.selector_vista.modelo import SelectorVistaModelo
from app.presentacion.paneles.selector_vista.vista import SelectorVistaVista
from app.presentacion.paneles.selector_vista.controlador import SelectorVistaControlador


class TestIntegracionMVC:
    """Tests de integración del patrón MVC del selector de vista."""

    def test_flujo_completo_modelo_vista_controlador(self, qapp, qtbot):
        """
        Test: Flujo completo modelo → controlador → vista.

        Given: Sistema MVC completo inicializado en modo "ambiente"
        When: Se cambia el modo a "deseada" y luego se deshabilita
        Then: Los cambios fluyen correctamente por toda la arquitectura
        """
        # Setup
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Verificar estado inicial
        assert controlador.modelo.modo == "ambiente"
        assert controlador.modelo.habilitado is True
        assert vista.boton_ambiente.isChecked()
        assert vista.boton_ambiente.isEnabled()

        # Cambiar modo a deseada
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            controlador._cambiar_modo("deseada")

        assert blocker.args == ["deseada"]
        assert controlador.modelo.modo == "deseada"
        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()

        # Deshabilitar
        controlador.setEnabled(False)
        assert not controlador.modelo.habilitado
        assert not vista.boton_ambiente.isEnabled()
        assert not vista.boton_deseada.isEnabled()

        # Habilitar nuevamente
        controlador.setEnabled(True)
        assert controlador.modelo.habilitado
        assert vista.boton_ambiente.isEnabled()
        assert vista.boton_deseada.isEnabled()

    def test_multiples_cambios_consecutivos(self, qapp, qtbot):
        """
        Test: Múltiples cambios de modo consecutivos sin problemas.

        Given: Sistema MVC inicializado
        When: Se realizan muchos cambios de modo alternados
        Then: Cada cambio se procesa correctamente sin errores
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Conectar mock para contar emisiones
        senal_mock = Mock()
        controlador.modo_cambiado.connect(senal_mock)

        # Alternar entre modos 10 veces
        for i in range(10):
            if i % 2 == 0:
                qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
                qtbot.wait(50)
                assert controlador.modelo.modo == "deseada"
            else:
                qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)
                qtbot.wait(50)
                assert controlador.modelo.modo == "ambiente"

        # Verificar que se emitieron 10 señales
        assert senal_mock.call_count == 10

    def test_estados_simultaneos(self, qapp, qtbot):
        """
        Test: Manejo correcto de estados simultáneos.

        Given: Sistema MVC inicializado
        When: Se cambian modo y habilitación simultáneamente
        Then: La vista refleja todos los cambios correctamente
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Deshabilitar mientras está en ambiente
        controlador.setEnabled(False)
        assert controlador.modelo.modo == "ambiente"
        assert not controlador.modelo.habilitado
        assert not vista.boton_ambiente.isEnabled()
        assert vista.boton_ambiente.isChecked()  # Sigue checked aunque deshabilitado

        # Habilitar y cambiar modo en secuencia rápida
        controlador.setEnabled(True)
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000):
            controlador._cambiar_modo("deseada")

        assert controlador.modelo.modo == "deseada"
        assert controlador.modelo.habilitado
        assert vista.boton_deseada.isEnabled()
        assert vista.boton_deseada.isChecked()


class TestIntegracionSignals:
    """Tests de integración de señales PyQt."""

    def test_senal_se_emite_en_contexto_real(self, qapp, qtbot):
        """
        Test: La señal modo_cambiado se emite correctamente en contexto integrado.

        Given: Sistema MVC completo con listener conectado
        When: Usuario hace click en botón
        Then: Señal se emite y listener la recibe
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Conectar listener
        listener = Mock()
        controlador.modo_cambiado.connect(listener)

        # Click en deseada
        qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        listener.assert_called_once_with("deseada")

    def test_multiples_listeners_reciben_senal(self, qapp, qtbot):
        """
        Test: Múltiples listeners conectados reciben la misma señal.

        Given: Sistema MVC con múltiples listeners
        When: Se cambia el modo
        Then: Todos los listeners reciben la señal
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Conectar múltiples listeners
        listener1 = Mock()
        listener2 = Mock()
        listener3 = Mock()
        controlador.modo_cambiado.connect(listener1)
        controlador.modo_cambiado.connect(listener2)
        controlador.modo_cambiado.connect(listener3)

        # Cambiar modo
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000):
            qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)

        # Verificar que todos recibieron
        listener1.assert_called_once_with("deseada")
        listener2.assert_called_once_with("deseada")
        listener3.assert_called_once_with("deseada")


class TestIntegracionUsuario:
    """Tests de integración simulando interacción de usuario real."""

    def test_usuario_alterna_entre_modos(self, qapp, qtbot):
        """
        Test: Usuario alterna entre modos varias veces.

        Given: Panel visible en la UI
        When: Usuario hace clicks alternados en ambos botones
        Then: El sistema responde correctamente en cada cambio
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Mock para rastrear cambios
        cambios = []
        controlador.modo_cambiado.connect(lambda modo: cambios.append(modo))

        # Usuario clicks: ambiente → deseada → ambiente → deseada
        qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # Verificar secuencia
        assert cambios == ["deseada", "ambiente", "deseada"]
        assert controlador.modelo.modo == "deseada"

    def test_usuario_intenta_clicks_redundantes(self, qapp, qtbot):
        """
        Test: Usuario hace clicks redundantes en el mismo botón.

        Given: Panel en modo "ambiente"
        When: Usuario hace múltiples clicks en botón ambiente
        Then: No se generan señales redundantes
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Mock para contar señales
        senal_mock = Mock()
        controlador.modo_cambiado.connect(senal_mock)

        # Usuario hace 5 clicks en ambiente (ya está en ese modo)
        for _ in range(5):
            qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)
            qtbot.wait(50)

        # No debería haber emitido señales
        senal_mock.assert_not_called()

        # Un click en deseada SÍ emite
        qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
        qtbot.wait(50)

        senal_mock.assert_called_once_with("deseada")

    def test_panel_deshabilitado_ignora_clicks(self, qapp, qtbot):
        """
        Test: Panel deshabilitado ignora clicks de usuario.

        Given: Panel deshabilitado
        When: Usuario intenta hacer clicks en botones
        Then: No se producen cambios ni se emiten señales
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=False)
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Verificar que está deshabilitado
        assert not vista.boton_deseada.isEnabled()

        # Mock para verificar señales
        senal_mock = Mock()
        controlador.modo_cambiado.connect(senal_mock)

        # Intentar clicks (deberían ser ignorados por Qt)
        qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # No debería haber emitido señal ni cambiado modo
        senal_mock.assert_not_called()
        assert controlador.modelo.modo == "ambiente"


class TestIntegracionResiliencia:
    """Tests de resiliencia del sistema integrado."""

    def test_sistema_recupera_de_estado_inicial_invalido(self, qapp, qtbot):
        """
        Test: Sistema puede cambiar desde cualquier estado inicial válido.

        Given: Sistema inicializado en modo "deseada"
        When: Se cambia a "ambiente" y se deshabilita/habilita
        Then: Sistema mantiene consistencia en todo momento
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Cambiar a ambiente
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000):
            qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)

        assert controlador.modelo.modo == "ambiente"

        # Deshabilitar
        controlador.setEnabled(False)
        assert not controlador.modelo.habilitado

        # Habilitar y cambiar de nuevo
        controlador.setEnabled(True)
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000):
            qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)

        assert controlador.modelo.modo == "deseada"
        assert controlador.modelo.habilitado

    def test_vista_siempre_consistente_con_modelo(self, qapp, qtbot):
        """
        Test: Vista siempre refleja el estado del modelo.

        Given: Sistema MVC inicializado
        When: Se realizan cambios de estado complejos
        Then: Vista siempre está sincronizada con modelo
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)
        vista = SelectorVistaVista()
        vista.show()
        controlador = SelectorVistaControlador(modelo, vista)

        # Secuencia compleja de cambios
        estados = [
            ("deseada", True),
            ("deseada", False),
            ("ambiente", False),
            ("ambiente", True),
            ("deseada", True),
        ]

        for modo, habilitado in estados:
            # Habilitar temporalmente si es necesario para cambiar modo
            if controlador.modelo.modo != modo:
                controlador.setEnabled(True)  # Asegurar que los botones están habilitados
                if modo == "ambiente":
                    qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)
                else:
                    qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
                qtbot.wait(50)

            # Establecer habilitación final
            controlador.setEnabled(habilitado)

            # Verificar consistencia
            assert controlador.modelo.modo == modo
            assert controlador.modelo.habilitado == habilitado

            if modo == "ambiente":
                assert vista.boton_ambiente.isChecked()
            else:
                assert vista.boton_deseada.isChecked()

            assert vista.boton_ambiente.isEnabled() == habilitado
            assert vista.boton_deseada.isEnabled() == habilitado
