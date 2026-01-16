"""
Tests unitarios para DisplayControlador.

Este módulo contiene los tests que validan el comportamiento del controlador
del panel Display LCD, incluyendo coordinación modelo-vista y señales PyQt.
"""

import pytest
from unittest.mock import Mock, call
from dataclasses import replace

from app.presentacion.paneles.display.modelo import DisplayModelo
from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.controlador import DisplayControlador


class TestCreacion:
    """Tests de creación del controlador DisplayControlador."""

    def test_crear_controlador(self, qapp):
        """
        Test: Crear controlador correctamente.

        Given: Modelo y vista inicializados
        When: Se crea una instancia de DisplayControlador
        Then: El controlador se crea sin errores
        """
        modelo = DisplayModelo(temperatura=22.0)
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        assert controlador is not None
        assert isinstance(controlador, DisplayControlador)

    def test_modelo_inicial(self, qapp):
        """
        Test: El controlador guarda referencia al modelo inicial.

        Given: Se crea controlador con modelo inicial
        When: Se accede a la propiedad modelo
        Then: Retorna el modelo correcto
        """
        modelo = DisplayModelo(temperatura=22.0, modo_vista="ambiente")
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        assert controlador.modelo == modelo
        assert controlador.modelo.temperatura == 22.0
        assert controlador.modelo.modo_vista == "ambiente"

    def test_vista_asociada(self, qapp):
        """
        Test: El controlador guarda referencia a la vista.

        Given: Se crea controlador con vista
        When: Se accede a la propiedad vista
        Then: Retorna la vista correcta
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        assert controlador.vista == vista
        assert controlador.vista is vista

    def test_vista_se_actualiza_al_crear(self, qapp):
        """
        Test: La vista se actualiza con el modelo inicial al crear el controlador.

        Given: Modelo con temperatura 25.0°C
        When: Se crea el controlador
        Then: La vista muestra la temperatura inicial
        """
        modelo = DisplayModelo(temperatura=25.0, encendido=True)
        vista = DisplayVista()
        vista.show()

        controlador = DisplayControlador(modelo, vista)

        assert vista.label_temp.text() == "25.0"


class TestActualizarTemperatura:
    """Tests del método actualizar_temperatura."""

    def test_actualizar_temperatura(self, qapp):
        """
        Test: Actualizar temperatura correctamente.

        Given: Controlador inicializado
        When: Se llama a actualizar_temperatura(23.5)
        Then: El modelo se actualiza y la vista se renderiza
        """
        modelo = DisplayModelo(temperatura=20.0)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.actualizar_temperatura(23.5)

        assert controlador.modelo.temperatura == 23.5
        assert vista.label_temp.text() == "23.5"

    def test_actualizar_temperatura_negativa(self, qapp):
        """
        Test: Actualizar temperatura con valor negativo.

        Given: Controlador inicializado
        When: Se llama a actualizar_temperatura(-5.0)
        Then: El modelo acepta el valor negativo
        """
        modelo = DisplayModelo(temperatura=20.0)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.actualizar_temperatura(-5.0)

        assert controlador.modelo.temperatura == -5.0
        assert vista.label_temp.text() == "-5.0"

    def test_actualizar_temperatura_emite_signal(self, qapp):
        """
        Test: actualizar_temperatura emite señal temperatura_actualizada.

        Given: Controlador inicializado con spy en la señal
        When: Se llama a actualizar_temperatura(24.0)
        Then: Se emite la señal con el valor correcto
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        # Spy para capturar emisión de señal
        signal_spy = Mock()
        controlador.temperatura_actualizada.connect(signal_spy)

        controlador.actualizar_temperatura(24.0)

        signal_spy.assert_called_once_with(24.0)

    def test_multiples_actualizaciones_temperatura(self, qapp):
        """
        Test: Múltiples actualizaciones consecutivas.

        Given: Controlador inicializado
        When: Se llama a actualizar_temperatura varias veces
        Then: Cada actualización se refleja correctamente
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.actualizar_temperatura(20.0)
        assert controlador.modelo.temperatura == 20.0
        assert vista.label_temp.text() == "20.0"

        controlador.actualizar_temperatura(25.5)
        assert controlador.modelo.temperatura == 25.5
        assert vista.label_temp.text() == "25.5"

        controlador.actualizar_temperatura(30.0)
        assert controlador.modelo.temperatura == 30.0
        assert vista.label_temp.text() == "30.0"


class TestCambiarModoVista:
    """Tests del método cambiar_modo_vista."""

    def test_cambiar_modo_vista_a_deseada(self, qapp):
        """
        Test: Cambiar modo vista a "deseada".

        Given: Controlador con modo "ambiente"
        When: Se llama a cambiar_modo_vista("deseada")
        Then: El modelo se actualiza y la vista muestra el nuevo modo
        """
        modelo = DisplayModelo(temperatura=22.0, modo_vista="ambiente")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.cambiar_modo_vista("deseada")

        assert controlador.modelo.modo_vista == "deseada"
        assert vista.label_modo.text() == "Temperatura Deseada"

    def test_cambiar_modo_vista_a_ambiente(self, qapp):
        """
        Test: Cambiar modo vista a "ambiente".

        Given: Controlador con modo "deseada"
        When: Se llama a cambiar_modo_vista("ambiente")
        Then: El modelo se actualiza y la vista muestra el nuevo modo
        """
        modelo = DisplayModelo(temperatura=22.0, modo_vista="deseada")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.cambiar_modo_vista("ambiente")

        assert controlador.modelo.modo_vista == "ambiente"
        assert vista.label_modo.text() == "Temperatura Ambiente"

    def test_cambiar_modo_vista_invalido_lanza_error(self, qapp):
        """
        Test: Cambiar modo vista con valor inválido lanza ValueError.

        Given: Controlador inicializado
        When: Se llama a cambiar_modo_vista("invalido")
        Then: Se lanza ValueError
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        with pytest.raises(ValueError) as exc_info:
            controlador.cambiar_modo_vista("invalido")

        assert "Modo inválido" in str(exc_info.value)
        assert "invalido" in str(exc_info.value)

    def test_cambiar_modo_vista_emite_signal(self, qapp):
        """
        Test: cambiar_modo_vista emite señal modo_vista_cambiado.

        Given: Controlador inicializado con spy en la señal
        When: Se llama a cambiar_modo_vista("deseada")
        Then: Se emite la señal con el valor correcto
        """
        modelo = DisplayModelo(modo_vista="ambiente")
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        signal_spy = Mock()
        controlador.modo_vista_cambiado.connect(signal_spy)

        controlador.cambiar_modo_vista("deseada")

        signal_spy.assert_called_once_with("deseada")


