"""
Tests unitarios para ControlTempVista.

Valida la creación, actualización y estilos de la vista del panel
de control de temperatura.
"""

import pytest

from app.presentacion.paneles.control_temp.modelo import ControlTempModelo
from app.presentacion.paneles.control_temp.vista import ControlTempVista


class TestCreacion:
    """Tests de creación e inicialización de ControlTempVista."""

    def test_crear_vista(self, qapp):
        """Test que ControlTempVista se crea correctamente."""
        vista = ControlTempVista()

        assert vista is not None
        assert isinstance(vista, ControlTempVista)

    def test_vista_tiene_boton_subir(self, qapp):
        """Test que la vista tiene botón SUBIR."""
        vista = ControlTempVista()

        assert hasattr(vista, "btn_subir")
        assert vista.btn_subir is not None
        assert "SUBIR" in vista.btn_subir.text()

    def test_vista_tiene_boton_bajar(self, qapp):
        """Test que la vista tiene botón BAJAR."""
        vista = ControlTempVista()

        assert hasattr(vista, "btn_bajar")
        assert vista.btn_bajar is not None
        assert "BAJAR" in vista.btn_bajar.text()

    def test_vista_tiene_label_temperatura(self, qapp):
        """Test que la vista tiene label de temperatura."""
        vista = ControlTempVista()

        assert hasattr(vista, "label_temp")
        assert vista.label_temp is not None

    def test_vista_tiene_label_titulo(self, qapp):
        """Test que la vista tiene label de título."""
        vista = ControlTempVista()

        assert hasattr(vista, "label_titulo")
        assert vista.label_titulo is not None
        assert "Control de Temperatura" in vista.label_titulo.text()

    def test_botones_tienen_tamano_minimo(self, qapp):
        """Test que los botones tienen tamaño mínimo configurado."""
        vista = ControlTempVista()

        assert vista.btn_subir.minimumHeight() == 80
        assert vista.btn_subir.minimumWidth() == 120
        assert vista.btn_bajar.minimumHeight() == 80
        assert vista.btn_bajar.minimumWidth() == 120

    def test_botones_tienen_cursor_pointer(self, qapp):
        """Test que los botones tienen cursor pointer configurado."""
        from PyQt6.QtCore import Qt

        vista = ControlTempVista()

        assert vista.btn_subir.cursor().shape() == Qt.CursorShape.PointingHandCursor
        assert vista.btn_bajar.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_botones_tienen_tooltips(self, qapp):
        """Test que los botones tienen tooltips informativos."""
        vista = ControlTempVista()

        assert vista.btn_subir.toolTip() == "Aumentar temperatura en 0.5°C"
        assert vista.btn_bajar.toolTip() == "Disminuir temperatura en 0.5°C"


class TestActualizacion:
    """Tests del método actualizar()."""

    def test_actualizar_con_modelo_habilitado(self, qapp):
        """Test que actualizar con modelo habilitado muestra temperatura."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=23.5, habilitado=True)

        vista.actualizar(modelo)

        assert "23.5°C" in vista.label_temp.text()

    def test_actualizar_con_modelo_deshabilitado(self, qapp):
        """Test que actualizar con modelo deshabilitado muestra guiones."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=23.5, habilitado=False)

        vista.actualizar(modelo)

        assert "--.-°C" in vista.label_temp.text()

    def test_actualizar_habilita_botones_cuando_puede(self, qapp):
        """Test que actualizar habilita botones cuando el modelo puede aumentar/disminuir."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is True
        assert vista.btn_bajar.isEnabled() is True

    def test_actualizar_deshabilita_botones_cuando_modelo_deshabilitado(self, qapp):
        """Test que actualizar deshabilita botones cuando el modelo está deshabilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is False
        assert vista.btn_bajar.isEnabled() is False

    def test_actualizar_deshabilita_subir_en_maximo(self, qapp):
        """Test que actualizar deshabilita SUBIR cuando alcanza el máximo."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=True)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is False
        assert vista.btn_bajar.isEnabled() is True

    def test_actualizar_deshabilita_bajar_en_minimo(self, qapp):
        """Test que actualizar deshabilita BAJAR cuando alcanza el mínimo."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=True)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is True
        assert vista.btn_bajar.isEnabled() is False

    def test_actualizar_multiple_veces(self, qapp):
        """Test que actualizar múltiples veces funciona correctamente."""
        vista = ControlTempVista()

        # Primera actualización
        modelo_1 = ControlTempModelo(temperatura_deseada=20.0, habilitado=True)
        vista.actualizar(modelo_1)
        assert "20.0°C" in vista.label_temp.text()

        # Segunda actualización
        modelo_2 = ControlTempModelo(temperatura_deseada=25.5, habilitado=True)
        vista.actualizar(modelo_2)
        assert "25.5°C" in vista.label_temp.text()

        # Tercera actualización (deshabilitado)
        modelo_3 = ControlTempModelo(temperatura_deseada=25.5, habilitado=False)
        vista.actualizar(modelo_3)
        assert "--.-°C" in vista.label_temp.text()


