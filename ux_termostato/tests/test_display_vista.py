"""
Tests unitarios para DisplayVista.

Este módulo contiene los tests que validan el comportamiento de la vista
del panel Display LCD, incluyendo creación, actualización y estilos.
"""

import pytest
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.modelo import DisplayModelo


class TestCreacion:
    """Tests de creación de la vista DisplayVista."""

    def test_crear_vista(self, qapp):
        """
        Test: Crear vista correctamente.

        Given: Aplicación Qt inicializada
        When: Se crea una instancia de DisplayVista
        Then: La vista se crea sin errores
        """
        vista = DisplayVista()

        assert vista is not None
        assert isinstance(vista, DisplayVista)

    def test_widgets_existen(self, qapp):
        """
        Test: Todos los widgets necesarios existen.

        Given: Se crea una instancia de DisplayVista
        When: Se verifican los widgets internos
        Then: Existen label_modo, label_temp, label_unidad, label_error
        """
        vista = DisplayVista()

        assert hasattr(vista, "label_modo")
        assert hasattr(vista, "label_temp")
        assert hasattr(vista, "label_unidad")
        assert hasattr(vista, "label_error")

    def test_widgets_son_qlabels(self, qapp):
        """
        Test: Los widgets son instancias de QLabel.

        Given: Se crea una instancia de DisplayVista
        When: Se verifican los tipos de widgets
        Then: Todos son QLabel
        """
        vista = DisplayVista()

        assert isinstance(vista.label_modo, QLabel)
        assert isinstance(vista.label_temp, QLabel)
        assert isinstance(vista.label_unidad, QLabel)
        assert isinstance(vista.label_error, QLabel)

    def test_label_error_oculto_inicialmente(self, qapp):
        """
        Test: El label de error está oculto al inicio.

        Given: Se crea una instancia de DisplayVista
        When: Se verifica el estado inicial
        Then: label_error no es visible
        """
        vista = DisplayVista()

        assert not vista.label_error.isVisible()


