"""
Tests unitarios para ControlTempControlador.

Valida la lógica de negocio, señales PyQt y comandos JSON del controlador
del panel de control de temperatura.
"""

import pytest
from datetime import datetime
from PyQt6.QtTest import QSignalSpy

from app.presentacion.paneles.control_temp.modelo import ControlTempModelo
from app.presentacion.paneles.control_temp.vista import ControlTempVista
from app.presentacion.paneles.control_temp.controlador import ControlTempControlador


class TestCreacion:
    """Tests de creación e inicialización de ControlTempControlador."""

    def test_crear_controlador(self, qapp):
        """Test que ControlTempControlador se crea correctamente."""
        modelo = ControlTempModelo()
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        assert controlador is not None
        assert isinstance(controlador, ControlTempControlador)

    def test_controlador_tiene_modelo(self, qapp):
        """Test que el controlador tiene referencia al modelo."""
        modelo = ControlTempModelo(temperatura_deseada=22.0)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        assert controlador.modelo == modelo
        assert controlador.modelo.temperatura_deseada == 22.0

    def test_controlador_tiene_vista(self, qapp):
        """Test que el controlador tiene referencia a la vista."""
        modelo = ControlTempModelo()
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        assert controlador.vista == vista

    def test_vista_renderiza_estado_inicial(self, qapp):
        """Test que la vista renderiza el estado inicial del modelo."""
        modelo = ControlTempModelo(temperatura_deseada=25.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # La vista debe mostrar la temperatura inicial
        assert "25.0°C" in vista.label_temp.text()

    def test_botones_conectados_a_metodos(self, qapp):
        """Test que los botones están conectados a los métodos del controlador."""
        modelo = ControlTempModelo()
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # Los clicks deben estar conectados (verificamos que existen los métodos)
        assert hasattr(controlador, "aumentar_temperatura")
        assert hasattr(controlador, "disminuir_temperatura")


class TestAumentarTemperatura:
    """Tests del método aumentar_temperatura()."""

    def test_aumentar_temperatura_incrementa_en_0_5(self, qapp):
        """Test que aumentar_temperatura incrementa en 0.5°C."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()

        assert controlador.modelo.temperatura_deseada == 22.5

    def test_aumentar_temperatura_actualiza_vista(self, qapp):
        """Test que aumentar_temperatura actualiza la vista."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()

        assert "22.5°C" in vista.label_temp.text()

    def test_aumentar_temperatura_no_funciona_cuando_deshabilitado(self, qapp):
        """Test que aumentar_temperatura no funciona cuando está deshabilitado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()

        # La temperatura no debe cambiar
        assert controlador.modelo.temperatura_deseada == 22.0

    def test_aumentar_temperatura_no_supera_maximo(self, qapp):
        """Test que aumentar_temperatura no supera el máximo de 35°C."""
        modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()

        # La temperatura debe seguir en 35°C
        assert controlador.modelo.temperatura_deseada == 35.0

    def test_aumentar_temperatura_multiples_veces(self, qapp):
        """Test que aumentar_temperatura funciona múltiples veces."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()  # 22.5
        controlador.aumentar_temperatura()  # 23.0
        controlador.aumentar_temperatura()  # 23.5

        assert controlador.modelo.temperatura_deseada == 23.5

    def test_aumentar_temperatura_desde_limite_inferior(self, qapp):
        """Test que aumentar_temperatura funciona desde el límite inferior."""
        modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()

        assert controlador.modelo.temperatura_deseada == 15.5


class TestDisminuirTemperatura:
    """Tests del método disminuir_temperatura()."""

    def test_disminuir_temperatura_decrementa_en_0_5(self, qapp):
        """Test que disminuir_temperatura decrementa en 0.5°C."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.disminuir_temperatura()

        assert controlador.modelo.temperatura_deseada == 21.5

    def test_disminuir_temperatura_actualiza_vista(self, qapp):
        """Test que disminuir_temperatura actualiza la vista."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.disminuir_temperatura()

        assert "21.5°C" in vista.label_temp.text()

    def test_disminuir_temperatura_no_funciona_cuando_deshabilitado(self, qapp):
        """Test que disminuir_temperatura no funciona cuando está deshabilitado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.disminuir_temperatura()

        # La temperatura no debe cambiar
        assert controlador.modelo.temperatura_deseada == 22.0

    def test_disminuir_temperatura_no_baja_de_minimo(self, qapp):
        """Test que disminuir_temperatura no baja del mínimo de 15°C."""
        modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.disminuir_temperatura()

        # La temperatura debe seguir en 15°C
        assert controlador.modelo.temperatura_deseada == 15.0

    def test_disminuir_temperatura_multiples_veces(self, qapp):
        """Test que disminuir_temperatura funciona múltiples veces."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.disminuir_temperatura()  # 21.5
        controlador.disminuir_temperatura()  # 21.0
        controlador.disminuir_temperatura()  # 20.5

        assert controlador.modelo.temperatura_deseada == 20.5

    def test_disminuir_temperatura_desde_limite_superior(self, qapp):
        """Test que disminuir_temperatura funciona desde el límite superior."""
        modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.disminuir_temperatura()

        assert controlador.modelo.temperatura_deseada == 34.5


class TestSignals:
    """Tests de señales PyQt emitidas."""

    def test_aumentar_emite_temperatura_cambiada(self, qapp, qtbot):
        """Test que aumentar_temperatura emite señal temperatura_cambiada."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # Crear spy para capturar señales
        spy = QSignalSpy(controlador.temperatura_cambiada)

        controlador.aumentar_temperatura()

        # Verificar que se emitió una señal
        assert len(spy) == 1
        # Verificar el valor emitido
        assert spy[0][0] == 22.5

    def test_disminuir_emite_temperatura_cambiada(self, qapp, qtbot):
        """Test que disminuir_temperatura emite señal temperatura_cambiada."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.temperatura_cambiada)

        controlador.disminuir_temperatura()

        assert len(spy) == 1
        assert spy[0][0] == 21.5

    def test_aumentar_emite_comando_enviado(self, qapp, qtbot):
        """Test que aumentar_temperatura emite señal comando_enviado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.comando_enviado)

        controlador.aumentar_temperatura()

        assert len(spy) == 1
        comando = spy[0][0]
        assert isinstance(comando, dict)
        assert comando["comando"] == "set_temp_deseada"
        assert comando["valor"] == 22.5

    def test_disminuir_emite_comando_enviado(self, qapp, qtbot):
        """Test que disminuir_temperatura emite señal comando_enviado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.comando_enviado)

        controlador.disminuir_temperatura()

        assert len(spy) == 1
        comando = spy[0][0]
        assert comando["comando"] == "set_temp_deseada"
        assert comando["valor"] == 21.5

    def test_no_emite_senales_cuando_deshabilitado(self, qapp, qtbot):
        """Test que no se emiten señales cuando está deshabilitado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy_temp = QSignalSpy(controlador.temperatura_cambiada)
        spy_cmd = QSignalSpy(controlador.comando_enviado)

        controlador.aumentar_temperatura()
        controlador.disminuir_temperatura()

        assert len(spy_temp) == 0
        assert len(spy_cmd) == 0


class TestComandoJSON:
    """Tests de generación de comando JSON."""

    def test_comando_json_estructura_basica(self, qapp):
        """Test que el comando JSON tiene la estructura correcta."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.comando_enviado)
        controlador.aumentar_temperatura()

        comando = spy[0][0]

        assert "comando" in comando
        assert "valor" in comando
        assert "timestamp" in comando

    def test_comando_json_valor_redondeado(self, qapp):
        """Test que el valor en el comando JSON está redondeado a 1 decimal."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.comando_enviado)
        controlador.aumentar_temperatura()

        comando = spy[0][0]

        # El valor debe ser float con 1 decimal
        assert comando["valor"] == 22.5
        assert isinstance(comando["valor"], (int, float))

    def test_comando_json_timestamp_formato_iso(self, qapp):
        """Test que el timestamp está en formato ISO 8601."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.comando_enviado)
        controlador.aumentar_temperatura()

        comando = spy[0][0]
        timestamp_str = comando["timestamp"]

        # Verificar que se puede parsear como datetime ISO
        timestamp = datetime.fromisoformat(timestamp_str)
        assert isinstance(timestamp, datetime)

    def test_comando_json_timestamp_reciente(self, qapp):
        """Test que el timestamp es reciente (menos de 1 segundo)."""
        from datetime import timedelta

        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        antes = datetime.now()
        spy = QSignalSpy(controlador.comando_enviado)
        controlador.aumentar_temperatura()
        despues = datetime.now()

        comando = spy[0][0]
        timestamp = datetime.fromisoformat(comando["timestamp"])

        # El timestamp debe estar entre antes y después
        assert antes <= timestamp <= despues + timedelta(seconds=1)


