"""
Tests unitarios para ClimatizadorControlador.

Este módulo contiene los tests que validan el comportamiento del controlador
del panel Climatizador, incluyendo métodos, señales y validación.
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import QObject

from app.presentacion.paneles.climatizador.modelo import (
    ClimatizadorModelo,
    MODO_CALENTANDO,
    MODO_ENFRIANDO,
    MODO_REPOSO,
    MODO_APAGADO,
)
from app.presentacion.paneles.climatizador.vista import ClimatizadorVista
from app.presentacion.paneles.climatizador.controlador import ClimatizadorControlador


class TestCreacion:
    """Tests de creación del controlador ClimatizadorControlador."""

    def test_crear_controlador(self, qapp):
        """
        Test: Crear controlador sin errores.

        Given: Modelo y vista válidos
        When: Se crea una instancia de ClimatizadorControlador
        Then: El controlador se crea correctamente
        """
        modelo = ClimatizadorModelo()
        vista = ClimatizadorVista()

        controlador = ClimatizadorControlador(modelo, vista)

        assert controlador is not None
        assert isinstance(controlador, QObject)

    def test_modelo_inicial(self, qapp):
        """
        Test: El modelo inicial se almacena correctamente.

        Given: Modelo con valores específicos
        When: Se crea el controlador
        Then: El controlador retorna el modelo correcto
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)
        vista = ClimatizadorVista()

        controlador = ClimatizadorControlador(modelo, vista)

        assert controlador.modelo == modelo
        assert controlador.modelo.modo == MODO_CALENTANDO
        assert controlador.modelo.encendido is True

    def test_vista_asociada(self, qapp):
        """
        Test: La vista se asocia correctamente.

        Given: Vista creada
        When: Se crea el controlador
        Then: El controlador retorna la vista correcta
        """
        modelo = ClimatizadorModelo()
        vista = ClimatizadorVista()

        controlador = ClimatizadorControlador(modelo, vista)

        assert controlador.vista == vista


class TestMetodos:
    """Tests de métodos del controlador."""

    def test_actualizar_estado_calentando(self, qapp):
        """
        Test: Actualizar estado a calentando.

        Given: Controlador con estado inicial
        When: Se llama a actualizar_estado(MODO_CALENTANDO)
        Then: El modelo se actualiza y la vista se renderiza
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        controlador.actualizar_estado(MODO_CALENTANDO)

        assert controlador.modelo.modo == MODO_CALENTANDO
        # Verificar que la vista se actualizó
        assert vista.indicador_calor.property("activo") == "true"

    def test_actualizar_estado_enfriando(self, qapp):
        """
        Test: Actualizar estado a enfriando.

        Given: Controlador con estado inicial
        When: Se llama a actualizar_estado(MODO_ENFRIANDO)
        Then: El modelo se actualiza correctamente
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        controlador.actualizar_estado(MODO_ENFRIANDO)

        assert controlador.modelo.modo == MODO_ENFRIANDO
        assert vista.indicador_frio.property("activo") == "true"

    def test_actualizar_estado_reposo(self, qapp):
        """
        Test: Actualizar estado a reposo.

        Given: Controlador con modo calentando
        When: Se llama a actualizar_estado(MODO_REPOSO)
        Then: El modelo cambia a reposo
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        controlador.actualizar_estado(MODO_REPOSO)

        assert controlador.modelo.modo == MODO_REPOSO
        assert vista.indicador_reposo.property("activo") == "true"

    def test_set_encendido(self, qapp):
        """
        Test: Cambiar estado de encendido.

        Given: Controlador con encendido=True
        When: Se llama a set_encendido(False)
        Then: El modelo actualiza encendido a False
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        controlador.set_encendido(False)

        assert controlador.modelo.encendido is False
        # Todos los indicadores deben estar inactivos
        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"

    def test_actualizar_desde_estado_termostato(self, qapp):
        """
        Test: Actualizar desde objeto EstadoTermostato.

        Given: Controlador creado
        When: Se llama a actualizar_desde_estado() con objeto que tiene modo_climatizador
        Then: El modelo se actualiza con el modo del termostato
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Mock de objeto EstadoTermostato
        estado_termostato = Mock()
        estado_termostato.modo_climatizador = MODO_ENFRIANDO

        controlador.actualizar_desde_estado(estado_termostato)

        assert controlador.modelo.modo == MODO_ENFRIANDO

    def test_actualizar_desde_estado_sin_atributo(self, qapp):
        """
        Test: Actualizar desde objeto sin modo_climatizador.

        Given: Controlador creado
        When: Se llama con objeto sin atributo modo_climatizador
        Then: Se asume MODO_REPOSO
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Mock sin atributo modo_climatizador
        estado_termostato = Mock(spec=[])

        controlador.actualizar_desde_estado(estado_termostato)

        assert controlador.modelo.modo == MODO_REPOSO