class TestActualizacion:
    """Tests de actualización de la vista DisplayVista."""

    def test_actualizar_con_temperatura_normal(self, qapp):
        """
        Test: Actualizar vista con temperatura normal.

        Given: Vista creada y modelo con temperatura 22.5°C
        When: Se llama a actualizar(modelo)
        Then: El label_temp muestra "22.5" con un decimal
        """
        vista = DisplayVista()
        vista.show()  # Mostrar vista para que isVisible() funcione
        modelo = DisplayModelo(temperatura=22.5, encendido=True, error_sensor=False)

        vista.actualizar(modelo)

        assert vista.label_temp.text() == "22.5"
        assert vista.label_temp.isVisible()
        assert vista.label_unidad.isVisible()
        assert not vista.label_error.isVisible()

    def test_actualizar_con_temperatura_cero(self, qapp):
        """
        Test: Actualizar vista con temperatura 0.0°C.

        Given: Vista creada y modelo con temperatura 0.0°C
        When: Se llama a actualizar(modelo)
        Then: El label_temp muestra "0.0"
        """
        vista = DisplayVista()
        modelo = DisplayModelo(temperatura=0.0, encendido=True, error_sensor=False)

        vista.actualizar(modelo)

        assert vista.label_temp.text() == "0.0"

    def test_actualizar_con_temperatura_negativa(self, qapp):
        """
        Test: Actualizar vista con temperatura negativa.

        Given: Vista creada y modelo con temperatura -5.0°C
        When: Se llama a actualizar(modelo)
        Then: El label_temp muestra "-5.0"
        """
        vista = DisplayVista()
        modelo = DisplayModelo(temperatura=-5.0, encendido=True, error_sensor=False)

        vista.actualizar(modelo)

        assert vista.label_temp.text() == "-5.0"

    def test_actualizar_con_error_sensor(self, qapp):
        """
        Test: Actualizar vista cuando hay error de sensor.

        Given: Vista creada y modelo con error_sensor=True
        When: Se llama a actualizar(modelo)
        Then: Se ocultan temp/unidad y se muestra label_error
        """
        vista = DisplayVista()
        vista.show()  # Mostrar vista para que isVisible() funcione
        modelo = DisplayModelo(temperatura=22.0, encendido=True, error_sensor=True)

        vista.actualizar(modelo)

        assert not vista.label_temp.isVisible()
        assert not vista.label_unidad.isVisible()
        assert vista.label_error.isVisible()
        assert vista.label_modo.text() == "ERROR DE SENSOR"

    def test_actualizar_cuando_apagado(self, qapp):
        """
        Test: Actualizar vista cuando el termostato está apagado.

        Given: Vista creada y modelo con encendido=False
        When: Se llama a actualizar(modelo)
        Then: El label_temp muestra "---" y label_error está oculto
        """
        vista = DisplayVista()
        vista.show()  # Mostrar vista para que isVisible() funcione
        modelo = DisplayModelo(temperatura=22.0, encendido=False, error_sensor=False)

        vista.actualizar(modelo)

        assert vista.label_temp.text() == "---"
        assert vista.label_temp.isVisible()
        assert vista.label_unidad.isVisible()
        assert not vista.label_error.isVisible()
        assert vista.label_modo.text() == "APAGADO"

    def test_cambio_de_modo_ambiente(self, qapp):
        """
        Test: Cambio de modo a "ambiente".

        Given: Vista creada y modelo con modo_vista="ambiente"
        When: Se llama a actualizar(modelo)
        Then: El label_modo muestra "Temperatura Ambiente"
        """
        vista = DisplayVista()
        modelo = DisplayModelo(temperatura=22.0, modo_vista="ambiente", encendido=True)

        vista.actualizar(modelo)

        assert vista.label_modo.text() == "Temperatura Ambiente"

    def test_cambio_de_modo_deseada(self, qapp):
        """
        Test: Cambio de modo a "deseada".

        Given: Vista creada y modelo con modo_vista="deseada"
        When: Se llama a actualizar(modelo)
        Then: El label_modo muestra "Temperatura Deseada"
        """
        vista = DisplayVista()
        modelo = DisplayModelo(temperatura=24.0, modo_vista="deseada", encendido=True)

        vista.actualizar(modelo)

        assert vista.label_modo.text() == "Temperatura Deseada"

    def test_formato_un_decimal(self, qapp):
        """
        Test: La temperatura se muestra con exactamente un decimal.

        Given: Vista creada y modelo con temperatura 22.567°C
        When: Se llama a actualizar(modelo)
        Then: El label_temp muestra "22.6" (redondeado a 1 decimal)
        """
        vista = DisplayVista()
        modelo = DisplayModelo(temperatura=22.567, encendido=True)

        vista.actualizar(modelo)

        assert vista.label_temp.text() == "22.6"

    def test_multiples_actualizaciones(self, qapp):
        """
        Test: Múltiples actualizaciones consecutivas.

        Given: Vista creada
        When: Se llama a actualizar() varias veces con diferentes modelos
        Then: La vista refleja correctamente cada cambio
        """
        vista = DisplayVista()

        # Primera actualización
        modelo1 = DisplayModelo(temperatura=20.0, encendido=True)
        vista.actualizar(modelo1)
        assert vista.label_temp.text() == "20.0"

        # Segunda actualización
        modelo2 = DisplayModelo(temperatura=25.5, encendido=True)
        vista.actualizar(modelo2)
        assert vista.label_temp.text() == "25.5"

        # Tercera actualización (apagado)
        modelo3 = DisplayModelo(temperatura=25.5, encendido=False)
        vista.actualizar(modelo3)
        assert vista.label_temp.text() == "---"