class TestSetHabilitado:
    """Tests del método set_habilitado()."""

    def test_set_habilitado_habilita_panel(self, qapp):
        """Test que set_habilitado(True) habilita el panel."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.set_habilitado(True)

        assert controlador.modelo.habilitado is True
        assert vista.btn_subir.isEnabled() is True
        assert vista.btn_bajar.isEnabled() is True

    def test_set_habilitado_deshabilita_panel(self, qapp):
        """Test que set_habilitado(False) deshabilita el panel."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.set_habilitado(False)

        assert controlador.modelo.habilitado is False
        assert vista.btn_subir.isEnabled() is False
        assert vista.btn_bajar.isEnabled() is False

    def test_set_habilitado_actualiza_vista(self, qapp):
        """Test que set_habilitado actualiza la vista correctamente."""
        modelo = ControlTempModelo(temperatura_deseada=23.5, habilitado=False)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # Inicialmente debe mostrar guiones
        assert "--.-°C" in vista.label_temp.text()

        # Al habilitar, debe mostrar la temperatura
        controlador.set_habilitado(True)
        assert "23.5°C" in vista.label_temp.text()


class TestSetTemperaturaActual:
    """Tests del método set_temperatura_actual()."""

    def test_set_temperatura_actual_actualiza_modelo(self, qapp):
        """Test que set_temperatura_actual actualiza el modelo."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.set_temperatura_actual(25.5)

        assert controlador.modelo.temperatura_deseada == 25.5

    def test_set_temperatura_actual_actualiza_vista(self, qapp):
        """Test que set_temperatura_actual actualiza la vista."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.set_temperatura_actual(28.0)

        assert "28.0°C" in vista.label_temp.text()

    def test_set_temperatura_actual_emite_senal(self, qapp, qtbot):
        """Test que set_temperatura_actual emite señal temperatura_cambiada."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.temperatura_cambiada)

        controlador.set_temperatura_actual(30.0)

        assert len(spy) == 1
        assert spy[0][0] == 30.0

    def test_set_temperatura_actual_no_emite_comando(self, qapp, qtbot):
        """Test que set_temperatura_actual NO emite comando_enviado (viene del servidor)."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        spy = QSignalSpy(controlador.comando_enviado)

        controlador.set_temperatura_actual(30.0)

        # NO debe emitir comando porque la actualización viene del servidor
        assert len(spy) == 0

    def test_set_temperatura_actual_valida_rango_maximo(self, qapp):
        """Test que set_temperatura_actual valida el rango máximo."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # Intentar establecer temperatura mayor al máximo
        controlador.set_temperatura_actual(40.0)

        # Debe quedar en el máximo permitido
        assert controlador.modelo.temperatura_deseada == 35.0

    def test_set_temperatura_actual_valida_rango_minimo(self, qapp):
        """Test que set_temperatura_actual valida el rango mínimo."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # Intentar establecer temperatura menor al mínimo
        controlador.set_temperatura_actual(10.0)

        # Debe quedar en el mínimo permitido
        assert controlador.modelo.temperatura_deseada == 15.0


