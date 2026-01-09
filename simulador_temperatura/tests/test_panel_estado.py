"""Tests para el Panel de Estado MVC."""

import pytest

from app.presentacion.paneles.estado import (
    EstadoSimulacion,
    PanelEstadoVista,
    PanelEstadoControlador,
)
from app.presentacion.paneles.estado.vista import ConfigPanelEstadoVista


class TestEstadoSimulacionModelo:
    """Tests para el modelo EstadoSimulacion."""

    def test_crear_estado_por_defecto(self):
        """Crear estado con valores por defecto."""
        estado = EstadoSimulacion()

        assert estado.temperatura_actual == 0.0
        assert estado.conectado is False
        assert estado.envios_exitosos == 0
        assert estado.envios_fallidos == 0

    def test_crear_estado_con_valores(self):
        """Crear estado con valores personalizados."""
        estado = EstadoSimulacion(
            temperatura_actual=25.5,
            conectado=True,
            envios_exitosos=10,
            envios_fallidos=2
        )

        assert estado.temperatura_actual == 25.5
        assert estado.conectado is True
        assert estado.envios_exitosos == 10
        assert estado.envios_fallidos == 2

    def test_incrementar_exitosos(self):
        """incrementar_exitosos incrementa el contador."""
        estado = EstadoSimulacion()

        estado.incrementar_exitosos()

        assert estado.envios_exitosos == 1

    def test_incrementar_fallidos(self):
        """incrementar_fallidos incrementa el contador."""
        estado = EstadoSimulacion()

        estado.incrementar_fallidos()

        assert estado.envios_fallidos == 1

    def test_reiniciar_contadores(self):
        """reiniciar_contadores pone ambos en cero."""
        estado = EstadoSimulacion(envios_exitosos=5, envios_fallidos=3)

        estado.reiniciar_contadores()

        assert estado.envios_exitosos == 0
        assert estado.envios_fallidos == 0

    def test_total_envios(self):
        """total_envios suma exitosos y fallidos."""
        estado = EstadoSimulacion(envios_exitosos=5, envios_fallidos=3)

        assert estado.total_envios == 8

    def test_tasa_exito_sin_envios(self):
        """tasa_exito retorna 0 sin envíos."""
        estado = EstadoSimulacion()

        assert estado.tasa_exito == 0.0

    def test_tasa_exito_con_envios(self):
        """tasa_exito calcula correctamente."""
        estado = EstadoSimulacion(envios_exitosos=8, envios_fallidos=2)

        assert estado.tasa_exito == 0.8

    def test_tasa_exito_todos_exitosos(self):
        """tasa_exito es 1.0 si todos son exitosos."""
        estado = EstadoSimulacion(envios_exitosos=10, envios_fallidos=0)

        assert estado.tasa_exito == 1.0


class TestPanelEstadoVista:
    """Tests para PanelEstadoVista."""

    def test_crear_vista(self, qtbot):
        """Crear vista con configuración por defecto."""
        vista = PanelEstadoVista()
        qtbot.addWidget(vista)

        assert vista is not None

    def test_crear_vista_con_config(self, qtbot):
        """Crear vista con configuración personalizada."""
        config = ConfigPanelEstadoVista(titulo="Mi Panel")
        vista = PanelEstadoVista(config=config)
        qtbot.addWidget(vista)

        assert vista is not None

    def test_actualizar_con_modelo(self, qtbot):
        """actualizar() actualiza los labels."""
        vista = PanelEstadoVista()
        qtbot.addWidget(vista)
        modelo = EstadoSimulacion(
            temperatura_actual=23.5,
            conectado=True,
            envios_exitosos=5,
            envios_fallidos=2
        )

        vista.actualizar(modelo)

        assert "23.5" in vista._label_temperatura.text()
        assert vista._config.texto_conectado in vista._label_conexion.text()
        assert "5" in vista._label_contador.text()
        assert "2" in vista._label_contador.text()

    def test_actualizar_desconectado(self, qtbot):
        """actualizar() muestra estado desconectado."""
        vista = PanelEstadoVista()
        qtbot.addWidget(vista)
        modelo = EstadoSimulacion(conectado=False)

        vista.actualizar(modelo)

        assert vista._config.texto_desconectado in vista._label_conexion.text()

    def test_mostrar_sin_datos(self, qtbot):
        """mostrar_sin_datos() muestra placeholder."""
        vista = PanelEstadoVista()
        qtbot.addWidget(vista)

        vista.mostrar_sin_datos()

        assert vista._config.texto_sin_datos in vista._label_temperatura.text()


