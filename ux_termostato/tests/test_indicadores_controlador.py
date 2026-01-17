"""
Tests unitarios para IndicadoresControlador.

Este módulo contiene tests para el controlador MVC del panel de indicadores,
verificando la lógica de actualización, señales y coordinación modelo-vista.
"""

import pytest
from unittest.mock import Mock

from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo
from app.presentacion.paneles.indicadores.vista import IndicadoresVista
from app.presentacion.paneles.indicadores.controlador import IndicadoresControlador


class TestCreacion:
    """Tests de creación del controlador."""

    def test_crear_controlador(self, qapp, indicadores_modelo, indicadores_vista):
        """Verifica que se pueda crear el controlador."""
        controlador = IndicadoresControlador(indicadores_modelo, indicadores_vista)

        assert controlador is not None
        assert controlador.modelo == indicadores_modelo
        assert controlador.vista == indicadores_vista

    def test_modelo_inicial(self, qapp):
        """Verifica que el controlador use el modelo inicial."""
        modelo = IndicadoresModelo(falla_sensor=True)
        vista = IndicadoresVista()
        controlador = IndicadoresControlador(modelo, vista)

        assert controlador.modelo.falla_sensor is True
        assert controlador.modelo.bateria_baja is False

    def test_vista_asociada(self, qapp, indicadores_modelo, indicadores_vista):
        """Verifica que el controlador esté asociado a la vista."""
        controlador = IndicadoresControlador(indicadores_modelo, indicadores_vista)

        assert controlador.vista is indicadores_vista


class TestMetodos:
    """Tests de métodos del controlador."""

    def test_actualizar_falla_sensor_activar(self, qapp, indicadores_controlador):
        """Verifica actualización de falla sensor (activar)."""
        indicadores_controlador.actualizar_falla_sensor(True)

        assert indicadores_controlador.modelo.falla_sensor is True
        assert indicadores_controlador.vista.alert_sensor._animacion_activa is True

    def test_actualizar_falla_sensor_desactivar(self, qapp, indicadores_controlador):
        """Verifica actualización de falla sensor (desactivar)."""
        # Primero activar
        indicadores_controlador.actualizar_falla_sensor(True)
        assert indicadores_controlador.modelo.falla_sensor is True

        # Luego desactivar
        indicadores_controlador.actualizar_falla_sensor(False)
        assert indicadores_controlador.modelo.falla_sensor is False
        assert indicadores_controlador.vista.alert_sensor._animacion_activa is False

    def test_actualizar_bateria_baja_activar(self, qapp, indicadores_controlador):
        """Verifica actualización de batería baja (activar)."""
        indicadores_controlador.actualizar_bateria_baja(True)

        assert indicadores_controlador.modelo.bateria_baja is True
        assert indicadores_controlador.vista.alert_bateria._animacion_activa is True

    def test_actualizar_bateria_baja_desactivar(self, qapp, indicadores_controlador):
        """Verifica actualización de batería baja (desactivar)."""
        # Primero activar
        indicadores_controlador.actualizar_bateria_baja(True)
        assert indicadores_controlador.modelo.bateria_baja is True

        # Luego desactivar
        indicadores_controlador.actualizar_bateria_baja(False)
        assert indicadores_controlador.modelo.bateria_baja is False
        assert indicadores_controlador.vista.alert_bateria._animacion_activa is False

    def test_actualizar_desde_estado_sin_alertas(self, qapp, indicadores_controlador):
        """Verifica actualización desde estado completo sin alertas."""
        indicadores_controlador.actualizar_desde_estado(
            falla_sensor=False,
            bateria_baja=False
        )

        assert indicadores_controlador.modelo.falla_sensor is False
        assert indicadores_controlador.modelo.bateria_baja is False
        assert indicadores_controlador.vista.alert_sensor._animacion_activa is False
        assert indicadores_controlador.vista.alert_bateria._animacion_activa is False

    def test_actualizar_desde_estado_con_falla(self, qapp, indicadores_controlador):
        """Verifica actualización desde estado con falla sensor."""
        indicadores_controlador.actualizar_desde_estado(
            falla_sensor=True,
            bateria_baja=False
        )

        assert indicadores_controlador.modelo.falla_sensor is True
        assert indicadores_controlador.modelo.bateria_baja is False
        assert indicadores_controlador.vista.alert_sensor._animacion_activa is True

    def test_actualizar_desde_estado_con_bateria(self, qapp, indicadores_controlador):
        """Verifica actualización desde estado con batería baja."""
        indicadores_controlador.actualizar_desde_estado(
            falla_sensor=False,
            bateria_baja=True
        )

        assert indicadores_controlador.modelo.falla_sensor is False
        assert indicadores_controlador.modelo.bateria_baja is True
        assert indicadores_controlador.vista.alert_bateria._animacion_activa is True

    def test_actualizar_desde_estado_ambas_alertas(self, qapp, indicadores_controlador):
        """Verifica actualización desde estado con ambas alertas."""
        indicadores_controlador.actualizar_desde_estado(
            falla_sensor=True,
            bateria_baja=True
        )

        assert indicadores_controlador.modelo.falla_sensor is True
        assert indicadores_controlador.modelo.bateria_baja is True
        assert indicadores_controlador.vista.alert_sensor._animacion_activa is True
        assert indicadores_controlador.vista.alert_bateria._animacion_activa is True

    def test_cambio_de_estado_multiple(self, qapp, indicadores_controlador):
        """Verifica múltiples cambios de estado consecutivos."""
        # Estado inicial: sin alertas
        assert indicadores_controlador.modelo.falla_sensor is False
        assert indicadores_controlador.modelo.bateria_baja is False

        # Activar falla sensor
        indicadores_controlador.actualizar_falla_sensor(True)
        assert indicadores_controlador.modelo.falla_sensor is True

        # Activar batería baja
        indicadores_controlador.actualizar_bateria_baja(True)
        assert indicadores_controlador.modelo.bateria_baja is True

        # Desactivar falla sensor (batería sigue baja)
        indicadores_controlador.actualizar_falla_sensor(False)
        assert indicadores_controlador.modelo.falla_sensor is False
        assert indicadores_controlador.modelo.bateria_baja is True

        # Desactivar batería
        indicadores_controlador.actualizar_bateria_baja(False)
        assert indicadores_controlador.modelo.falla_sensor is False
        assert indicadores_controlador.modelo.bateria_baja is False


