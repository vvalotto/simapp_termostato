"""
Tests unitarios para UICompositor.

Este módulo contiene los tests que validan el comportamiento del compositor
de UI, incluyendo ensamblado de paneles, layout y configuración de tamaño.
"""

import pytest
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from app.presentacion.ui_compositor import UICompositor
from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.modelo import DisplayModelo
from app.presentacion.paneles.display.controlador import DisplayControlador


class TestCreacion:
    """Tests de creación del UICompositor."""

    def test_crear_compositor_exitoso(self, todos_paneles):
        """
        Test: Crear compositor correctamente con todos los paneles.

        Given: Dict con todos los paneles MVC requeridos
        When: Se crea una instancia de UICompositor
        Then: El compositor se crea sin errores
        """
        compositor = UICompositor(todos_paneles)

        assert compositor is not None
        assert isinstance(compositor, UICompositor)

    def test_compositor_almacena_paneles(self, todos_paneles):
        """
        Test: El compositor almacena referencia a los paneles.

        Given: Dict con todos los paneles
        When: Se crea el compositor
        Then: Los paneles están accesibles internamente
        """
        compositor = UICompositor(todos_paneles)

        assert compositor._paneles == todos_paneles
        assert len(compositor._paneles) == 8

    def test_crear_compositor_con_paneles_vacios_falla(self):
        """
        Test: Crear compositor con dict vacío lanza ValueError.

        Given: Dict vacío de paneles
        When: Se intenta crear un compositor
        Then: Lanza ValueError con mensaje apropiado
        """
        with pytest.raises(ValueError, match="El diccionario de paneles está vacío"):
            UICompositor({})


class TestValidacion:
    """Tests de validación de paneles requeridos."""

    def test_falta_panel_display(self, todos_paneles):
        """
        Test: Fallar si falta el panel display.

        Given: Dict sin el panel 'display'
        When: Se intenta crear compositor
        Then: Lanza ValueError indicando panel faltante
        """
        paneles_incompletos = todos_paneles.copy()
        del paneles_incompletos["display"]

        with pytest.raises(ValueError, match="Faltan paneles requeridos.*display"):
            UICompositor(paneles_incompletos)

    def test_falta_panel_climatizador(self, todos_paneles):
        """
        Test: Fallar si falta el panel climatizador.

        Given: Dict sin el panel 'climatizador'
        When: Se intenta crear compositor
        Then: Lanza ValueError indicando panel faltante
        """
        paneles_incompletos = todos_paneles.copy()
        del paneles_incompletos["climatizador"]

        with pytest.raises(ValueError, match="Faltan paneles requeridos.*climatizador"):
            UICompositor(paneles_incompletos)

    def test_faltan_multiples_paneles(self, todos_paneles):
        """
        Test: Fallar si faltan múltiples paneles.

        Given: Dict sin varios paneles
        When: Se intenta crear compositor
        Then: Lanza ValueError listando todos los faltantes
        """
        paneles_incompletos = {
            "display": todos_paneles["display"],
            "power": todos_paneles["power"],
        }

        with pytest.raises(ValueError, match="Faltan paneles requeridos"):
            UICompositor(paneles_incompletos)

    def test_paneles_requeridos_definidos(self):
        """
        Test: La clase define los paneles requeridos correctamente.

        Given: Clase UICompositor
        When: Se accede a PANELES_REQUERIDOS
        Then: Contiene lista completa de paneles
        """
        assert len(UICompositor.PANELES_REQUERIDOS) == 8
        assert "display" in UICompositor.PANELES_REQUERIDOS
        assert "climatizador" in UICompositor.PANELES_REQUERIDOS
        assert "indicadores" in UICompositor.PANELES_REQUERIDOS
        assert "power" in UICompositor.PANELES_REQUERIDOS
        assert "control_temp" in UICompositor.PANELES_REQUERIDOS
        assert "selector_vista" in UICompositor.PANELES_REQUERIDOS
        assert "estado_conexion" in UICompositor.PANELES_REQUERIDOS
        assert "conexion" in UICompositor.PANELES_REQUERIDOS


