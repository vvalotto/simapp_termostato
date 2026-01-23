"""
Tests unitarios para ServidorEstado.

Verifica que el servidor recibe JSON del RPi, lo parsea correctamente
y emite señales PyQt apropiadas.
"""
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest
from PyQt6.QtCore import QObject

from app.comunicacion import ServidorEstado
from app.dominio import EstadoTermostato


# --- Fixtures ---

@pytest.fixture
def servidor(qapp):
    """Crea una instancia de ServidorEstado para tests."""
    servidor = ServidorEstado("127.0.0.1", 14001)
    yield servidor
    if servidor.is_running():
        servidor.detener()


@pytest.fixture
def json_estado_valido():
    """JSON válido de estado del termostato."""
    return {
        "temperatura_actual": 22.5,
        "temperatura_deseada": 24.0,
        "modo_climatizador": "calentando",
        "falla_sensor": False,
        "bateria_baja": False,
        "encendido": True,
        "modo_display": "ambiente",
        "timestamp": "2026-01-23T10:30:00Z"
    }


@pytest.fixture
def mensaje_json_valido(json_estado_valido):
    """Mensaje JSON como string (formato recibido del socket)."""
    return json.dumps(json_estado_valido) + "\n"


# --- Tests de Creación ---

class TestCreacion:
    """Tests de inicialización del servidor."""

    def test_creacion_con_defaults(self, qapp):
        """Verifica que se puede crear servidor con valores por defecto."""
        servidor = ServidorEstado()

        assert servidor.host == "0.0.0.0"
        assert servidor.port == 14001
        assert not servidor.esta_activo()

    def test_creacion_con_parametros(self, qapp):
        """Verifica que se puede crear servidor con parámetros custom."""
        servidor = ServidorEstado("192.168.1.50", 15000)

        assert servidor.host == "192.168.1.50"
        assert servidor.port == 15000
        assert not servidor.esta_activo()

    def test_senales_definidas(self, servidor):
        """Verifica que todas las señales PyQt están definidas."""
        assert hasattr(servidor, 'estado_recibido')
        assert hasattr(servidor, 'conexion_establecida')
        assert hasattr(servidor, 'conexion_perdida')
        assert hasattr(servidor, 'error_parsing')


# --- Tests de Recepción JSON ---

class TestRecepcionJSON:
    """Tests de parseo de mensajes JSON válidos."""

    def test_procesa_json_valido(self, servidor, mensaje_json_valido, qtbot):
        """Verifica que procesa JSON válido y emite estado_recibido."""
        # Conectar señal para capturar emisión
        with qtbot.waitSignal(servidor.estado_recibido, timeout=1000) as blocker:
            servidor._procesar_mensaje(mensaje_json_valido)

        # Verificar que emitió señal con EstadoTermostato correcto
        estado = blocker.args[0]
        assert isinstance(estado, EstadoTermostato)
        assert estado.temperatura_actual == 22.5
        assert estado.temperatura_deseada == 24.0
        assert estado.modo_climatizador == "calentando"
        assert not estado.falla_sensor
        assert not estado.bateria_baja
        assert estado.encendido
        assert estado.modo_display == "ambiente"

    def test_procesa_temperatura_actual_variada(self, servidor, qtbot):
        """Verifica que procesa diferentes valores de temperatura actual."""
        temperaturas = [20.0, 25.5, 18.3, 30.0]

        for temp in temperaturas:
            json_data = {
                "temperatura_actual": temp,
                "temperatura_deseada": 24.0,
                "modo_climatizador": "reposo",
                "falla_sensor": False,
                "bateria_baja": False,
                "encendido": True,
                "modo_display": "ambiente",
                "timestamp": "2026-01-23T10:30:00Z"
            }
            mensaje = json.dumps(json_data)

            with qtbot.waitSignal(servidor.estado_recibido) as blocker:
                servidor._procesar_mensaje(mensaje)

            estado = blocker.args[0]
            assert estado.temperatura_actual == temp

    def test_procesa_todos_los_modos_climatizador(self, servidor, qtbot):
        """Verifica que procesa todos los modos de climatizador válidos."""
        modos = ["calentando", "enfriando", "reposo", "apagado"]

        for modo in modos:
            json_data = {
                "temperatura_actual": 22.0,
                "temperatura_deseada": 24.0,
                "modo_climatizador": modo,
                "falla_sensor": False,
                "bateria_baja": False,
                "encendido": True,
                "modo_display": "ambiente",
                "timestamp": "2026-01-23T10:30:00Z"
            }
            mensaje = json.dumps(json_data)

            with qtbot.waitSignal(servidor.estado_recibido) as blocker:
                servidor._procesar_mensaje(mensaje)

            estado = blocker.args[0]
            assert estado.modo_climatizador == modo


# --- Tests de Errores JSON ---

