"""Tests para PanelEstadoVista.

Tests de UI usando qtbot para widgets Qt reales.
"""

import pytest

from app.presentacion.paneles.estado.vista import PanelEstadoVista, ConfigPanelEstadoVista
from app.presentacion.paneles.estado.modelo import EstadoBateriaPanelModelo


@pytest.fixture
def vista(qtbot):
    """Vista real para tests."""
    v = PanelEstadoVista()
    qtbot.addWidget(v)
    return v


@pytest.fixture
def modelo():
    """Modelo para tests."""
    return EstadoBateriaPanelModelo(
        voltaje_actual=2.5,
        porcentaje=50.0,
        conectado=True,
        envios_exitosos=10,
        envios_fallidos=2
    )


class TestPanelEstadoVistaCreacion:
    """Tests de inicializacion de la vista."""

    def test_creacion_sin_config(self, qtbot):
        """Vista se crea con config por defecto."""
        vista = PanelEstadoVista()
        qtbot.addWidget(vista)

        assert vista._config is not None
        assert vista._config.titulo == "Estado Bateria"

    def test_creacion_con_config(self, qtbot):
        """Vista acepta config personalizada."""
        config = ConfigPanelEstadoVista(titulo="Test Panel")
        vista = PanelEstadoVista(config=config)
        qtbot.addWidget(vista)

        assert vista._config.titulo == "Test Panel"

    def test_tiene_labels(self, vista):
        """Vista tiene todos los labels necesarios."""
        assert vista._label_voltaje is not None
        assert vista._label_porcentaje is not None
        assert vista._label_conexion is not None
        assert vista._label_contador is not None


class TestPanelEstadoVistaActualizar:
    """Tests de actualizar con modelo."""

    def test_actualizar_voltaje(self, vista, modelo):
        """actualizar muestra voltaje correcto."""
        modelo.voltaje_actual = 3.7

        vista.actualizar(modelo)

        assert "3.7V" in vista._label_voltaje.text()

    def test_actualizar_porcentaje(self, vista, modelo):
        """actualizar muestra porcentaje correcto."""
        modelo.porcentaje = 75.0

        vista.actualizar(modelo)

        assert "75%" in vista._label_porcentaje.text()

    def test_actualizar_conectado_true(self, vista, modelo):
        """actualizar muestra estado conectado."""
        modelo.conectado = True

        vista.actualizar(modelo)

        assert vista._config.texto_conectado in vista._label_conexion.text()

    def test_actualizar_conectado_false(self, vista, modelo):
        """actualizar muestra estado desconectado."""
        modelo.conectado = False

        vista.actualizar(modelo)

        assert vista._config.texto_desconectado in vista._label_conexion.text()

    def test_actualizar_contadores(self, vista, modelo):
        """actualizar muestra contadores correctos."""
        modelo.envios_exitosos = 15
        modelo.envios_fallidos = 3

        vista.actualizar(modelo)

        texto = vista._label_contador.text()
        assert "15" in texto
        assert "3" in texto

    def test_actualizar_ignora_modelo_invalido(self, vista):
        """actualizar ignora modelo de tipo incorrecto."""
        texto_original = vista._label_voltaje.text()

        vista.actualizar("no es un modelo")

        assert vista._label_voltaje.text() == texto_original


class TestPanelEstadoVistaMostrarSinDatos:
    """Tests de mostrar_sin_datos."""

    def test_mostrar_sin_datos_voltaje(self, vista):
        """mostrar_sin_datos muestra texto sin datos en voltaje."""
        vista.mostrar_sin_datos()

        assert vista._config.texto_sin_datos in vista._label_voltaje.text()

    def test_mostrar_sin_datos_porcentaje(self, vista):
        """mostrar_sin_datos muestra 0% en porcentaje."""
        vista.mostrar_sin_datos()

        assert "0%" in vista._label_porcentaje.text()