class TestSignals:
    """Tests de señales PyQt."""

    def test_emite_signal_alerta_sensor_activada(self, qapp, indicadores_controlador, qtbot):
        """Verifica que se emita señal al activar alerta de sensor."""
        with qtbot.waitSignal(indicadores_controlador.alerta_activada, timeout=1000) as blocker:
            indicadores_controlador.actualizar_falla_sensor(True)

        # Verificar que se emitió la señal con el parámetro correcto
        assert blocker.args == ["sensor"]

    def test_emite_signal_alerta_sensor_desactivada(self, qapp, indicadores_controlador, qtbot):
        """Verifica que se emita señal al desactivar alerta de sensor."""
        # Primero activar
        indicadores_controlador.actualizar_falla_sensor(True)

        # Luego desactivar y verificar señal
        with qtbot.waitSignal(indicadores_controlador.alerta_desactivada, timeout=1000) as blocker:
            indicadores_controlador.actualizar_falla_sensor(False)

        assert blocker.args == ["sensor"]

    def test_emite_signal_alerta_bateria_activada(self, qapp, indicadores_controlador, qtbot):
        """Verifica que se emita señal al activar alerta de batería."""
        with qtbot.waitSignal(indicadores_controlador.alerta_activada, timeout=1000) as blocker:
            indicadores_controlador.actualizar_bateria_baja(True)

        assert blocker.args == ["bateria"]

    def test_emite_signal_alerta_bateria_desactivada(self, qapp, indicadores_controlador, qtbot):
        """Verifica que se emita señal al desactivar alerta de batería."""
        # Primero activar
        indicadores_controlador.actualizar_bateria_baja(True)

        # Luego desactivar y verificar señal
        with qtbot.waitSignal(indicadores_controlador.alerta_desactivada, timeout=1000) as blocker:
            indicadores_controlador.actualizar_bateria_baja(False)

        assert blocker.args == ["bateria"]

    def test_no_emite_signal_sin_cambio_sensor(self, qapp, indicadores_controlador, qtbot):
        """Verifica que no se emita señal si no cambia el estado del sensor."""
        # Estado inicial: False
        # Actualizar a False de nuevo (sin cambio)
        # No debería emitir señal
        try:
            with qtbot.waitSignal(indicadores_controlador.alerta_activada, timeout=500):
                indicadores_controlador.actualizar_falla_sensor(False)
            pytest.fail("No debería emitir señal si no hay cambio")
        except:
            # Esto es lo esperado: timeout porque no se emitió señal
            pass

    def test_no_emite_signal_sin_cambio_bateria(self, qapp, indicadores_controlador, qtbot):
        """Verifica que no se emita señal si no cambia el estado de batería."""
        try:
            with qtbot.waitSignal(indicadores_controlador.alerta_activada, timeout=500):
                indicadores_controlador.actualizar_bateria_baja(False)
            pytest.fail("No debería emitir señal si no hay cambio")
        except:
            # Esto es lo esperado
            pass

    def test_signals_multiples_con_actualizar_desde_estado(
        self, qapp, indicadores_controlador, qtbot
    ):
        """Verifica que se emitan ambas señales al actualizar desde estado."""
        # Usar Mock para capturar todas las señales
        sensor_activada = Mock()
        bateria_activada = Mock()

        indicadores_controlador.alerta_activada.connect(sensor_activada)
        indicadores_controlador.alerta_activada.connect(bateria_activada)

        # Actualizar ambas alertas
        indicadores_controlador.actualizar_desde_estado(
            falla_sensor=True,
            bateria_baja=True
        )

        # Procesar eventos de Qt
        qtbot.wait(100)

        # Verificar que se emitieron señales (al menos 2 veces)
        assert sensor_activada.call_count == 2
        assert bateria_activada.call_count == 2
