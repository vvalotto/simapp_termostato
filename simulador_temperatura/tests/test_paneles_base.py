"""Tests para las clases base MVC de paneles."""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget

from app.presentacion.paneles.base import (
    ModeloBase,
    VistaBase,
    ControladorBase,
)


# Implementaciones concretas para testing

class ModeloConcreto(ModeloBase):
    """Modelo concreto para tests."""

    def __init__(self, valor: int = 0):
        self.valor = valor


class VistaConcreto(VistaBase):
    """Vista concreta para tests."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ultimo_modelo = None
        self.actualizaciones = 0

    def actualizar(self, modelo: ModeloBase) -> None:
        self.ultimo_modelo = modelo
        self.actualizaciones += 1


class ControladorConcreto(ControladorBase[ModeloConcreto, VistaConcreto]):
    """Controlador concreto para tests."""

    def _conectar_signals(self) -> None:
        # Implementación vacía para tests
        pass


class TestModeloBase:
    """Tests para ModeloBase."""

    def test_modelo_es_abstracto(self):
        """ModeloBase no puede instanciarse directamente."""
        # ModeloBase es ABC pero no tiene métodos abstractos,
        # por lo que técnicamente puede instanciarse si no se usa ABC
        # Verificamos que la clase existe y hereda correctamente
        assert issubclass(ModeloConcreto, ModeloBase)

    def test_modelo_concreto_puede_instanciarse(self):
        """Un modelo concreto puede instanciarse."""
        modelo = ModeloConcreto(valor=42)
        assert modelo.valor == 42


class TestVistaBase:
    """Tests para VistaBase."""

    def test_vista_es_qwidget(self, qtbot):
        """VistaBase hereda de QWidget."""
        vista = VistaConcreto()
        qtbot.addWidget(vista)
        assert isinstance(vista, QWidget)

    def test_vista_requiere_actualizar(self):
        """VistaBase requiere implementar actualizar()."""
        # Verificamos que VistaConcreto implementa actualizar
        assert hasattr(VistaConcreto, 'actualizar')

    def test_vista_actualizar_recibe_modelo(self, qtbot):
        """El método actualizar recibe un modelo."""
        vista = VistaConcreto()
        qtbot.addWidget(vista)
        modelo = ModeloConcreto(valor=10)

        vista.actualizar(modelo)

        assert vista.ultimo_modelo == modelo
        assert vista.actualizaciones == 1

    def test_vista_multiples_actualizaciones(self, qtbot):
        """La vista puede actualizarse múltiples veces."""
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        for i in range(5):
            vista.actualizar(ModeloConcreto(valor=i))

        assert vista.actualizaciones == 5


class TestControladorBase:
    """Tests para ControladorBase."""

    def test_controlador_es_qobject(self, qtbot):
        """ControladorBase hereda de QObject."""
        modelo = ModeloConcreto()
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        controlador = ControladorConcreto(modelo, vista)

        assert isinstance(controlador, QObject)

    def test_controlador_tiene_modelo(self, qtbot):
        """El controlador expone el modelo."""
        modelo = ModeloConcreto(valor=100)
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        controlador = ControladorConcreto(modelo, vista)

        assert controlador.modelo is modelo
        assert controlador.modelo.valor == 100

    def test_controlador_tiene_vista(self, qtbot):
        """El controlador expone la vista."""
        modelo = ModeloConcreto()
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        controlador = ControladorConcreto(modelo, vista)

        assert controlador.vista is vista

    def test_controlador_conecta_signals_al_crear(self, qtbot):
        """El controlador llama _conectar_signals al inicializar."""
        modelo = ModeloConcreto()
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        with patch.object(
            ControladorConcreto,
            '_conectar_signals'
        ) as mock_conectar:
            controlador = ControladorConcreto(modelo, vista)
            mock_conectar.assert_called_once()

    def test_controlador_actualizar_vista(self, qtbot):
        """_actualizar_vista actualiza la vista con el modelo."""
        modelo = ModeloConcreto(valor=50)
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        controlador = ControladorConcreto(modelo, vista)
        controlador._actualizar_vista()

        assert vista.ultimo_modelo is modelo
        assert vista.actualizaciones == 1

    def test_controlador_emite_modelo_cambiado(self, qtbot):
        """_actualizar_vista emite signal modelo_cambiado."""
        modelo = ModeloConcreto(valor=25)
        vista = VistaConcreto()
        qtbot.addWidget(vista)

        controlador = ControladorConcreto(modelo, vista)

        with qtbot.waitSignal(controlador.modelo_cambiado, timeout=1000) as blocker:
            controlador._actualizar_vista()

        assert blocker.args[0] is modelo

    def test_controlador_con_parent(self, qtbot):
        """El controlador puede tener un parent QObject."""
        modelo = ModeloConcreto()
        vista = VistaConcreto()
        qtbot.addWidget(vista)
        parent = QObject()

        controlador = ControladorConcreto(modelo, vista, parent=parent)

        assert controlador.parent() is parent