class TestEstilosSubir:
    """Tests de estilos del botón SUBIR."""

    def test_boton_subir_tiene_object_name(self, qapp):
        """Test que el botón SUBIR tiene objectName configurado."""
        vista = ControlTempVista()

        assert vista.btn_subir.objectName() == "btnSubir"

    def test_boton_subir_tiene_icono_flecha(self, qapp):
        """Test que el botón SUBIR tiene icono de flecha arriba."""
        vista = ControlTempVista()

        assert "▲" in vista.btn_subir.text()

    def test_boton_subir_tiene_stylesheet_cuando_habilitado(self, qapp):
        """Test que el botón SUBIR tiene stylesheet cuando está habilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        vista.actualizar(modelo)
        stylesheet = vista.btn_subir.styleSheet()

        # Verificar colores rojos
        assert "#dc2626" in stylesheet  # red-600
        assert vista.btn_subir.isEnabled() is True

    def test_boton_subir_tiene_stylesheet_cuando_deshabilitado(self, qapp):
        """Test que el botón SUBIR tiene stylesheet cuando está deshabilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)

        vista.actualizar(modelo)
        stylesheet = vista.btn_subir.styleSheet()

        # Verificar colores grises
        assert "#475569" in stylesheet  # slate-600
        assert vista.btn_subir.isEnabled() is False


class TestEstilosBajar:
    """Tests de estilos del botón BAJAR."""

    def test_boton_bajar_tiene_object_name(self, qapp):
        """Test que el botón BAJAR tiene objectName configurado."""
        vista = ControlTempVista()

        assert vista.btn_bajar.objectName() == "btnBajar"

    def test_boton_bajar_tiene_icono_flecha(self, qapp):
        """Test que el botón BAJAR tiene icono de flecha abajo."""
        vista = ControlTempVista()

        assert "▼" in vista.btn_bajar.text()

    def test_boton_bajar_tiene_stylesheet_cuando_habilitado(self, qapp):
        """Test que el botón BAJAR tiene stylesheet cuando está habilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        vista.actualizar(modelo)
        stylesheet = vista.btn_bajar.styleSheet()

        # Verificar colores azules
        assert "#2563eb" in stylesheet  # blue-600
        assert vista.btn_bajar.isEnabled() is True

    def test_boton_bajar_tiene_stylesheet_cuando_deshabilitado(self, qapp):
        """Test que el botón BAJAR tiene stylesheet cuando está deshabilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)

        vista.actualizar(modelo)
        stylesheet = vista.btn_bajar.styleSheet()

        # Verificar colores grises
        assert "#475569" in stylesheet  # slate-600
        assert vista.btn_bajar.isEnabled() is False


class TestEstadosLimite:
    """Tests de estados límite (máximo y mínimo)."""

    def test_solo_subir_deshabilitado_en_maximo(self, qapp):
        """Test que solo SUBIR está deshabilitado cuando alcanza el máximo."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=True)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is False
        assert vista.btn_bajar.isEnabled() is True

    def test_solo_bajar_deshabilitado_en_minimo(self, qapp):
        """Test que solo BAJAR está deshabilitado cuando alcanza el mínimo."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=True)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is True
        assert vista.btn_bajar.isEnabled() is False

    def test_ambos_deshabilitados_cuando_panel_deshabilitado(self, qapp):
        """Test que ambos botones están deshabilitados cuando el panel está deshabilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)

        vista.actualizar(modelo)

        assert vista.btn_subir.isEnabled() is False
        assert vista.btn_bajar.isEnabled() is False


class TestFormatoTemperatura:
    """Tests de formato de temperatura mostrada."""

    def test_temperatura_con_un_decimal(self, qapp):
        """Test que la temperatura se muestra con un decimal."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=23.5, habilitado=True)

        vista.actualizar(modelo)

        # Verificar formato X.X°C
        assert "23.5°C" in vista.label_temp.text()

    def test_temperatura_entera_muestra_decimal(self, qapp):
        """Test que temperatura entera muestra .0 al final."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        vista.actualizar(modelo)

        assert "22.0°C" in vista.label_temp.text()

    def test_temperatura_guiones_cuando_deshabilitado(self, qapp):
        """Test que muestra --.-°C cuando está deshabilitado."""
        vista = ControlTempVista()
        modelo = ControlTempModelo(temperatura_deseada=23.5, habilitado=False)

        vista.actualizar(modelo)

        assert "--.-°C" in vista.label_temp.text()


class TestLayoutYSpacing:
    """Tests de layout y espaciado de componentes."""

    def test_vista_tiene_layout_configurado(self, qapp):
        """Test que la vista tiene un layout configurado."""
        vista = ControlTempVista()

        assert vista.layout() is not None

    def test_label_titulo_tiene_texto_centrado(self, qapp):
        """Test que el label de título tiene texto centrado."""
        from PyQt6.QtCore import Qt

        vista = ControlTempVista()

        alignment = vista.label_titulo.alignment()
        assert alignment == Qt.AlignmentFlag.AlignCenter

    def test_label_temp_tiene_texto_centrado(self, qapp):
        """Test que el label de temperatura tiene texto centrado."""
        from PyQt6.QtCore import Qt

        vista = ControlTempVista()

        alignment = vista.label_temp.alignment()
        assert alignment == Qt.AlignmentFlag.AlignCenter
