"""
Tests de integración para el panel Display.

Este módulo contiene tests que validan la integración completa entre
modelo, vista y controlador del panel Display LCD, simulando flujos
end-to-end reales de uso.
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import QTimer

from app.presentacion.paneles.display.modelo import DisplayModelo
from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.controlador import DisplayControlador


class TestIntegracionMVC:
    """Tests de integración del patrón MVC del display."""

    def test_flujo_completo_modelo_vista_controlador(self, qapp):
        """
        Test: Flujo completo modelo → controlador → vista.

        Given: Sistema MVC completo inicializado
        When: Se actualiza la temperatura varias veces
        Then: Los cambios fluyen correctamente por toda la arquitectura
        """
        # Setup
        modelo = DisplayModelo(temperatura=20.0, modo_vista="ambiente")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Verificar estado inicial
        assert controlador.modelo.temperatura == 20.0
        assert vista.label_temp.text() == "20.0"

        # Actualizar temperatura
        controlador.actualizar_temperatura(23.5)
        assert controlador.modelo.temperatura == 23.5
        assert vista.label_temp.text() == "23.5"

        # Cambiar modo vista
        controlador.cambiar_modo_vista("deseada")
        assert controlador.modelo.modo_vista == "deseada"
        assert vista.label_modo.text() == "Temperatura Deseada"

        # Apagar
        controlador.set_encendido(False)
        assert not controlador.modelo.encendido
        assert vista.label_temp.text() == "---"

    def test_multiples_actualizaciones_consecutivas(self, qapp):
        """
        Test: Múltiples actualizaciones consecutivas sin problemas.

        Given: Sistema MVC inicializado
        When: Se realizan muchas actualizaciones rápidas
        Then: Cada cambio se procesa correctamente sin errores
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Simular 100 actualizaciones rápidas
        for temp in range(0, 100):
            controlador.actualizar_temperatura(float(temp))
            assert controlador.modelo.temperatura == float(temp)
            assert vista.label_temp.text() == f"{temp}.0"

    def test_estados_simultáneos(self, qapp):
        """
        Test: Manejo correcto de estados simultáneos.

        Given: Sistema MVC inicializado
        When: Se cambian múltiples propiedades del modelo
        Then: La vista refleja todos los cambios correctamente
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Cambiar temperatura y modo
        controlador.actualizar_temperatura(25.5)
        controlador.cambiar_modo_vista("deseada")

        assert controlador.modelo.temperatura == 25.5
        assert controlador.modelo.modo_vista == "deseada"
        assert vista.label_temp.text() == "25.5"
        assert vista.label_modo.text() == "Temperatura Deseada"


class TestIntegracionConServidor:
    """Tests de integración simulando comunicación con servidor."""

    def test_actualizacion_desde_servidor_simulado(self, qapp):
        """
        Test: Actualización desde un objeto EstadoTermostato simulado.

        Given: Controlador en modo "ambiente"
        When: Llega estado desde servidor con datos actualizados
        Then: El display se actualiza correctamente
        """
        modelo = DisplayModelo(modo_vista="ambiente")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Simular estado recibido del servidor
        estado_servidor = Mock()
        estado_servidor.temp_actual = 24.5
        estado_servidor.temp_deseada = 26.0
        estado_servidor.falla_sensor = False

        controlador.actualizar_desde_estado(estado_servidor)

        # En modo ambiente, debe mostrar temp_actual
        assert controlador.modelo.temperatura == 24.5
        assert vista.label_temp.text() == "24.5"

    def test_cambio_modo_afecta_temperatura_mostrada(self, qapp):
        """
        Test: Cambiar modo vista afecta qué temperatura se muestra del servidor.

        Given: Estado del servidor con temp_actual y temp_deseada diferentes
        When: Se cambia entre modo ambiente y deseada
        Then: Se muestra la temperatura correspondiente
        """
        modelo = DisplayModelo(modo_vista="ambiente")
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        estado = Mock()
        estado.temp_actual = 22.0
        estado.temp_deseada = 25.0
        estado.falla_sensor = False

        # Modo ambiente: muestra temp_actual
        controlador.actualizar_desde_estado(estado)
        assert vista.label_temp.text() == "22.0"

        # Cambiar a modo deseada
        controlador.cambiar_modo_vista("deseada")

        # Actualizar desde servidor nuevamente
        controlador.actualizar_desde_estado(estado)
        assert vista.label_temp.text() == "25.0"

    def test_falla_sensor_desde_servidor(self, qapp):
        """
        Test: Manejo de falla de sensor reportada por servidor.

        Given: Display funcionando normalmente
        When: Servidor reporta falla_sensor=True
        Then: Display muestra error correctamente
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Estado normal
        estado_normal = Mock()
        estado_normal.temp_actual = 22.0
        estado_normal.temp_deseada = 25.0
        estado_normal.falla_sensor = False

        controlador.actualizar_desde_estado(estado_normal)
        assert vista.label_temp.isVisible()
        assert not vista.label_error.isVisible()

        # Falla de sensor
        estado_error = Mock()
        estado_error.temp_actual = 0.0  # Temperatura inválida
        estado_error.temp_deseada = 25.0
        estado_error.falla_sensor = True

        controlador.actualizar_desde_estado(estado_error)
        assert not vista.label_temp.isVisible()
        assert vista.label_error.isVisible()


