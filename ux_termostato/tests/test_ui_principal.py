"""
Tests unitarios para VentanaPrincipalUX.

Este módulo contiene los tests que validan el comportamiento de la ventana
principal, incluyendo ciclo de vida, integración de componentes y manejo de errores.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget

from app.presentacion.ui_principal import VentanaPrincipalUX
from app.configuracion import ConfigUX
from app.factory import ComponenteFactoryUX


class TestCreacion:
    """Tests de creación de la ventana principal."""

    def test_crear_ventana_exitoso(self, qapp, factory_ux):
        """
        Test: Crear ventana correctamente con factory.

        Given: Factory configurada
        When: Se crea VentanaPrincipalUX
        Then: La ventana se crea sin errores
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana is not None
        assert isinstance(ventana, VentanaPrincipalUX)

    def test_ventana_tiene_factory(self, qapp, factory_ux):
        """
        Test: La ventana almacena referencia a la factory.

        Given: Se crea ventana con factory
        When: Se accede al atributo _factory
        Then: La factory está almacenada correctamente
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana._factory is factory_ux

    def test_componentes_creados(self, qapp, factory_ux):
        """
        Test: Los componentes se crean durante la inicialización.

        Given: Factory con paneles
        When: Se crea la ventana
        Then: Los componentes están creados y almacenados
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana._componentes is not None
        assert len(ventana._componentes) == 8
        assert "display" in ventana._componentes
        assert "power" in ventana._componentes

    def test_servidor_creado(self, qapp, factory_ux):
        """
        Test: El servidor de estado se crea.

        Given: Factory configurada
        When: Se crea la ventana
        Then: ServidorEstado está creado
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana._servidor_estado is not None

    def test_cliente_creado(self, qapp, factory_ux):
        """
        Test: El cliente de comandos se crea.

        Given: Factory configurada
        When: Se crea la ventana
        Then: ClienteComandos está creado
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana._cliente_comandos is not None


class TestConfiguracion:
    """Tests de configuración de la ventana."""

    def test_titulo_ventana(self, qapp, factory_ux):
        """
        Test: La ventana tiene el título correcto.

        Given: Ventana creada
        When: Se verifica el título
        Then: El título es "UX Termostato Desktop"
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana.windowTitle() == "UX Termostato Desktop"

    def test_tamano_ventana(self, qapp, factory_ux):
        """
        Test: La ventana tiene el tamaño inicial correcto.

        Given: Ventana creada
        When: Se verifica el tamaño
        Then: El tamaño es 600x800
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana.width() == 600
        assert ventana.height() == 800

    def test_tamano_minimo(self, qapp, factory_ux):
        """
        Test: La ventana tiene tamaño mínimo configurado.

        Given: Ventana creada
        When: Se verifica el tamaño mínimo
        Then: El tamaño mínimo es 500x700
        """
        ventana = VentanaPrincipalUX(factory_ux)

        min_size = ventana.minimumSize()
        assert min_size.width() == 500
        assert min_size.height() == 700

    def test_tema_oscuro_aplicado(self, qapp, factory_ux):
        """
        Test: El tema oscuro está aplicado.

        Given: Ventana creada
        When: Se verifica el stylesheet
        Then: Tiene stylesheet aplicado
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana.styleSheet() != ""
        assert len(ventana.styleSheet()) > 0


class TestCoordinator:
    """Tests de integración con coordinator."""

    def test_coordinator_creado(self, qapp, factory_ux):
        """
        Test: El coordinator se crea correctamente.

        Given: Ventana creada
        When: Se verifica el coordinator
        Then: El coordinator está creado
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana._coordinator is not None

    def test_coordinator_recibe_paneles(self, qapp, factory_ux):
        """
        Test: El coordinator recibe todos los paneles.

        Given: Ventana con paneles
        When: Se crea el coordinator
        Then: El coordinator tiene acceso a los paneles
        """
        ventana = VentanaPrincipalUX(factory_ux)

        # Verificar que el coordinator existe y tiene paneles
        assert ventana._coordinator is not None
        assert hasattr(ventana._coordinator, '_paneles')
        assert len(ventana._coordinator._paneles) == 8


class TestUI:
    """Tests de ensamblado de la interfaz."""

    def test_compositor_creado(self, qapp, factory_ux):
        """
        Test: El compositor se crea.

        Given: Ventana creada
        When: Se verifica el compositor
        Then: El compositor está creado
        """
        ventana = VentanaPrincipalUX(factory_ux)

        assert ventana._compositor is not None

    def test_central_widget_establecido(self, qapp, factory_ux):
        """
        Test: El widget central está establecido.

        Given: Ventana creada
        When: Se verifica el central widget
        Then: Tiene un widget central válido
        """
        ventana = VentanaPrincipalUX(factory_ux)

        central = ventana.centralWidget()
        assert central is not None
        assert isinstance(central, QWidget)

    def test_central_widget_tiene_layout(self, qapp, factory_ux):
        """
        Test: El widget central tiene un layout.

        Given: Ventana creada
        When: Se verifica el layout del central widget
        Then: Tiene un layout válido
        """
        ventana = VentanaPrincipalUX(factory_ux)

        central = ventana.centralWidget()
        assert central.layout() is not None