class TestErroresJSON:
    """Tests de manejo de errores en mensajes JSON."""

    def test_json_malformado_emite_error_parsing(self, servidor, qtbot):
        """Verifica que JSON malformado emite error_parsing."""
        mensaje_invalido = "{esto no es JSON válido"

        with qtbot.waitSignal(servidor.error_parsing, timeout=1000) as blocker:
            servidor._procesar_mensaje(mensaje_invalido)

        # Verificar que emitió error con mensaje apropiado
        error_msg = blocker.args[0]
        assert "JSON malformado" in error_msg

    def test_json_sin_campo_requerido_emite_error(self, servidor, qtbot):
        """Verifica que JSON sin campo requerido emite error_parsing."""
        json_incompleto = {
            "temperatura_actual": 22.5,
            # Falta temperatura_deseada
            "modo_climatizador": "reposo",
            "timestamp": "2026-01-23T10:30:00Z"
        }
        mensaje = json.dumps(json_incompleto)

        with qtbot.waitSignal(servidor.error_parsing, timeout=1000) as blocker:
            servidor._procesar_mensaje(mensaje)

        error_msg = blocker.args[0]
        assert "faltante" in error_msg.lower() or "KeyError" in error_msg

    def test_temperatura_fuera_de_rango_emite_error(self, servidor, qtbot):
        """Verifica que temperatura fuera de rango emite error_parsing."""
        json_temp_invalida = {
            "temperatura_actual": 999.0,  # Fuera de rango -40 a 85
            "temperatura_deseada": 24.0,
            "modo_climatizador": "reposo",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": "2026-01-23T10:30:00Z"
        }
        mensaje = json.dumps(json_temp_invalida)

        with qtbot.waitSignal(servidor.error_parsing, timeout=1000) as blocker:
            servidor._procesar_mensaje(mensaje)

        error_msg = blocker.args[0]
        assert "validar" in error_msg.lower() or "rango" in error_msg.lower()

    def test_modo_climatizador_invalido_emite_error(self, servidor, qtbot):
        """Verifica que modo climatizador inválido emite error_parsing."""
        json_modo_invalido = {
            "temperatura_actual": 22.5,
            "temperatura_deseada": 24.0,
            "modo_climatizador": "modo_inexistente",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": "2026-01-23T10:30:00Z"
        }
        mensaje = json.dumps(json_modo_invalido)

        with qtbot.waitSignal(servidor.error_parsing, timeout=1000) as blocker:
            servidor._procesar_mensaje(mensaje)

        error_msg = blocker.args[0]
        assert "validar" in error_msg.lower() or "inválido" in error_msg.lower()


# --- Tests de Señales de Conexión ---

class TestSenalesConexion:
    """Tests de señales de conexión/desconexión."""

    def test_conexion_establecida_emite_senal(self, servidor, qtbot):
        """Verifica que _on_cliente_conectado emite conexion_establecida."""
        direccion = "192.168.1.50:54321"

        with qtbot.waitSignal(servidor.conexion_establecida, timeout=1000) as blocker:
            servidor._on_cliente_conectado(direccion)

        assert blocker.args[0] == direccion

    def test_conexion_perdida_emite_senal(self, servidor, qtbot):
        """Verifica que _on_cliente_desconectado emite conexion_perdida."""
        direccion = "192.168.1.50:54321"

        with qtbot.waitSignal(servidor.conexion_perdida, timeout=1000) as blocker:
            servidor._on_cliente_desconectado(direccion)

        assert blocker.args[0] == direccion

    def test_senales_funcionan_correctamente(self, servidor, qtbot):
        """Verifica que las señales de BaseSocketServer están conectadas y funcionan."""
        # Test que data_received dispara _procesar_mensaje
        json_data = {
            "temperatura_actual": 22.0,
            "temperatura_deseada": 24.0,
            "modo_climatizador": "reposo",
            "falla_sensor": False,
            "bateria_baja": False,
            "encendido": True,
            "modo_display": "ambiente",
            "timestamp": "2026-01-23T10:30:00Z"
        }
        mensaje = json.dumps(json_data)

        # Emitir data_received debe disparar estado_recibido
        with qtbot.waitSignal(servidor.estado_recibido, timeout=1000):
            servidor.data_received.emit(mensaje)


# --- Tests de Lifecycle ---

class TestLifecycle:
    """Tests del ciclo de vida del servidor (iniciar/detener)."""

    def test_iniciar_servidor(self, qapp):
        """Verifica que se puede iniciar el servidor."""
        servidor = ServidorEstado("127.0.0.1", 14099)  # Puerto único para test

        try:
            exito = servidor.iniciar()
            assert exito
            assert servidor.esta_activo()
        finally:
            servidor.detener()

    def test_detener_servidor(self, qapp):
        """Verifica que se puede detener el servidor."""
        servidor = ServidorEstado("127.0.0.1", 14098)  # Puerto único

        servidor.iniciar()
        assert servidor.esta_activo()

        servidor.detener()
        assert not servidor.esta_activo()

    def test_detener_servidor_no_iniciado_no_falla(self, servidor):
        """Verifica que detener un servidor no iniciado no causa error."""
        assert not servidor.esta_activo()
        servidor.detener()  # No debe fallar
        assert not servidor.esta_activo()


# --- Tests de Robustez ---

class TestRobustez:
    """Tests de casos edge y robustez."""

    def test_json_con_whitespace_se_procesa(self, servidor, json_estado_valido, qtbot):
        """Verifica que JSON con espacios/tabs se procesa correctamente."""
        mensaje = "  \n" + json.dumps(json_estado_valido) + "  \n"

        with qtbot.waitSignal(servidor.estado_recibido, timeout=1000) as blocker:
            servidor._procesar_mensaje(mensaje)

        estado = blocker.args[0]
        assert estado.temperatura_actual == 22.5

    def test_multiples_mensajes_consecutivos(self, servidor, json_estado_valido, qtbot):
        """Verifica que puede procesar múltiples mensajes consecutivos."""
        temperaturas = [20.0, 21.5, 23.0]

        for temp in temperaturas:
            json_data = {**json_estado_valido, "temperatura_actual": temp}
            mensaje = json.dumps(json_data)

            with qtbot.waitSignal(servidor.estado_recibido) as blocker:
                servidor._procesar_mensaje(mensaje)

            estado = blocker.args[0]
            assert estado.temperatura_actual == temp