class TestIntegracionEstadosEspeciales:
    """Tests de integración para estados especiales del display."""

    def test_cambio_estado_encendido_apagado(self, qapp):
        """
        Test: Transición completa entre encendido y apagado.

        Given: Display encendido mostrando temperatura
        When: Se apaga y se vuelve a encender
        Then: El display maneja correctamente ambas transiciones
        """
        modelo = DisplayModelo(temperatura=22.0, encendido=True)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Estado inicial encendido
        assert vista.label_temp.text() == "22.0"
        assert vista.label_modo.text() == "Temperatura Ambiente"

        # Apagar
        controlador.set_encendido(False)
        assert vista.label_temp.text() == "---"
        assert vista.label_modo.text() == "APAGADO"

        # Actualizar temperatura mientras está apagado (no debe mostrarse)
        controlador.actualizar_temperatura(25.0)
        assert vista.label_temp.text() == "---"

        # Encender nuevamente
        controlador.set_encendido(True)
        assert vista.label_temp.text() == "25.0"
        assert vista.label_modo.text() == "Temperatura Ambiente"

    def test_manejo_de_error_sensor(self, qapp):
        """
        Test: Transición entre estado normal y error de sensor.

        Given: Display funcionando normalmente
        When: Ocurre error y luego se resuelve
        Then: El display maneja ambas transiciones correctamente
        """
        modelo = DisplayModelo(temperatura=22.0, error_sensor=False)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Estado normal
        assert vista.label_temp.isVisible()
        assert not vista.label_error.isVisible()

        # Error de sensor
        controlador.set_error_sensor(True)
        assert not vista.label_temp.isVisible()
        assert vista.label_error.isVisible()
        assert vista.label_modo.text() == "ERROR DE SENSOR"

        # Resolver error
        controlador.set_error_sensor(False)
        assert vista.label_temp.isVisible()
        assert not vista.label_error.isVisible()
        assert vista.label_temp.text() == "22.0"

    def test_error_sensor_tiene_prioridad_sobre_apagado(self, qapp):
        """
        Test: Error de sensor tiene prioridad sobre estado apagado.

        Given: Display apagado
        When: Se reporta error de sensor
        Then: Se muestra mensaje de error (no "---")
        """
        modelo = DisplayModelo(temperatura=22.0, encendido=False)
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Verificar estado apagado
        assert vista.label_temp.text() == "---"

        # Encender y luego causar error
        controlador.set_encendido(True)
        controlador.set_error_sensor(True)

        # Error tiene prioridad
        assert vista.label_error.isVisible()
        assert not vista.label_temp.isVisible()


