"""
Tests de integración para el panel de Indicadores.

Este módulo contiene tests end-to-end que verifican la integración completa
entre el modelo, la vista y el controlador del panel de indicadores.
"""

import pytest
from unittest.mock import Mock

from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo
from app.presentacion.paneles.indicadores.vista import IndicadoresVista
from app.presentacion.paneles.indicadores.controlador import IndicadoresControlador


class TestIntegracion:
    """Tests de integración del panel completo."""

    def test_flujo_completo_modelo_vista_controlador(self, qapp):
        """
        Verifica el flujo completo desde modelo hasta vista pasando por controlador.

        Este test valida que:
        1. El controlador se crea correctamente con modelo y vista
        2. Los cambios en el controlador actualizan el modelo
        3. Los cambios en el modelo se reflejan en la vista
        """
        # Setup: crear componentes MVC
        modelo = IndicadoresModelo()
        vista = IndicadoresVista()
        controlador = IndicadoresControlador(modelo, vista)

        # Estado inicial: sin alertas
        assert controlador.modelo.falla_sensor is False
        assert controlador.modelo.bateria_baja is False
        assert vista.alert_sensor.led.state is False
        assert vista.alert_bateria.led.state is False

        # Acción: activar falla sensor
        controlador.actualizar_falla_sensor(True)

        # Verificar: modelo actualizado
        assert controlador.modelo.falla_sensor is True

        # Verificar: vista actualizada (LED rojo pulsante)
        assert vista.alert_sensor._animacion_activa is True

        # Acción: activar batería baja
        controlador.actualizar_bateria_baja(True)

        # Verificar: ambas alertas activas
        assert controlador.modelo.falla_sensor is True
        assert controlador.modelo.bateria_baja is True
        assert vista.alert_sensor._animacion_activa is True
        assert vista.alert_bateria._animacion_activa is True

        # Acción: recuperar sensor
        controlador.actualizar_falla_sensor(False)

        # Verificar: solo batería sigue activa
        assert controlador.modelo.falla_sensor is False
        assert controlador.modelo.bateria_baja is True
        assert vista.alert_sensor._animacion_activa is False
        assert vista.alert_bateria._animacion_activa is True

    def test_actualizacion_desde_servidor_simulado(self, qapp, qtbot):
        """
        Simula la recepción de datos del servidor (JSON del RPi) y
        verifica que los indicadores se actualicen correctamente.
        """
        # Setup
        controlador = IndicadoresControlador(
            IndicadoresModelo(),
            IndicadoresVista()
        )

        # Mock del servidor que emite estado
        mock_servidor = Mock()
        mock_servidor.estado_recibido = Mock()

        # Escenario 1: Recibir JSON con falla_sensor: true
        json_data_1 = {"falla_sensor": True, "bateria_baja": False}
        controlador.actualizar_desde_estado(
            falla_sensor=json_data_1["falla_sensor"],
            bateria_baja=json_data_1["bateria_baja"]
        )

        # Verificar
        assert controlador.modelo.falla_sensor is True
        assert controlador.modelo.bateria_baja is False
        assert controlador.vista.alert_sensor._animacion_activa is True
        assert controlador.vista.alert_bateria._animacion_activa is False

        # Escenario 2: Recibir JSON con bateria_baja: true
        json_data_2 = {"falla_sensor": True, "bateria_baja": True}
        controlador.actualizar_desde_estado(
            falla_sensor=json_data_2["falla_sensor"],
            bateria_baja=json_data_2["bateria_baja"]
        )

        # Verificar ambas alertas
        assert controlador.modelo.falla_sensor is True
        assert controlador.modelo.bateria_baja is True
        assert controlador.vista.alert_sensor._animacion_activa is True
        assert controlador.vista.alert_bateria._animacion_activa is True

        # Escenario 3: Recibir JSON con todo normal
        json_data_3 = {"falla_sensor": False, "bateria_baja": False}
        controlador.actualizar_desde_estado(
            falla_sensor=json_data_3["falla_sensor"],
            bateria_baja=json_data_3["bateria_baja"]
        )

        # Verificar recuperación
        assert controlador.modelo.falla_sensor is False
        assert controlador.modelo.bateria_baja is False
        assert controlador.vista.alert_sensor._animacion_activa is False
        assert controlador.vista.alert_bateria._animacion_activa is False

    def test_transicion_estados_sensor(self, qapp):
        """
        Verifica las transiciones de estado del sensor: normal → error → normal.
        """
        controlador = IndicadoresControlador(
            IndicadoresModelo(),
            IndicadoresVista()
        )

        # Estado inicial: normal
        assert controlador.modelo.falla_sensor is False
        assert controlador.vista.alert_sensor._animacion_activa is False

        # Transición: normal → error
        controlador.actualizar_falla_sensor(True)
        assert controlador.modelo.falla_sensor is True
        assert controlador.vista.alert_sensor._animacion_activa is True

        # Transición: error → normal
        controlador.actualizar_falla_sensor(False)
        assert controlador.modelo.falla_sensor is False
        assert controlador.vista.alert_sensor._animacion_activa is False
        assert controlador.vista.alert_sensor.led.state is False

    def test_transicion_estados_bateria(self, qapp):
        """
        Verifica las transiciones de estado de batería: normal → warning → normal.
        """
        controlador = IndicadoresControlador(
            IndicadoresModelo(),
            IndicadoresVista()
        )

        # Estado inicial: normal
        assert controlador.modelo.bateria_baja is False
        assert controlador.vista.alert_bateria._animacion_activa is False

        # Transición: normal → warning
        controlador.actualizar_bateria_baja(True)
        assert controlador.modelo.bateria_baja is True
        assert controlador.vista.alert_bateria._animacion_activa is True

        # Transición: warning → normal
        controlador.actualizar_bateria_baja(False)
        assert controlador.modelo.bateria_baja is False
        assert controlador.vista.alert_bateria._animacion_activa is False
        assert controlador.vista.alert_bateria.led.state is False

    def test_multiples_alertas_simultaneas(self, qapp, qtbot):
        """
        Verifica que se puedan manejar múltiples alertas simultáneamente
        sin conflictos o comportamientos inesperados.
        """
        controlador = IndicadoresControlador(
            IndicadoresModelo(),
            IndicadoresVista()
        )

        # Capturar señales con Mocks
        sensor_activada = Mock()
        bateria_activada = Mock()
        controlador.alerta_activada.connect(sensor_activada)
        controlador.alerta_activada.connect(bateria_activada)

        # Activar ambas alertas simultáneamente
        controlador.actualizar_desde_estado(
            falla_sensor=True,
            bateria_baja=True
        )

        # Procesar eventos
        qtbot.wait(100)

        # Verificar estado del modelo
        assert controlador.modelo.falla_sensor is True
        assert controlador.modelo.bateria_baja is True

        # Verificar estado de la vista (ambos LEDs pulsando)
        assert controlador.vista.alert_sensor._animacion_activa is True
        assert controlador.vista.alert_bateria._animacion_activa is True

        # Verificar que se emitieron señales
        assert sensor_activada.call_count >= 1
        assert bateria_activada.call_count >= 1

        # Ahora desactivar ambas
        controlador.actualizar_desde_estado(
            falla_sensor=False,
            bateria_baja=False
        )

        # Verificar recuperación completa
        assert controlador.modelo.falla_sensor is False
        assert controlador.modelo.bateria_baja is False
        assert controlador.vista.alert_sensor._animacion_activa is False
        assert controlador.vista.alert_bateria._animacion_activa is False

    def test_señales_conectadas_a_otros_componentes(self, qapp, qtbot):
        """
        Verifica que las señales del controlador puedan ser conectadas
        a otros componentes y funcionen correctamente (simulación de
        integración con otros paneles o coordinador).
        """
        controlador = IndicadoresControlador(
            IndicadoresModelo(),
            IndicadoresVista()
        )

        # Mock de otro componente que escucha las señales
        componente_externo = Mock()

        # Conectar señales
        controlador.alerta_activada.connect(componente_externo.on_alerta_activada)
        controlador.alerta_desactivada.connect(componente_externo.on_alerta_desactivada)

        # Activar alerta sensor
        with qtbot.waitSignal(controlador.alerta_activada, timeout=1000):
            controlador.actualizar_falla_sensor(True)

        # Verificar que componente externo recibió la señal
        componente_externo.on_alerta_activada.assert_called_once_with("sensor")

        # Desactivar alerta sensor
        with qtbot.waitSignal(controlador.alerta_desactivada, timeout=1000):
            controlador.actualizar_falla_sensor(False)

        # Verificar señal de desactivación
        componente_externo.on_alerta_desactivada.assert_called_once_with("sensor")

    def test_inmutabilidad_del_modelo_en_integracion(self, qapp):
        """
        Verifica que el modelo se mantenga inmutable durante
        operaciones de integración complejas.
        """
        modelo_inicial = IndicadoresModelo()
        vista = IndicadoresVista()
        controlador = IndicadoresControlador(modelo_inicial, vista)

        # Guardar referencia al modelo inicial
        id_modelo_inicial = id(controlador.modelo)

        # Realizar múltiples actualizaciones
        controlador.actualizar_falla_sensor(True)

        # Verificar que se creó un nuevo modelo (inmutabilidad)
        assert id(controlador.modelo) != id_modelo_inicial

        # Guardar referencia al segundo modelo
        id_modelo_segundo = id(controlador.modelo)

        # Otra actualización
        controlador.actualizar_bateria_baja(True)

        # Verificar nuevamente inmutabilidad
        assert id(controlador.modelo) != id_modelo_segundo

        # Verificar que modelo original no cambió
        assert modelo_inicial.falla_sensor is False
        assert modelo_inicial.bateria_baja is False

        # Verificar estado actual correcto
        assert controlador.modelo.falla_sensor is True
        assert controlador.modelo.bateria_baja is True