class TestSetEncendido:
    """Tests del método set_encendido."""

    def test_set_encendido_true(self, qapp):
        """
        Test: Encender el termostato.

        Given: Controlador con encendido=False
        When: Se llama a set_encendido(True)
        Then: El modelo se actualiza y la vista muestra temperatura
        """
        modelo = DisplayModelo(temperatura=22.0, encendido=False)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.set_encendido(True)

        assert controlador.modelo.encendido is True
        assert vista.label_temp.text() == "22.0"
        assert vista.label_modo.text() == "Temperatura Ambiente"

    def test_set_encendido_false(self, qapp):
        """
        Test: Apagar el termostato.

        Given: Controlador con encendido=True
        When: Se llama a set_encendido(False)
        Then: El modelo se actualiza y la vista muestra "---"
        """
        modelo = DisplayModelo(temperatura=22.0, encendido=True)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.set_encendido(False)

        assert controlador.modelo.encendido is False
        assert vista.label_temp.text() == "---"
        assert vista.label_modo.text() == "APAGADO"


class TestSetErrorSensor:
    """Tests del método set_error_sensor."""

    def test_set_error_sensor_true(self, qapp):
        """
        Test: Establecer error de sensor.

        Given: Controlador sin error
        When: Se llama a set_error_sensor(True)
        Then: El modelo se actualiza y la vista muestra error
        """
        modelo = DisplayModelo(temperatura=22.0, error_sensor=False)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.set_error_sensor(True)

        assert controlador.modelo.error_sensor is True
        assert not vista.label_temp.isVisible()
        assert vista.label_error.isVisible()

    def test_set_error_sensor_false(self, qapp):
        """
        Test: Limpiar error de sensor.

        Given: Controlador con error
        When: Se llama a set_error_sensor(False)
        Then: El modelo se actualiza y la vista muestra temperatura normal
        """
        modelo = DisplayModelo(temperatura=22.0, error_sensor=True)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        controlador.set_error_sensor(False)

        assert controlador.modelo.error_sensor is False
        assert vista.label_temp.isVisible()
        assert not vista.label_error.isVisible()