class TestEstilos:
    """Tests de estilos de la vista DisplayVista."""

    def test_fuente_grande(self, qapp):
        """
        Test: La fuente del label_temp es grande (≥48px).

        Given: Vista creada
        When: Se verifica el tamaño de fuente del label_temp
        Then: El pointSize es ≥ 48
        """
        vista = DisplayVista()
        font = vista.label_temp.font()

        # US-001 requiere fuente ≥48px
        assert font.pointSize() >= 48

    def test_fuente_temperatura_es_bold(self, qapp):
        """
        Test: La fuente del label_temp es negrita.

        Given: Vista creada
        When: Se verifica el estilo de fuente del label_temp
        Then: La fuente es bold
        """
        vista = DisplayVista()
        font = vista.label_temp.font()

        assert font.bold()

    def test_fondo_verde_lcd(self, qapp):
        """
        Test: El display tiene estilo de fondo verde (LCD).

        Given: Vista creada
        When: Se verifica el stylesheet
        Then: Contiene configuración de color verde (#065f46)
        """
        vista = DisplayVista()
        stylesheet = vista.styleSheet()

        # Verificar que hay estilos aplicados
        assert stylesheet != ""
        # Verificar que contiene el color verde característico del LCD
        assert "#065f46" in stylesheet or "#064e3b" in stylesheet

    def test_alineacion_centrada(self, qapp):
        """
        Test: Los labels están centrados.

        Given: Vista creada
        When: Se verifica la alineación de los labels
        Then: Todos están centrados
        """
        vista = DisplayVista()

        assert vista.label_modo.alignment() == Qt.AlignmentFlag.AlignCenter
        assert vista.label_temp.alignment() == Qt.AlignmentFlag.AlignCenter
        assert vista.label_unidad.alignment() == Qt.AlignmentFlag.AlignCenter
        assert vista.label_error.alignment() == Qt.AlignmentFlag.AlignCenter

    def test_object_names_asignados(self, qapp):
        """
        Test: Los widgets tienen objectName asignado (para CSS).

        Given: Vista creada
        When: Se verifican los objectNames
        Then: Están correctamente asignados para aplicar estilos CSS
        """
        vista = DisplayVista()

        assert vista.objectName() == "displayLCD"
        assert vista.label_modo.objectName() == "labelModo"
        assert vista.label_temp.objectName() == "labelTemp"
        assert vista.label_unidad.objectName() == "labelUnidad"
        assert vista.label_error.objectName() == "labelError"


class TestIntegracionVisual:
    """Tests de integración visual de la vista DisplayVista."""

    def test_transicion_normal_a_error(self, qapp):
        """
        Test: Transición de estado normal a error.

        Given: Vista mostrando temperatura normal
        When: Se actualiza con error_sensor=True
        Then: La vista cambia correctamente a estado de error
        """
        vista = DisplayVista()
        vista.show()  # Mostrar vista para que isVisible() funcione

        # Estado inicial normal
        modelo_normal = DisplayModelo(temperatura=22.0, encendido=True, error_sensor=False)
        vista.actualizar(modelo_normal)
        assert vista.label_temp.isVisible()
        assert not vista.label_error.isVisible()

        # Cambio a error
        modelo_error = DisplayModelo(temperatura=22.0, encendido=True, error_sensor=True)
        vista.actualizar(modelo_error)
        assert not vista.label_temp.isVisible()
        assert vista.label_error.isVisible()

    def test_transicion_encendido_a_apagado(self, qapp):
        """
        Test: Transición de encendido a apagado.

        Given: Vista mostrando temperatura con termostato encendido
        When: Se actualiza con encendido=False
        Then: La vista muestra "---"
        """
        vista = DisplayVista()

        # Estado inicial encendido
        modelo_on = DisplayModelo(temperatura=22.0, encendido=True)
        vista.actualizar(modelo_on)
        assert vista.label_temp.text() == "22.0"

        # Cambio a apagado
        modelo_off = DisplayModelo(temperatura=22.0, encendido=False)
        vista.actualizar(modelo_off)
        assert vista.label_temp.text() == "---"
        assert vista.label_modo.text() == "APAGADO"
