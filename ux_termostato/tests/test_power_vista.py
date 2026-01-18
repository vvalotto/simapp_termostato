"""
Tests unitarios para PowerVista.

Este módulo contiene los tests que validan el comportamiento de la vista
del panel Power, incluyendo creación, actualización y estilos.
"""

import pytest
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt

from app.presentacion.paneles.power.vista import PowerVista
from app.presentacion.paneles.power.modelo import PowerModelo


class TestCreacion:
    """Tests de creación de la vista PowerVista."""

    def test_crear_vista(self, qapp):
        """
        Test: Crear vista correctamente.

        Given: Aplicación Qt inicializada
        When: Se crea una instancia de PowerVista
        Then: La vista se crea sin errores
        """
        vista = PowerVista()

        assert vista is not None
        assert isinstance(vista, PowerVista)

    def test_boton_existe(self, qapp):
        """
        Test: El botón power existe.

        Given: Se crea una instancia de PowerVista
        When: Se verifica el botón interno
        Then: Existe btn_power
        """
        vista = PowerVista()

        assert hasattr(vista, "btn_power")
        assert isinstance(vista.btn_power, QPushButton)

    def test_boton_texto_inicial(self, qapp):
        """
        Test: El botón tiene texto inicial correcto.

        Given: Se crea una instancia de PowerVista
        When: Se verifica el texto del botón
        Then: El texto es "⚡ ENCENDER"
        """
        vista = PowerVista()

        assert "ENCENDER" in vista.btn_power.text()
        assert "⚡" in vista.btn_power.text()

    def test_boton_cursor_pointer(self, qapp):
        """
        Test: El botón tiene cursor de puntero.

        Given: Se crea una instancia de PowerVista
        When: Se verifica el cursor
        Then: El cursor es PointingHandCursor
        """
        vista = PowerVista()

        assert vista.btn_power.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_boton_tamano_minimo(self, qapp):
        """
        Test: El botón tiene tamaño mínimo configurado.

        Given: Se crea una instancia de PowerVista
        When: Se verifica el tamaño mínimo
        Then: Tiene al menos 200x60px
        """
        vista = PowerVista()

        assert vista.btn_power.minimumWidth() >= 200
        assert vista.btn_power.minimumHeight() >= 60


class TestActualizacion:
    """Tests de actualización de la vista PowerVista."""

    def test_actualizar_a_encendido(self, qapp):
        """
        Test: Actualizar vista a estado encendido.

        Given: Vista creada y modelo encendido=True
        When: Se llama a actualizar(modelo)
        Then: El botón muestra "⚡ APAGAR"
        """
        vista = PowerVista()
        modelo = PowerModelo(encendido=True)

        vista.actualizar(modelo)

        assert "APAGAR" in vista.btn_power.text()
        assert "⚡" in vista.btn_power.text()

    def test_actualizar_a_apagado(self, qapp):
        """
        Test: Actualizar vista a estado apagado.

        Given: Vista creada y modelo encendido=False
        When: Se llama a actualizar(modelo)
        Then: El botón muestra "⚡ ENCENDER"
        """
        vista = PowerVista()
        modelo = PowerModelo(encendido=False)

        vista.actualizar(modelo)

        assert "ENCENDER" in vista.btn_power.text()
        assert "⚡" in vista.btn_power.text()

    def test_actualizar_toggle_encender(self, qapp):
        """
        Test: Toggle de apagado a encendido.

        Given: Vista en estado apagado
        When: Se actualiza a encendido
        Then: El texto cambia de ENCENDER a APAGAR
        """
        vista = PowerVista()

        # Estado inicial: apagado
        modelo_apagado = PowerModelo(encendido=False)
        vista.actualizar(modelo_apagado)
        assert "ENCENDER" in vista.btn_power.text()

        # Actualizar a encendido
        modelo_encendido = PowerModelo(encendido=True)
        vista.actualizar(modelo_encendido)
        assert "APAGAR" in vista.btn_power.text()

    def test_actualizar_toggle_apagar(self, qapp):
        """
        Test: Toggle de encendido a apagado.

        Given: Vista en estado encendido
        When: Se actualiza a apagado
        Then: El texto cambia de APAGAR a ENCENDER
        """
        vista = PowerVista()

        # Estado inicial: encendido
        modelo_encendido = PowerModelo(encendido=True)
        vista.actualizar(modelo_encendido)
        assert "APAGAR" in vista.btn_power.text()

        # Actualizar a apagado
        modelo_apagado = PowerModelo(encendido=False)
        vista.actualizar(modelo_apagado)
        assert "ENCENDER" in vista.btn_power.text()


class TestEstilos:
    """Tests de estilos visuales de PowerVista."""

    def test_estilo_apagado_aplicado(self, qapp):
        """
        Test: El estilo de apagado se aplica.

        Given: Vista actualizada con modelo apagado
        When: Se verifica el stylesheet
        Then: Contiene colores verdes (#16a34a)
        """
        vista = PowerVista()
        modelo = PowerModelo(encendido=False)

        vista.actualizar(modelo)
        stylesheet = vista.btn_power.styleSheet()

        # Verificar que contiene color verde
        assert "#16a34a" in stylesheet or "green" in stylesheet.lower()

    def test_estilo_encendido_aplicado(self, qapp):
        """
        Test: El estilo de encendido se aplica.

        Given: Vista actualizada con modelo encendido
        When: Se verifica el stylesheet
        Then: Contiene colores grises (#475569)
        """
        vista = PowerVista()
        modelo = PowerModelo(encendido=True)

        vista.actualizar(modelo)
        stylesheet = vista.btn_power.styleSheet()

        # Verificar que contiene color gris slate
        assert "#475569" in stylesheet or "slate" in stylesheet.lower()

    def test_estilo_cambia_al_actualizar(self, qapp):
        """
        Test: El estilo cambia al actualizar el modelo.

        Given: Vista con estilo apagado (verde)
        When: Se actualiza a encendido
        Then: El estilo cambia a gris
        """
        vista = PowerVista()

        # Aplicar estilo apagado
        modelo_apagado = PowerModelo(encendido=False)
        vista.actualizar(modelo_apagado)
        stylesheet_apagado = vista.btn_power.styleSheet()

        # Aplicar estilo encendido
        modelo_encendido = PowerModelo(encendido=True)
        vista.actualizar(modelo_encendido)
        stylesheet_encendido = vista.btn_power.styleSheet()

        # Los stylesheets deben ser diferentes
        assert stylesheet_apagado != stylesheet_encendido


class TestInteraccion:
    """Tests de interacción con el botón."""

    def test_boton_es_clickeable(self, qapp):
        """
        Test: El botón es clickeable.

        Given: Vista creada
        When: Se verifica que el botón está habilitado
        Then: El botón está habilitado
        """
        vista = PowerVista()

        assert vista.btn_power.isEnabled()

    def test_boton_emite_signal_clicked(self, qapp, qtbot):
        """
        Test: El botón emite señal clicked al hacer click.

        Given: Vista creada
        When: Se hace click en el botón
        Then: La señal clicked se emite
        """
        vista = PowerVista()

        # Usar qtbot para verificar señales
        with qtbot.waitSignal(vista.btn_power.clicked, timeout=1000):
            vista.btn_power.click()
