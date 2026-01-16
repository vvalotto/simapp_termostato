"""
Tests unitarios para ClimatizadorVista.

Este módulo contiene los tests que validan el comportamiento de la vista
del panel Climatizador, incluyendo widgets, estilos, animaciones y transiciones.
"""

import pytest

from app.presentacion.paneles.climatizador.modelo import (
    ClimatizadorModelo,
    MODO_CALENTANDO,
    MODO_ENFRIANDO,
    MODO_REPOSO,
    MODO_APAGADO,
)
from app.presentacion.paneles.climatizador.vista import ClimatizadorVista


class TestCreacion:
    """Tests de creación de la vista ClimatizadorVista."""

    def test_crear_vista(self, qapp):
        """
        Test: Crear vista sin errores.

        Given: Existe una instancia de QApplication
        When: Se crea una instancia de ClimatizadorVista
        Then: La vista se crea correctamente
        """
        vista = ClimatizadorVista()

        assert vista is not None
        assert vista.objectName() == "panelClimatizador"

    def test_widgets_indicadores_existen(self, qapp):
        """
        Test: Los 3 widgets indicadores existen.

        Given: Se crea una ClimatizadorVista
        When: Se accede a los atributos de indicadores
        Then: Los 3 indicadores están presentes
        """
        vista = ClimatizadorVista()

        assert hasattr(vista, 'indicador_calor')
        assert hasattr(vista, 'indicador_reposo')
        assert hasattr(vista, 'indicador_frio')
        assert vista.indicador_calor is not None
        assert vista.indicador_reposo is not None
        assert vista.indicador_frio is not None

    def test_iconos_correctos(self, qapp):
        """
        Test: Los iconos emoji son correctos.

        Given: Se crea una ClimatizadorVista
        When: Se inspeccionan los labels de iconos
        Then: Contienen los emojis correctos (🔥, 🌬️, ❄️)
        """
        vista = ClimatizadorVista()

        # Buscar QLabel dentro de cada indicador
        icono_calor = vista.indicador_calor.findChild(
            type(vista.indicador_calor.layout().itemAt(0).widget())
        )
        icono_reposo = vista.indicador_reposo.findChild(
            type(vista.indicador_reposo.layout().itemAt(0).widget())
        )
        icono_frio = vista.indicador_frio.findChild(
            type(vista.indicador_frio.layout().itemAt(0).widget())
        )

        # Verificar que los labels de icono contienen los emojis
        # Los iconos están en el primer widget del layout
        label_calor = vista.indicador_calor.layout().itemAt(0).widget()
        label_reposo = vista.indicador_reposo.layout().itemAt(0).widget()
        label_frio = vista.indicador_frio.layout().itemAt(0).widget()

        assert "🔥" in label_calor.text()
        assert "🌬️" in label_reposo.text()
        assert "❄️" in label_frio.text()


class TestActualizacion:
    """Tests de actualización de la vista con diferentes modelos."""

    def test_actualizar_modo_calentando(self, qapp):
        """
        Test: Actualizar vista con modo calentando.

        Given: Vista creada
        When: Se actualiza con modelo modo=MODO_CALENTANDO, encendido=True
        Then: Solo indicador_calor tiene activo="true"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)

        vista.actualizar(modelo)

        assert vista.indicador_calor.property("activo") == "true"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"

    def test_actualizar_modo_enfriando(self, qapp):
        """
        Test: Actualizar vista con modo enfriando.

        Given: Vista creada
        When: Se actualiza con modelo modo=MODO_ENFRIANDO, encendido=True
        Then: Solo indicador_frio tiene activo="true"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_ENFRIANDO, encendido=True)

        vista.actualizar(modelo)

        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "true"

    def test_actualizar_modo_reposo(self, qapp):
        """
        Test: Actualizar vista con modo reposo.

        Given: Vista creada
        When: Se actualiza con modelo modo=MODO_REPOSO, encendido=True
        Then: Solo indicador_reposo tiene activo="true"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        vista.actualizar(modelo)

        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "true"
        assert vista.indicador_frio.property("activo") == "false"

    def test_actualizar_cuando_apagado(self, qapp):
        """
        Test: Actualizar vista cuando está apagado.

        Given: Vista creada
        When: Se actualiza con modelo encendido=False
        Then: Todos los indicadores tienen activo="false"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=False)

        vista.actualizar(modelo)

        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"


