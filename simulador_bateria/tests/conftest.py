"""Configuración de pytest para el Simulador de Batería.

Provee fixtures globales compartidas por todos los tests.
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Setup PYTHONPATH para imports
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


# ============================================================================
# FIXTURES NIVEL 1: CONFIGURACIÓN BASE
# ============================================================================

@pytest.fixture
def config():
    """ConfigSimuladorBateria con valores de test."""
    from app.configuracion.config import ConfigSimuladorBateria
    return ConfigSimuladorBateria(
        host="127.0.0.1",
        puerto=11000,
        intervalo_envio_ms=100,
        voltaje_minimo=10.0,
        voltaje_maximo=15.0,
        voltaje_inicial=12.0
    )


# ============================================================================
# FIXTURES NIVEL 2: MOCK DE DEPENDENCIAS EXTERNAS
# ============================================================================

@pytest.fixture
def mock_ephemeral_client(qtbot):
    """Mock completo de EphemeralSocketClient.

    Configura comportamiento default para send y send_async.
    Usa signals PyQt6 reales para permitir emisión y conexión.
    """
    from PyQt6.QtCore import QObject, pyqtSignal

    class MockEphemeralClient(QObject):
        """Mock con signals PyQt6 reales."""
        data_sent = pyqtSignal()
        error_occurred = pyqtSignal(str)

        def __init__(self):
            super().__init__()
            self.send = MagicMock(return_value=True)
            self.send_async = MagicMock(return_value=None)

    with patch('app.comunicacion.cliente_bateria.EphemeralSocketClient') as mock_class:
        mock_instance = MockEphemeralClient()
        mock_class.return_value = mock_instance
        yield mock_instance


# ============================================================================
# FIXTURES NIVEL 3: COMPONENTES DE DOMINIO
# ============================================================================

@pytest.fixture
def generador(config, qtbot):
    """GeneradorBateria con config de test."""
    from app.dominio.generador_bateria import GeneradorBateria
    return GeneradorBateria(config)


@pytest.fixture
def estado_bateria():
    """EstadoBateria de ejemplo."""
    from app.dominio.estado_bateria import EstadoBateria
    return EstadoBateria(voltaje=12.5)


# ============================================================================
# FIXTURES NIVEL 4: COMPONENTES DE COMUNICACIÓN
# ============================================================================

@pytest.fixture
def mock_cliente(mock_ephemeral_client, qtbot):
    """ClienteBateria con EphemeralSocketClient mockeado."""
    with patch('app.comunicacion.cliente_bateria.EphemeralSocketClient') as mock_class:
        mock_class.return_value = mock_ephemeral_client
        from app.comunicacion.cliente_bateria import ClienteBateria
        return ClienteBateria("127.0.0.1", 11000)


# ============================================================================
# FIXTURES NIVEL 5: SERVICIOS
# ============================================================================

@pytest.fixture
def servicio(generador, mock_cliente, qtbot):
    """ServicioEnvioBateria con generador y cliente mockeado."""
    from app.comunicacion.servicio_envio import ServicioEnvioBateria
    return ServicioEnvioBateria(generador, mock_cliente)
