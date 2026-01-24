"""
Tests unitarios para SelectorVistaControlador.

Este módulo contiene los tests que validan el comportamiento del controlador
del panel SelectorVista, incluyendo cambios de modo, señales y habilitación.
"""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import Qt

from app.presentacion.paneles.selector_vista.controlador import SelectorVistaControlador
from app.presentacion.paneles.selector_vista.modelo import SelectorVistaModelo
from app.presentacion.paneles.selector_vista.vista import SelectorVistaVista


class TestCreacion:
    """Tests de creación del controlador SelectorVistaControlador."""

    def test_crear_controlador(self, qapp):
        """
        Test: Crear controlador correctamente.

        Given: Modelo y vista creados
        When: Se crea una instancia de SelectorVistaControlador
        Then: Se crea sin errores
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()

        controlador = SelectorVistaControlador(modelo, vista)

        assert controlador is not None
        assert isinstance(controlador, SelectorVistaControlador)

    def test_modelo_asignado(self, qapp):
        """
        Test: El modelo se asigna correctamente.

        Given: Controlador creado con un modelo
        When: Se accede a la propiedad modelo
        Then: Retorna el modelo correcto
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()

        controlador = SelectorVistaControlador(modelo, vista)

        assert controlador.modelo == modelo
        assert controlador.modelo.modo == "ambiente"

    def test_vista_se_inicializa(self, qapp):
        """
        Test: La vista se inicializa con el modelo.

        Given: Controlador creado con modelo modo "deseada"
        When: Se crea el controlador
        Then: La vista muestra el modo deseada checked
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()

        controlador = SelectorVistaControlador(modelo, vista)

        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()


class TestCambioModo:
    """Tests de cambio de modo."""

    def test_cambiar_a_ambiente(self, qapp):
        """
        Test: Cambiar modo a ambiente actualiza modelo.

        Given: Controlador con modo "deseada"
        When: Se llama a _cambiar_modo("ambiente")
        Then: El modelo se actualiza a "ambiente"
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador._cambiar_modo("ambiente")

        assert controlador.modelo.modo == "ambiente"

    def test_cambiar_a_deseada(self, qapp):
        """
        Test: Cambiar modo a deseada actualiza modelo.

        Given: Controlador con modo "ambiente"
        When: Se llama a _cambiar_modo("deseada")
        Then: El modelo se actualiza a "deseada"
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador._cambiar_modo("deseada")

        assert controlador.modelo.modo == "deseada"

    def test_cambiar_modo_actualiza_vista(self, qapp):
        """
        Test: Cambiar modo actualiza la vista.

        Given: Controlador con modo "ambiente"
        When: Se llama a _cambiar_modo("deseada")
        Then: La vista muestra el botón deseada checked
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador._cambiar_modo("deseada")

        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()


class TestHandlers:
    """Tests de handlers de clicks."""

    def test_click_ambiente_desde_deseada(self, qapp):
        """
        Test: Click en ambiente desde deseada cambia el modo.

        Given: Controlador con modo "deseada"
        When: Se ejecuta _on_ambiente_clicked()
        Then: El modo cambia a "ambiente"
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador._on_ambiente_clicked()

        assert controlador.modelo.modo == "ambiente"

    def test_click_ambiente_desde_ambiente_no_cambia(self, qapp):
        """
        Test: Click en ambiente cuando ya está en ambiente no hace nada.

        Given: Controlador con modo "ambiente"
        When: Se ejecuta _on_ambiente_clicked()
        Then: El modo sigue siendo "ambiente"
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        # Mock de _cambiar_modo para verificar que NO se llama
        with patch.object(controlador, "_cambiar_modo") as mock_cambiar:
            controlador._on_ambiente_clicked()
            mock_cambiar.assert_not_called()

    def test_click_deseada_desde_ambiente(self, qapp):
        """
        Test: Click en deseada desde ambiente cambia el modo.

        Given: Controlador con modo "ambiente"
        When: Se ejecuta _on_deseada_clicked()
        Then: El modo cambia a "deseada"
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador._on_deseada_clicked()

        assert controlador.modelo.modo == "deseada"

    def test_click_deseada_desde_deseada_no_cambia(self, qapp):
        """
        Test: Click en deseada cuando ya está en deseada no hace nada.

        Given: Controlador con modo "deseada"
        When: Se ejecuta _on_deseada_clicked()
        Then: El modo sigue siendo "deseada"
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        # Mock de _cambiar_modo para verificar que NO se llama
        with patch.object(controlador, "_cambiar_modo") as mock_cambiar:
            controlador._on_deseada_clicked()
            mock_cambiar.assert_not_called()


