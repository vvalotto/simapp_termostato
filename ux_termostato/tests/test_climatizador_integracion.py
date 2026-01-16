"""
Tests de integración para el panel Climatizador.

Este módulo contiene tests que validan la integración entre componentes
del panel Climatizador (Modelo, Vista, Controlador) y con sistemas externos.
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import QTimer

from app.presentacion.paneles.climatizador.modelo import (
    ClimatizadorModelo,
    MODO_CALENTANDO,
    MODO_ENFRIANDO,
    MODO_REPOSO,
    MODO_APAGADO,
)
from app.presentacion.paneles.climatizador.vista import ClimatizadorVista
from app.presentacion.paneles.climatizador.controlador import ClimatizadorControlador


class TestIntegracionMVC:
    """Tests de integración del patrón MVC completo."""

    def test_flujo_completo_modelo_vista_controlador(self, qapp):
        """
        Test: Flujo completo desde modelo hasta vista.

        Given: Se crea un sistema MVC completo
        When: Se actualiza el modelo a través del controlador
        Then: Los cambios se reflejan en la vista correctamente
        """
        # Crear componentes
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Estado inicial: reposo activo
        assert controlador.modelo.modo == MODO_REPOSO
        assert vista.indicador_reposo.property("activo") == "true"

        # Cambio 1: Calentando
        controlador.actualizar_estado(MODO_CALENTANDO)
        assert controlador.modelo.modo == MODO_CALENTANDO
        assert vista.indicador_calor.property("activo") == "true"
        assert vista.indicador_reposo.property("activo") == "false"

        # Cambio 2: Enfriando
        controlador.actualizar_estado(MODO_ENFRIANDO)
        assert controlador.modelo.modo == MODO_ENFRIANDO
        assert vista.indicador_frio.property("activo") == "true"
        assert vista.indicador_calor.property("activo") == "false"

        # Cambio 3: Apagar
        controlador.set_encendido(False)
        assert controlador.modelo.encendido is False
        assert vista.indicador_frio.property("activo") == "false"
        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"

    def test_transiciones_entre_estados(self, qapp):
        """
        Test: Múltiples transiciones consecutivas.

        Given: Sistema MVC configurado
        When: Se realizan múltiples cambios de estado seguidos
        Then: Cada transición se refleja correctamente en vista
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Secuencia de transiciones
        estados = [
            MODO_CALENTANDO,
            MODO_REPOSO,
            MODO_ENFRIANDO,
            MODO_REPOSO,
            MODO_CALENTANDO,
        ]

        for estado in estados:
            controlador.actualizar_estado(estado)
            assert controlador.modelo.modo == estado

            # Verificar que solo el indicador correcto está activo
            if estado == MODO_CALENTANDO:
                assert vista.indicador_calor.property("activo") == "true"
                assert vista.indicador_reposo.property("activo") == "false"
                assert vista.indicador_frio.property("activo") == "false"
            elif estado == MODO_REPOSO:
                assert vista.indicador_calor.property("activo") == "false"
                assert vista.indicador_reposo.property("activo") == "true"
                assert vista.indicador_frio.property("activo") == "false"
            elif estado == MODO_ENFRIANDO:
                assert vista.indicador_calor.property("activo") == "false"
                assert vista.indicador_reposo.property("activo") == "false"
                assert vista.indicador_frio.property("activo") == "true"


class TestIntegracionConServidor:
    """Tests de integración con servidor simulado."""

    def test_actualizacion_desde_servidor_simulado(self, qapp):
        """
        Test: Actualizar desde datos de servidor.

        Given: Sistema MVC configurado
        When: Se recibe actualización desde servidor con modo_climatizador
        Then: El modelo y vista se actualizan correctamente
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Simular objeto de estado del servidor
        estado_servidor = Mock()
        estado_servidor.modo_climatizador = MODO_CALENTANDO

        # Actualizar desde servidor
        controlador.actualizar_desde_estado(estado_servidor)

        # Verificar que se aplicó el cambio
        assert controlador.modelo.modo == MODO_CALENTANDO
        assert vista.indicador_calor.property("activo") == "true"

    def test_cambio_estado_en_tiempo_real(self, qapp):
        """
        Test: Simular cambios en tiempo real desde servidor.

        Given: Sistema MVC configurado
        When: Se simulan múltiples actualizaciones del servidor
        Then: Cada actualización se refleja correctamente
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Simular secuencia de actualizaciones desde servidor
        estados_servidor = [
            Mock(modo_climatizador=MODO_CALENTANDO),
            Mock(modo_climatizador=MODO_REPOSO),
            Mock(modo_climatizador=MODO_ENFRIANDO),
        ]

        for estado in estados_servidor:
            controlador.actualizar_desde_estado(estado)
            assert controlador.modelo.modo == estado.modo_climatizador