class TestCicloDeVida:
    """Tests del ciclo de vida (iniciar/cerrar)."""

    def test_iniciar_muestra_ventana(self, qapp, factory_ux):
        """
        Test: El método iniciar() muestra la ventana.

        Given: Ventana creada pero no mostrada
        When: Se llama a iniciar()
        Then: La ventana se muestra
        """
        ventana = VentanaPrincipalUX(factory_ux)
        assert not ventana.isVisible()

        ventana.iniciar()

        assert ventana.isVisible()

    def test_iniciar_retorna_self(self, qapp, factory_ux):
        """
        Test: El método iniciar() retorna self para chaining.

        Given: Ventana creada
        When: Se llama a iniciar()
        Then: Retorna la misma instancia
        """
        ventana = VentanaPrincipalUX(factory_ux)

        resultado = ventana.iniciar()

        assert resultado is ventana

    def test_iniciar_inicia_servidor(self, qapp, factory_ux):
        """
        Test: El método iniciar() inicia el servidor.

        Given: Ventana creada con servidor
        When: Se llama a iniciar()
        Then: El servidor se inicia
        """
        ventana = VentanaPrincipalUX(factory_ux)
        servidor_mock = Mock()
        ventana._servidor_estado = servidor_mock

        ventana.iniciar()

        servidor_mock.start.assert_called_once()

    def test_cerrar_detiene_servidor(self, qapp, factory_ux):
        """
        Test: El método cerrar() detiene el servidor.

        Given: Ventana iniciada
        When: Se llama a cerrar()
        Then: El servidor se detiene
        """
        ventana = VentanaPrincipalUX(factory_ux)
        servidor_mock = Mock()
        ventana._servidor_estado = servidor_mock

        ventana.cerrar()

        # Verificar que stop fue llamado al menos una vez
        assert servidor_mock.stop.called
        assert servidor_mock.stop.call_count >= 1

    def test_close_event_llama_cerrar(self, qapp, factory_ux):
        """
        Test: closeEvent() llama al método cerrar().

        Given: Ventana creada
        When: Se recibe un evento de cierre
        Then: Se llama a cerrar() y se acepta el evento
        """
        ventana = VentanaPrincipalUX(factory_ux)
        ventana.cerrar = Mock()  # Mock del método cerrar

        # Simular evento de cierre
        event = Mock()
        ventana.closeEvent(event)

        ventana.cerrar.assert_called_once()
        event.accept.assert_called_once()


class TestManejoErrores:
    """Tests de manejo de errores."""

    def test_error_crear_componentes_lanza_runtime_error(self, qapp):
        """
        Test: Error al crear componentes lanza RuntimeError.

        Given: Factory que falla al crear paneles
        When: Se intenta crear la ventana
        Then: Lanza RuntimeError
        """
        factory_mock = Mock()
        factory_mock.crear_todos_paneles.side_effect = Exception("Error de prueba")
        factory_mock.config = Mock()

        with pytest.raises(RuntimeError, match="Error crítico al crear componentes"):
            VentanaPrincipalUX(factory_mock)

    def test_error_iniciar_muestra_dialogo(self, qapp, factory_ux):
        """
        Test: Error al iniciar muestra diálogo de error.

        Given: Ventana con servidor que falla al iniciar
        When: Se llama a iniciar()
        Then: Se muestra QMessageBox y se lanza RuntimeError
        """
        ventana = VentanaPrincipalUX(factory_ux)
        servidor_mock = Mock()
        servidor_mock.start.side_effect = Exception("Error de servidor")
        ventana._servidor_estado = servidor_mock

        with patch('app.presentacion.ui_principal.QMessageBox.critical'):
            with pytest.raises(RuntimeError, match="Error al iniciar aplicación"):
                ventana.iniciar()

    def test_cerrar_maneja_errores_gracefully(self, qapp, factory_ux):
        """
        Test: cerrar() maneja errores sin lanzar excepción.

        Given: Ventana con servidor que falla al detener
        When: Se llama a cerrar()
        Then: No lanza excepción, solo loguea
        """
        ventana = VentanaPrincipalUX(factory_ux)
        servidor_mock = Mock()
        servidor_mock.stop.side_effect = Exception("Error al detener")
        ventana._servidor_estado = servidor_mock

        # No debería lanzar excepción
        ventana.cerrar()

        # Verificar que intentó detener el servidor al menos una vez
        assert servidor_mock.stop.called
        assert servidor_mock.stop.call_count >= 1


class TestIntegracion:
    """Tests de integración completa."""

    def test_ventana_completa_funcional(self, qapp, factory_ux, qtbot):
        """
        Test: La ventana completa es funcional.

        Given: Factory configurada
        When: Se crea, inicia y muestra la ventana
        Then: Todo funciona sin errores
        """
        ventana = VentanaPrincipalUX(factory_ux)
        qtbot.addWidget(ventana)

        # Iniciar
        ventana.iniciar()

        # Verificaciones
        assert ventana.isVisible()
        assert ventana.centralWidget() is not None
        assert ventana._coordinator is not None
        assert ventana._servidor_estado is not None