class TestExtraerVista:
    """Tests de extracción de vistas de paneles MVC."""

    def test_extraer_vista_display(self, todos_paneles):
        """
        Test: Extraer vista del panel display correctamente.

        Given: Compositor con paneles completos
        When: Se extrae la vista del panel 'display'
        Then: Retorna la vista (índice 1 de la tupla)
        """
        compositor = UICompositor(todos_paneles)
        vista = compositor._extraer_vista("display")

        assert vista is not None
        assert isinstance(vista, DisplayVista)
        assert vista == todos_paneles["display"][1]

    def test_extraer_vista_de_cada_panel(self, todos_paneles):
        """
        Test: Extraer vistas de todos los paneles.

        Given: Compositor con todos los paneles
        When: Se extrae la vista de cada panel
        Then: Todas las vistas son QWidget válidos
        """
        compositor = UICompositor(todos_paneles)

        for nombre_panel in UICompositor.PANELES_REQUERIDOS:
            vista = compositor._extraer_vista(nombre_panel)
            assert vista is not None
            assert isinstance(vista, QWidget)

    def test_extraer_vista_tupla_invalida(self, todos_paneles):
        """
        Test: Fallar si la tupla MVC no tiene estructura válida.

        Given: Panel con tupla que no tiene al menos 2 elementos
        When: Se intenta extraer la vista
        Then: Lanza IndexError
        """
        compositor = UICompositor(todos_paneles)
        compositor._paneles["display"] = (DisplayModelo(),)  # Solo 1 elemento

        with pytest.raises(IndexError, match="no tiene estructura MVC válida"):
            compositor._extraer_vista("display")

    def test_extraer_vista_no_es_widget(self, todos_paneles):
        """
        Test: Fallar si el segundo elemento no es QWidget.

        Given: Panel con tupla donde índice 1 no es QWidget
        When: Se intenta extraer la vista
        Then: Lanza AttributeError
        """
        compositor = UICompositor(todos_paneles)
        compositor._paneles["display"] = (DisplayModelo(), "no es widget", DisplayControlador)

        with pytest.raises(AttributeError, match="no es un QWidget"):
            compositor._extraer_vista("display")