class TestPanelEstadoControlador:
    """Tests para PanelEstadoControlador."""

    def test_crear_controlador(self, qtbot):
        """Crear controlador sin argumentos."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        assert controlador.modelo is not None
        assert controlador.vista is not None

    def test_crear_controlador_con_modelo_y_vista(self, qtbot):
        """Crear controlador con modelo y vista existentes."""
        modelo = EstadoSimulacion(temperatura_actual=20.0)
        vista = PanelEstadoVista()
        qtbot.addWidget(vista)

        controlador = PanelEstadoControlador(modelo=modelo, vista=vista)

        assert controlador.modelo is modelo
        assert controlador.vista is vista

    def test_actualizar_temperatura(self, qtbot):
        """actualizar_temperatura actualiza modelo y vista."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.actualizar_temperatura(25.5)

        assert controlador.temperatura_actual == 25.5
        assert "25.5" in controlador.vista._label_temperatura.text()

    def test_actualizar_temperatura_emite_signal(self, qtbot):
        """actualizar_temperatura emite signal."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.temperatura_actualizada, timeout=1000) as blocker:
            controlador.actualizar_temperatura(30.0)

        assert blocker.args[0] == 30.0

    def test_actualizar_conexion_conectado(self, qtbot):
        """actualizar_conexion(True) actualiza estado."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.actualizar_conexion(True)

        assert controlador.conectado is True

    def test_actualizar_conexion_desconectado(self, qtbot):
        """actualizar_conexion(False) actualiza estado."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.actualizar_conexion(False)

        assert controlador.conectado is False

    def test_actualizar_conexion_emite_signal(self, qtbot):
        """actualizar_conexion emite signal."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.conexion_actualizada, timeout=1000) as blocker:
            controlador.actualizar_conexion(True)

        assert blocker.args[0] is True

    def test_registrar_envio_exitoso(self, qtbot):
        """registrar_envio_exitoso incrementa contador."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.registrar_envio_exitoso()

        assert controlador.envios_exitosos == 1

    def test_registrar_envio_fallido(self, qtbot):
        """registrar_envio_fallido incrementa contador."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.registrar_envio_fallido()

        assert controlador.envios_fallidos == 1

    def test_registrar_envio_emite_signal(self, qtbot):
        """registrar_envio emite contadores_actualizados."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        with qtbot.waitSignal(controlador.contadores_actualizados, timeout=1000) as blocker:
            controlador.registrar_envio_exitoso()

        assert blocker.args == [1, 0]

    def test_reiniciar_contadores(self, qtbot):
        """reiniciar_contadores pone contadores en cero."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_fallido()

        controlador.reiniciar_contadores()

        assert controlador.envios_exitosos == 0
        assert controlador.envios_fallidos == 0

    def test_multiples_actualizaciones(self, qtbot):
        """Múltiples actualizaciones funcionan correctamente."""
        controlador = PanelEstadoControlador()
        qtbot.addWidget(controlador.vista)

        controlador.actualizar_temperatura(15.0)
        controlador.actualizar_conexion(True)
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_fallido()

        assert controlador.temperatura_actual == 15.0
        assert controlador.conectado is True
        assert controlador.envios_exitosos == 2
        assert controlador.envios_fallidos == 1