class TestActualizarDesdeEstado:
    """Tests del método actualizar_desde_estado."""

    def test_actualizar_desde_estado_modo_ambiente(self, qapp):
        """
        Test: Actualizar desde objeto EstadoTermostato en modo ambiente.

        Given: Controlador en modo "ambiente"
        When: Se llama a actualizar_desde_estado con temp_actual=23.0
        Then: Se muestra temp_actual
        """
        modelo = DisplayModelo(modo_vista="ambiente")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Mock de EstadoTermostato
        estado = Mock()
        estado.temp_actual = 23.0
        estado.temp_deseada = 25.0
        estado.falla_sensor = False

        controlador.actualizar_desde_estado(estado)

        assert controlador.modelo.temperatura == 23.0
        assert vista.label_temp.text() == "23.0"

    def test_actualizar_desde_estado_modo_deseada(self, qapp):
        """
        Test: Actualizar desde objeto EstadoTermostato en modo deseada.

        Given: Controlador en modo "deseada"
        When: Se llama a actualizar_desde_estado con temp_deseada=25.0
        Then: Se muestra temp_deseada
        """
        modelo = DisplayModelo(modo_vista="deseada")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        estado = Mock()
        estado.temp_actual = 23.0
        estado.temp_deseada = 25.0
        estado.falla_sensor = False

        controlador.actualizar_desde_estado(estado)

        assert controlador.modelo.temperatura == 25.0
        assert vista.label_temp.text() == "25.0"

    def test_actualizar_desde_estado_con_falla_sensor(self, qapp):
        """
        Test: Actualizar desde estado con falla de sensor.

        Given: Controlador inicializado
        When: Se llama a actualizar_desde_estado con falla_sensor=True
        Then: Se muestra error en la vista
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        estado = Mock()
        estado.temp_actual = 23.0
        estado.temp_deseada = 25.0
        estado.falla_sensor = True

        controlador.actualizar_desde_estado(estado)

        assert controlador.modelo.error_sensor is True
        assert vista.label_error.isVisible()


class TestInmutabilidadModelo:
    """Tests de inmutabilidad del modelo en el controlador."""

    def test_modelo_es_reemplazado_no_mutado(self, qapp):
        """
        Test: El controlador reemplaza el modelo en lugar de mutarlo.

        Given: Controlador con modelo inicial
        When: Se actualiza temperatura
        Then: Se crea nueva instancia del modelo (inmutabilidad)
        """
        modelo_inicial = DisplayModelo(temperatura=20.0)
        vista = DisplayVista()
        controlador = DisplayControlador(modelo_inicial, vista)

        # Guardar referencia al modelo inicial
        id_inicial = id(controlador.modelo)

        # Actualizar temperatura
        controlador.actualizar_temperatura(25.0)

        # El modelo debe ser una nueva instancia
        id_nuevo = id(controlador.modelo)
        assert id_inicial != id_nuevo

        # El modelo inicial no debe cambiar (inmutable)
        assert modelo_inicial.temperatura == 20.0

    def test_otros_campos_se_preservan_al_actualizar(self, qapp):
        """
        Test: Otros campos del modelo se preservan al actualizar.

        Given: Modelo con modo_vista="deseada" y encendido=True
        When: Se actualiza solo la temperatura
        Then: Los otros campos permanecen iguales
        """
        modelo = DisplayModelo(
            temperatura=20.0,
            modo_vista="deseada",
            encendido=True,
            error_sensor=False
        )
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        controlador.actualizar_temperatura(25.0)

        # Verificar que solo cambió la temperatura
        assert controlador.modelo.temperatura == 25.0
        assert controlador.modelo.modo_vista == "deseada"
        assert controlador.modelo.encendido is True
        assert controlador.modelo.error_sensor is False