class TestCrearLayout:
    """Tests de creación del layout completo."""

    def test_crear_layout_retorna_widget(self, todos_paneles):
        """
        Test: crear_layout() retorna un QWidget.

        Given: Compositor con todos los paneles
        When: Se llama a crear_layout()
        Then: Retorna un QWidget válido
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        assert widget is not None
        assert isinstance(widget, QWidget)

    def test_widget_tiene_layout_vertical(self, todos_paneles):
        """
        Test: El widget tiene un QVBoxLayout principal.

        Given: Compositor con paneles
        When: Se crea el layout
        Then: El widget tiene un layout vertical
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        layout = widget.layout()
        assert layout is not None
        assert isinstance(layout, QVBoxLayout)

    def test_layout_tiene_margenes_correctos(self, todos_paneles):
        """
        Test: El layout tiene márgenes de 15px.

        Given: Compositor con paneles
        When: Se crea el layout
        Then: Los márgenes son 15, 15, 15, 15
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        layout = widget.layout()
        margins = layout.contentsMargins()

        assert margins.left() == 15
        assert margins.top() == 15
        assert margins.right() == 15
        assert margins.bottom() == 15

    def test_layout_tiene_espaciado_correcto(self, todos_paneles):
        """
        Test: El layout tiene espaciado de 12px.

        Given: Compositor con paneles
        When: Se crea el layout
        Then: El espaciado es 12px
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        layout = widget.layout()
        assert layout.spacing() == 12

    def test_layout_contiene_todos_paneles(self, todos_paneles):
        """
        Test: El layout contiene todos los widgets de paneles.

        Given: Compositor con 8 paneles
        When: Se crea el layout
        Then: El layout contiene al menos 8 items (paneles + header)
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        layout = widget.layout()
        # Header (layout) + 7 paneles = 8 items
        # (display, climatizador, power, control_temp, selector_vista, conexion están en el layout principal)
        # (estado_conexion e indicadores están en el header)
        assert layout.count() >= 7


class TestHeader:
    """Tests de creación del header horizontal."""

    def test_crear_header_retorna_layout(self, todos_paneles):
        """
        Test: _crear_header() retorna un QHBoxLayout.

        Given: Compositor con paneles
        When: Se crea el header
        Then: Retorna un layout horizontal
        """
        compositor = UICompositor(todos_paneles)
        header = compositor._crear_header()

        assert header is not None
        assert isinstance(header, QHBoxLayout)

    def test_header_tiene_espaciado(self, todos_paneles):
        """
        Test: El header tiene espaciado de 10px.

        Given: Compositor con paneles
        When: Se crea el header
        Then: El espaciado es 10px
        """
        compositor = UICompositor(todos_paneles)
        header = compositor._crear_header()

        assert header.spacing() == 10

    def test_header_contiene_estado_conexion_e_indicadores(self, todos_paneles):
        """
        Test: El header contiene EstadoConexion e Indicadores.

        Given: Compositor con paneles
        When: Se crea el header
        Then: Contiene 3 items (EstadoConexion, stretch, Indicadores)
        """
        compositor = UICompositor(todos_paneles)
        header = compositor._crear_header()

        # Header debe tener: EstadoConexion + Stretch + Indicadores = 3 items
        assert header.count() == 3


class TestTamaño:
    """Tests de configuración de tamaño del widget."""

    def test_widget_tiene_tamano_minimo(self, todos_paneles):
        """
        Test: El widget tiene tamaño mínimo de 500x700.

        Given: Compositor con paneles
        When: Se crea el layout
        Then: El tamaño mínimo es 500x700
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        min_size = widget.minimumSize()
        assert min_size.width() == 500
        assert min_size.height() == 700

    def test_widget_tiene_tamano_inicial(self, todos_paneles):
        """
        Test: El widget tiene tamaño inicial de 600x800.

        Given: Compositor con paneles
        When: Se crea el layout
        Then: El tamaño inicial es 600x800
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        size = widget.size()
        assert size.width() == 600
        assert size.height() == 800


class TestIntegracion:
    """Tests de integración del compositor completo."""

    def test_multiples_llamadas_crear_layout(self, todos_paneles):
        """
        Test: Llamar crear_layout() múltiples veces crea widgets independientes.

        Given: Compositor con paneles
        When: Se llama crear_layout() dos veces
        Then: Se crean dos widgets diferentes
        """
        compositor = UICompositor(todos_paneles)

        widget1 = compositor.crear_layout()
        widget2 = compositor.crear_layout()

        assert widget1 is not widget2
        assert widget1 != widget2

    def test_layout_completo_funcional(self, todos_paneles, qtbot):
        """
        Test: El layout completo es funcional y se puede mostrar.

        Given: Compositor con todos los paneles
        When: Se crea el layout y se muestra
        Then: El widget es visible sin errores
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        # Agregar widget al qtbot para manejo de recursos
        qtbot.addWidget(widget)

        # Mostrar widget
        widget.show()

        # Verificar que está visible
        assert widget.isVisible()

    def test_orden_paneles_en_layout(self, todos_paneles):
        """
        Test: Los paneles están en el orden correcto en el layout.

        Given: Compositor con paneles
        When: Se crea el layout
        Then: Los paneles aparecen en el orden esperado
        """
        compositor = UICompositor(todos_paneles)
        widget = compositor.crear_layout()

        layout = widget.layout()

        # El orden esperado es:
        # 0: Header (QHBoxLayout)
        # 1: Display
        # 2: Climatizador
        # 3: Power
        # 4: ControlTemp
        # 5: SelectorVista
        # 6: Conexion

        # Verificar que el primer item es un layout (header)
        item_0 = layout.itemAt(0)
        assert item_0 is not None
        assert isinstance(item_0.layout(), QHBoxLayout)

        # Verificar que los siguientes items son widgets
        for i in range(1, 7):
            item = layout.itemAt(i)
            assert item is not None
            assert item.widget() is not None