class TestSignals:
    """Tests de señales emitidas por el controlador."""

    def test_emite_signal_al_cambiar_estado(self, qapp):
        """
        Test: Emitir señal estado_cambiado al cambiar estado.

        Given: Controlador creado
        When: Se actualiza el estado
        Then: Se emite la señal estado_cambiado con el nuevo modo
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Mock para capturar la señal
        signal_received = []

        def slot_signal(modo):
            signal_received.append(modo)

        controlador.estado_cambiado.connect(slot_signal)

        # Cambiar estado
        controlador.actualizar_estado(MODO_CALENTANDO)

        assert len(signal_received) == 1
        assert signal_received[0] == MODO_CALENTANDO

    def test_emite_signal_con_cada_cambio(self, qapp):
        """
        Test: Emitir señal en cada cambio de estado.

        Given: Controlador creado
        When: Se cambia el estado múltiples veces
        Then: Se emite señal en cada cambio
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        signals_received = []
        controlador.estado_cambiado.connect(lambda modo: signals_received.append(modo))

        # Múltiples cambios
        controlador.actualizar_estado(MODO_CALENTANDO)
        controlador.actualizar_estado(MODO_REPOSO)
        controlador.actualizar_estado(MODO_ENFRIANDO)

        assert len(signals_received) == 3
        assert signals_received[0] == MODO_CALENTANDO
        assert signals_received[1] == MODO_REPOSO
        assert signals_received[2] == MODO_ENFRIANDO


class TestValidacion:
    """Tests de validación del controlador."""

    def test_estado_invalido_lanza_error(self, qapp):
        """
        Test: Estado inválido lanza ValueError.

        Given: Controlador creado
        When: Se llama a actualizar_estado() con modo inválido
        Then: Se lanza ValueError con mensaje descriptivo
        """
        modelo = ClimatizadorModelo()
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        with pytest.raises(ValueError) as exc_info:
            controlador.actualizar_estado("modo_invalido")

        assert "Modo inválido" in str(exc_info.value)
        assert "modo_invalido" in str(exc_info.value)

    def test_estado_vacio_lanza_error(self, qapp):
        """
        Test: Estado vacío lanza ValueError.

        Given: Controlador creado
        When: Se llama con modo=""
        Then: Se lanza ValueError
        """
        modelo = ClimatizadorModelo()
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        with pytest.raises(ValueError):
            controlador.actualizar_estado("")


class TestInmutabilidadModelo:
    """Tests que verifican que el modelo se maneja inmutablemente."""

    def test_actualizar_crea_nuevo_modelo(self, qapp):
        """
        Test: Actualizar estado crea una nueva instancia del modelo.

        Given: Controlador con modelo inicial
        When: Se actualiza el estado
        Then: Se crea una nueva instancia de modelo (inmutabilidad)
        """
        modelo_inicial = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo_inicial, vista)

        # Guardar referencia al modelo original
        modelo_original = controlador.modelo

        # Actualizar estado
        controlador.actualizar_estado(MODO_CALENTANDO)

        # Verificar que es una nueva instancia
        assert controlador.modelo is not modelo_original
        assert controlador.modelo != modelo_original
        assert controlador.modelo.modo == MODO_CALENTANDO

    def test_set_encendido_crea_nuevo_modelo(self, qapp):
        """
        Test: set_encendido crea una nueva instancia del modelo.

        Given: Controlador con modelo inicial
        When: Se cambia el estado de encendido
        Then: Se crea una nueva instancia de modelo
        """
        modelo_inicial = ClimatizadorModelo(encendido=True)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo_inicial, vista)

        modelo_original = controlador.modelo

        controlador.set_encendido(False)

        assert controlador.modelo is not modelo_original
        assert controlador.modelo.encendido is False