class TestSecuencias:
    """Tests de secuencias de operaciones."""

    def test_secuencia_aumentar_y_disminuir(self, qapp):
        """Test de secuencia aumentar → disminuir → aumentar."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()  # 22.5
        assert controlador.modelo.temperatura_deseada == 22.5

        controlador.disminuir_temperatura()  # 22.0
        assert controlador.modelo.temperatura_deseada == 22.0

        controlador.aumentar_temperatura()  # 22.5
        assert controlador.modelo.temperatura_deseada == 22.5

    def test_secuencia_hasta_maximo_y_vuelta(self, qapp):
        """Test de secuencia subiendo hasta el máximo y bajando."""
        modelo = ControlTempModelo(temperatura_deseada=34.0, habilitado=True)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        controlador.aumentar_temperatura()  # 34.5
        controlador.aumentar_temperatura()  # 35.0
        controlador.aumentar_temperatura()  # Debe quedar en 35.0 (máximo alcanzado)

        assert controlador.modelo.temperatura_deseada == 35.0

        controlador.disminuir_temperatura()  # 34.5
        assert controlador.modelo.temperatura_deseada == 34.5

    def test_secuencia_habilitar_modificar_deshabilitar(self, qapp):
        """Test de secuencia habilitar → modificar → deshabilitar."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)
        vista = ControlTempVista()
        controlador = ControlTempControlador(modelo, vista)

        # Habilitar
        controlador.set_habilitado(True)
        assert controlador.modelo.habilitado is True

        # Modificar
        controlador.aumentar_temperatura()
        assert controlador.modelo.temperatura_deseada == 22.5

        # Deshabilitar
        controlador.set_habilitado(False)
        assert controlador.modelo.habilitado is False

        # Intentar modificar (no debe funcionar)
        controlador.aumentar_temperatura()
        assert controlador.modelo.temperatura_deseada == 22.5  # No cambió