class TestEstilos:
    """Tests de estilos CSS de los indicadores."""

    def test_colores_activo_calor(self, qapp):
        """
        Test: Colores del indicador calor cuando activo.

        Given: Vista con modo=MODO_CALENTANDO
        When: Se renderiza
        Then: indicador_calor tiene property activo="true"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)

        vista.actualizar(modelo)

        # Verificar que la propiedad CSS está establecida
        assert vista.indicador_calor.property("activo") == "true"

    def test_colores_activo_reposo(self, qapp):
        """
        Test: Colores del indicador reposo cuando activo.

        Given: Vista con modo=MODO_REPOSO
        When: Se renderiza
        Then: indicador_reposo tiene property activo="true"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        vista.actualizar(modelo)

        assert vista.indicador_reposo.property("activo") == "true"

    def test_colores_activo_frio(self, qapp):
        """
        Test: Colores del indicador frío cuando activo.

        Given: Vista con modo=MODO_ENFRIANDO
        When: Se renderiza
        Then: indicador_frio tiene property activo="true"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_ENFRIANDO, encendido=True)

        vista.actualizar(modelo)

        assert vista.indicador_frio.property("activo") == "true"

    def test_colores_inactivos(self, qapp):
        """
        Test: Colores de indicadores inactivos.

        Given: Vista con modo=MODO_REPOSO
        When: Se renderiza
        Then: Los otros indicadores tienen activo="false"
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        vista.actualizar(modelo)

        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "false"

    def test_animacion_presente_calor(self, qapp):
        """
        Test: Animación presente en indicador calor cuando activo.

        Given: Vista con modo=MODO_CALENTANDO
        When: Se renderiza
        Then: indicador_calor tiene animación iniciada
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)

        vista.actualizar(modelo)

        # Verificar que el widget tiene el atributo _animation y está corriendo
        from PyQt6.QtCore import QAbstractAnimation
        assert hasattr(vista.indicador_calor, '_animation')
        assert vista.indicador_calor._animation.state() != QAbstractAnimation.State.Stopped

    def test_animacion_presente_frio(self, qapp):
        """
        Test: Animación presente en indicador frío cuando activo.

        Given: Vista con modo=MODO_ENFRIANDO
        When: Se renderiza
        Then: indicador_frio tiene animación iniciada
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_ENFRIANDO, encendido=True)

        vista.actualizar(modelo)

        from PyQt6.QtCore import QAbstractAnimation
        assert hasattr(vista.indicador_frio, '_animation')
        assert vista.indicador_frio._animation.state() != QAbstractAnimation.State.Stopped

    def test_sin_animacion_reposo(self, qapp):
        """
        Test: Sin animación en indicador reposo.

        Given: Vista con modo=MODO_REPOSO
        When: Se renderiza
        Then: indicador_reposo NO tiene animación corriendo
        """
        vista = ClimatizadorVista()
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        vista.actualizar(modelo)

        # Reposo puede tener el atributo pero debe estar detenida
        if hasattr(vista.indicador_reposo, '_animation'):
            from PyQt6.QtCore import QAbstractAnimation
            assert vista.indicador_reposo._animation.state() == QAbstractAnimation.State.Stopped


class TestTransiciones:
    """Tests de transiciones entre estados del climatizador."""

    def test_transicion_calor_a_reposo(self, qapp):
        """
        Test: Transición de calor a reposo.

        Given: Vista con modo=MODO_CALENTANDO
        When: Se actualiza a modo=MODO_REPOSO
        Then: Solo reposo está activo, animación de calor se detiene
        """
        vista = ClimatizadorVista()
        modelo_inicial = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)
        vista.actualizar(modelo_inicial)

        # Verificar estado inicial
        assert vista.indicador_calor.property("activo") == "true"

        # Transición
        modelo_nuevo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)
        vista.actualizar(modelo_nuevo)

        # Verificar transición
        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "true"
        assert vista.indicador_frio.property("activo") == "false"

        # Animación de calor detenida
        if hasattr(vista.indicador_calor, '_animation'):
            from PyQt6.QtCore import QAbstractAnimation
            assert vista.indicador_calor._animation.state() == QAbstractAnimation.State.Stopped

    def test_transicion_reposo_a_frio(self, qapp):
        """
        Test: Transición de reposo a frío.

        Given: Vista con modo=MODO_REPOSO
        When: Se actualiza a modo=MODO_ENFRIANDO
        Then: Solo frío está activo, animación de frío inicia
        """
        vista = ClimatizadorVista()
        modelo_inicial = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)
        vista.actualizar(modelo_inicial)

        # Transición
        modelo_nuevo = ClimatizadorModelo(modo=MODO_ENFRIANDO, encendido=True)
        vista.actualizar(modelo_nuevo)

        # Verificar transición
        assert vista.indicador_calor.property("activo") == "false"
        assert vista.indicador_reposo.property("activo") == "false"
        assert vista.indicador_frio.property("activo") == "true"

        # Animación de frío corriendo
        from PyQt6.QtCore import QAbstractAnimation
        assert hasattr(vista.indicador_frio, '_animation')
        assert vista.indicador_frio._animation.state() != QAbstractAnimation.State.Stopped

    def test_solo_un_indicador_activo(self, qapp):
        """
        Test: Solo un indicador puede estar activo a la vez.

        Given: Vista creada
        When: Se prueba con todos los modos
        Then: En cada caso solo un indicador está activo
        """
        vista = ClimatizadorVista()

        # Caso 1: Calentando
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)
        vista.actualizar(modelo)
        activos = [
            vista.indicador_calor.property("activo") == "true",
            vista.indicador_reposo.property("activo") == "true",
            vista.indicador_frio.property("activo") == "true"
        ]
        assert sum(activos) == 1

        # Caso 2: Reposo
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)
        vista.actualizar(modelo)
        activos = [
            vista.indicador_calor.property("activo") == "true",
            vista.indicador_reposo.property("activo") == "true",
            vista.indicador_frio.property("activo") == "true"
        ]
        assert sum(activos) == 1

        # Caso 3: Enfriando
        modelo = ClimatizadorModelo(modo=MODO_ENFRIANDO, encendido=True)
        vista.actualizar(modelo)
        activos = [
            vista.indicador_calor.property("activo") == "true",
            vista.indicador_reposo.property("activo") == "true",
            vista.indicador_frio.property("activo") == "true"
        ]
        assert sum(activos) == 1

        # Caso 4: Apagado - ninguno activo
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=False)
        vista.actualizar(modelo)
        activos = [
            vista.indicador_calor.property("activo") == "true",
            vista.indicador_reposo.property("activo") == "true",
            vista.indicador_frio.property("activo") == "true"
        ]
        assert sum(activos) == 0