class TestIntegracionEstadosEspeciales:
    """Tests de integración para estados especiales."""

    def test_cambio_estado_encendido_apagado(self, qapp):
        """
        Test: Cambiar entre encendido y apagado.

        Given: Sistema MVC con modo activo
        When: Se alterna encendido/apagado
        Then: La vista refleja el estado correcto
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Estado inicial: encendido
        assert vista.indicador_calor.property("activo") == "true"

        # Apagar
        controlador.set_encendido(False)
        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"

        # Encender
        controlador.set_encendido(True)
        # Sigue en modo calentando, debe mostrar calor activo
        assert vista.indicador_calor.property("activo") == "true"

    def test_todos_estados_del_climatizador(self, qapp):
        """
        Test: Verificar todos los estados posibles.

        Given: Sistema MVC configurado
        When: Se prueban todos los estados definidos
        Then: Cada estado se renderiza correctamente
        """
        modelo = ClimatizadorModelo()
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Test 1: Calentando
        controlador.actualizar_estado(MODO_CALENTANDO)
        assert controlador.modelo.esta_calentando
        assert vista.indicador_calor.property("activo") == "true"

        # Test 2: Enfriando
        controlador.actualizar_estado(MODO_ENFRIANDO)
        assert controlador.modelo.esta_enfriando
        assert vista.indicador_frio.property("activo") == "true"

        # Test 3: Reposo
        controlador.actualizar_estado(MODO_REPOSO)
        assert controlador.modelo.esta_en_reposo
        assert vista.indicador_reposo.property("activo") == "true"

        # Test 4: Apagado (modo apagado)
        controlador.actualizar_estado(MODO_APAGADO)
        assert controlador.modelo.esta_apagado
        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"


class TestIntegracionSignals:
    """Tests de integración de señales PyQt."""

    def test_signals_se_emiten_correctamente(self, qapp):
        """
        Test: Las señales se emiten y pueden ser capturadas.

        Given: Sistema MVC configurado
        When: Se cambia el estado
        Then: La señal estado_cambiado se emite correctamente
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Capturar señales
        signals_emitidas = []

        def capturar_signal(modo):
            signals_emitidas.append(modo)

        controlador.estado_cambiado.connect(capturar_signal)

        # Generar cambios
        controlador.actualizar_estado(MODO_CALENTANDO)
        controlador.actualizar_estado(MODO_ENFRIANDO)
        controlador.actualizar_estado(MODO_REPOSO)

        # Verificar que se emitieron 3 señales
        assert len(signals_emitidas) == 3
        assert signals_emitidas[0] == MODO_CALENTANDO
        assert signals_emitidas[1] == MODO_ENFRIANDO
        assert signals_emitidas[2] == MODO_REPOSO

    def test_signals_con_multiples_suscriptores(self, qapp):
        """
        Test: Múltiples componentes pueden suscribirse a señales.

        Given: Sistema MVC con múltiples suscriptores
        When: Se emite una señal
        Then: Todos los suscriptores reciben la señal
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Crear múltiples suscriptores
        suscriptor1 = []
        suscriptor2 = []
        suscriptor3 = []

        controlador.estado_cambiado.connect(lambda m: suscriptor1.append(m))
        controlador.estado_cambiado.connect(lambda m: suscriptor2.append(m))
        controlador.estado_cambiado.connect(lambda m: suscriptor3.append(m))

        # Emitir señal
        controlador.actualizar_estado(MODO_CALENTANDO)

        # Verificar que todos recibieron la señal
        assert suscriptor1 == [MODO_CALENTANDO]
        assert suscriptor2 == [MODO_CALENTANDO]
        assert suscriptor3 == [MODO_CALENTANDO]


class TestIntegracionAnimaciones:
    """Tests de integración para animaciones."""

    def test_animaciones_se_inician_y_detienen(self, qapp):
        """
        Test: Animaciones se inician y detienen correctamente.

        Given: Sistema MVC configurado
        When: Se cambia entre estados con/sin animación
        Then: Las animaciones se gestionan correctamente
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # Cambiar a calentando (debe iniciar animación)
        controlador.actualizar_estado(MODO_CALENTANDO)
        assert hasattr(vista.indicador_calor, '_animation')
        from PyQt6.QtCore import QAbstractAnimation
        assert vista.indicador_calor._animation.state() != QAbstractAnimation.State.Stopped

        # Cambiar a reposo (debe detener animación de calor)
        controlador.actualizar_estado(MODO_REPOSO)
        if hasattr(vista.indicador_calor, '_animation'):
            assert vista.indicador_calor._animation.state() == QAbstractAnimation.State.Stopped

        # Cambiar a enfriando (debe iniciar animación)
        controlador.actualizar_estado(MODO_ENFRIANDO)
        assert hasattr(vista.indicador_frio, '_animation')
        assert vista.indicador_frio._animation.state() != QAbstractAnimation.State.Stopped


class TestIntegracionRendimiento:
    """Tests de integración para rendimiento."""

    def test_multiples_actualizaciones_rapidas(self, qapp):
        """
        Test: El sistema maneja múltiples actualizaciones rápidas.

        Given: Sistema MVC configurado
        When: Se realizan múltiples actualizaciones rápidas
        Then: El sistema se mantiene estable y consistente
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)
        vista = ClimatizadorVista()
        controlador = ClimatizadorControlador(modelo, vista)

        # 100 actualizaciones rápidas alternando estados
        estados = [MODO_CALENTANDO, MODO_ENFRIANDO, MODO_REPOSO]
        for i in range(100):
            estado = estados[i % len(estados)]
            controlador.actualizar_estado(estado)

        # Verificar que el sistema está en estado consistente
        # i=99: 99 % 3 = 0 -> MODO_CALENTANDO es el último estado
        assert controlador.modelo.modo == MODO_CALENTANDO
        assert vista.indicador_calor.property("activo") == "true"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"