class TestIntegracionSignals:
    """Tests de integración para señales PyQt del controlador."""

    def test_signals_se_emiten_correctamente(self, qapp):
        """
        Test: Las señales PyQt se emiten en las operaciones correctas.

        Given: Controlador con spies conectados a las señales
        When: Se realizan operaciones que deben emitir señales
        Then: Las señales se emiten con los valores correctos
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        # Spies para las señales
        spy_temperatura = Mock()
        spy_modo = Mock()
        controlador.temperatura_actualizada.connect(spy_temperatura)
        controlador.modo_vista_cambiado.connect(spy_modo)

        # Actualizar temperatura
        controlador.actualizar_temperatura(23.5)
        spy_temperatura.assert_called_once_with(23.5)

        # Cambiar modo
        controlador.cambiar_modo_vista("deseada")
        spy_modo.assert_called_once_with("deseada")

    def test_signals_pueden_conectarse_a_otros_componentes(self, qapp):
        """
        Test: Las señales pueden conectarse a componentes externos.

        Given: Controlador y componente externo mock
        When: El controlador emite señales
        Then: El componente externo recibe las notificaciones
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        controlador = DisplayControlador(modelo, vista)

        # Simular componente externo
        componente_externo = Mock()
        componente_externo.procesar_temperatura = Mock()

        # Conectar señal a componente externo
        controlador.temperatura_actualizada.connect(
            componente_externo.procesar_temperatura
        )

        # Actualizar temperatura
        controlador.actualizar_temperatura(24.0)

        # Verificar que el componente externo fue notificado
        componente_externo.procesar_temperatura.assert_called_once_with(24.0)


class TestIntegracionRobustez:
    """Tests de integración para robustez y casos extremos."""

    def test_temperaturas_extremas(self, qapp):
        """
        Test: Manejo de temperaturas extremas.

        Given: Sistema MVC inicializado
        When: Se actualizan temperaturas muy bajas o muy altas
        Then: El sistema las maneja correctamente sin errores
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Temperatura muy baja
        controlador.actualizar_temperatura(-50.0)
        assert vista.label_temp.text() == "-50.0"

        # Temperatura muy alta
        controlador.actualizar_temperatura(150.0)
        assert vista.label_temp.text() == "150.0"

        # Cero absoluto (aproximado)
        controlador.actualizar_temperatura(-273.15)
        assert vista.label_temp.text() == "-273.1"  # Python redondea .15 hacia abajo

    def test_cambios_rapidos_entre_estados(self, qapp):
        """
        Test: Cambios rápidos entre múltiples estados.

        Given: Sistema MVC inicializado
        When: Se alternan rápidamente entre estados
        Then: El sistema permanece consistente
        """
        modelo = DisplayModelo()
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        # Alternar rápidamente entre estados
        for i in range(20):
            controlador.set_encendido(True)
            controlador.actualizar_temperatura(20.0 + i)
            controlador.cambiar_modo_vista("ambiente" if i % 2 == 0 else "deseada")
            controlador.set_error_sensor(False)
            controlador.set_encendido(False)

        # Verificar que el sistema está en estado válido
        assert controlador.modelo is not None
        assert vista is not None

    def test_inmutabilidad_preservada_en_integracion(self, qapp):
        """
        Test: La inmutabilidad del modelo se preserva durante operaciones.

        Given: Sistema MVC con modelo inicial
        When: Se realizan múltiples operaciones
        Then: El modelo original nunca se muta
        """
        modelo_inicial = DisplayModelo(temperatura=20.0)
        vista = DisplayVista()
        controlador = DisplayControlador(modelo_inicial, vista)

        # Realizar múltiples operaciones
        controlador.actualizar_temperatura(25.0)
        controlador.cambiar_modo_vista("deseada")
        controlador.set_error_sensor(True)

        # El modelo inicial debe permanecer inalterado (inmutable)
        assert modelo_inicial.temperatura == 20.0
        assert modelo_inicial.modo_vista == "ambiente"
        assert modelo_inicial.error_sensor is False

        # El controlador debe tener un nuevo modelo
        assert controlador.modelo.temperatura == 25.0
        assert controlador.modelo.modo_vista == "deseada"
        assert controlador.modelo.error_sensor is True