class TestHabilitacion:
    """Tests de habilitación/deshabilitación."""

    def test_deshabilitar_actualiza_modelo(self, qapp):
        """
        Test: Deshabilitar actualiza el modelo.

        Given: Controlador habilitado
        When: Se llama a setEnabled(False)
        Then: El modelo se actualiza con habilitado=False
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador.setEnabled(False)

        assert controlador.modelo.habilitado is False

    def test_deshabilitar_actualiza_vista(self, qapp):
        """
        Test: Deshabilitar actualiza la vista.

        Given: Controlador habilitado
        When: Se llama a setEnabled(False)
        Then: Los botones de la vista están deshabilitados
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador.setEnabled(False)

        assert not vista.boton_ambiente.isEnabled()
        assert not vista.boton_deseada.isEnabled()

    def test_habilitar_actualiza_modelo(self, qapp):
        """
        Test: Habilitar actualiza el modelo.

        Given: Controlador deshabilitado
        When: Se llama a setEnabled(True)
        Then: El modelo se actualiza con habilitado=True
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=False)
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador.setEnabled(True)

        assert controlador.modelo.habilitado is True

    def test_habilitar_actualiza_vista(self, qapp):
        """
        Test: Habilitar actualiza la vista.

        Given: Controlador deshabilitado
        When: Se llama a setEnabled(True)
        Then: Los botones de la vista están habilitados
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=False)
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        controlador.setEnabled(True)

        assert vista.boton_ambiente.isEnabled()
        assert vista.boton_deseada.isEnabled()


class TestSignals:
    """Tests de señales PyQt."""

    def test_modo_cambiado_emite_ambiente(self, qapp, qtbot):
        """
        Test: Cambiar a ambiente emite señal modo_cambiado.

        Given: Controlador con modo "deseada"
        When: Se cambia a modo "ambiente"
        Then: Se emite señal modo_cambiado con valor "ambiente"
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            controlador._cambiar_modo("ambiente")

        assert blocker.args == ["ambiente"]

    def test_modo_cambiado_emite_deseada(self, qapp, qtbot):
        """
        Test: Cambiar a deseada emite señal modo_cambiado.

        Given: Controlador con modo "ambiente"
        When: Se cambia a modo "deseada"
        Then: Se emite señal modo_cambiado con valor "deseada"
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            controlador._cambiar_modo("deseada")

        assert blocker.args == ["deseada"]

    def test_click_boton_emite_senal(self, qapp, qtbot):
        """
        Test: Click en botón emite señal.

        Given: Controlador con modo "ambiente"
        When: Se hace click en botón deseada
        Then: Se emite señal modo_cambiado con "deseada"
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)

        assert blocker.args == ["deseada"]


class TestIntegracion:
    """Tests de integración del controlador."""

    def test_flujo_completo_ambiente_a_deseada(self, qapp, qtbot):
        """
        Test: Flujo completo de cambio de ambiente a deseada.

        Given: Controlador iniciado en modo "ambiente"
        When: Usuario hace click en botón deseada
        Then: Modelo se actualiza, vista se actualiza, señal se emite
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        # Verificar estado inicial
        assert controlador.modelo.modo == "ambiente"
        assert vista.boton_ambiente.isChecked()

        # Click en deseada
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)

        # Verificar resultado
        assert blocker.args == ["deseada"]
        assert controlador.modelo.modo == "deseada"
        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()

    def test_flujo_completo_deseada_a_ambiente(self, qapp, qtbot):
        """
        Test: Flujo completo de cambio de deseada a ambiente.

        Given: Controlador iniciado en modo "deseada"
        When: Usuario hace click en botón ambiente
        Then: Modelo se actualiza, vista se actualiza, señal se emite
        """
        modelo = SelectorVistaModelo(modo="deseada")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        # Verificar estado inicial
        assert controlador.modelo.modo == "deseada"
        assert vista.boton_deseada.isChecked()

        # Click en ambiente
        with qtbot.waitSignal(controlador.modo_cambiado, timeout=1000) as blocker:
            qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)

        # Verificar resultado
        assert blocker.args == ["ambiente"]
        assert controlador.modelo.modo == "ambiente"
        assert vista.boton_ambiente.isChecked()
        assert not vista.boton_deseada.isChecked()

    def test_clicks_multiples_solo_cambian_cuando_es_necesario(self, qapp, qtbot):
        """
        Test: Clicks múltiples en el mismo botón no emiten señales redundantes.

        Given: Controlador en modo "ambiente"
        When: Se hacen múltiples clicks en botón ambiente
        Then: No se emiten señales adicionales
        """
        modelo = SelectorVistaModelo(modo="ambiente")
        vista = SelectorVistaVista()
        controlador = SelectorVistaControlador(modelo, vista)

        # Primer click - no debería emitir señal (ya está en ambiente)
        senal_mock = Mock()
        controlador.modo_cambiado.connect(senal_mock)

        qtbot.mouseClick(vista.boton_ambiente, Qt.MouseButton.LeftButton)
        qtbot.wait(100)  # Esperar procesamiento

        # No debería haber emitido señal
        senal_mock.assert_not_called()

        # Segundo click en deseada - SÍ debería emitir
        qtbot.mouseClick(vista.boton_deseada, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        senal_mock.assert_called_once_with("deseada")
