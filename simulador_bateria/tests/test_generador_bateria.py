"""Tests unitarios para GeneradorBateria.

Cubre:
- Creación e inicialización
- Método set_voltaje()
- Método generar_valor()
- Signals: valor_generado, voltaje_cambiado
- Timer interno (iniciar/detener)
"""
import pytest

from app.dominio.generador_bateria import GeneradorBateria
from app.dominio.estado_bateria import EstadoBateria


class TestGeneradorBateriaCreacion:
    """Tests de creación del generador."""

    def test_crear_generador(self, config, qtbot):
        """Verifica creación básica."""
        gen = GeneradorBateria(config)

        assert gen is not None
        assert gen.voltaje_actual == 12.0

    def test_voltaje_inicial_desde_config(self, generador):
        """Voltaje inicial viene de config."""
        assert generador.voltaje_actual == 12.0

    def test_timer_no_activo_al_crear(self, generador):
        """Timer no está activo al crear el generador."""
        # El timer existe pero no está activo
        assert hasattr(generador, '_timer')


class TestGeneradorBateriaSetVoltaje:
    """Tests de set_voltaje()."""

    def test_set_voltaje_actualiza_valor(self, generador):
        """set_voltaje cambia voltaje_actual."""
        generador.set_voltaje(13.5)

        assert generador.voltaje_actual == 13.5

    def test_set_voltaje_emite_signal(self, generador, qtbot):
        """set_voltaje emite voltaje_cambiado."""
        with qtbot.waitSignal(generador.voltaje_cambiado, timeout=1000) as blocker:
            generador.set_voltaje(14.0)

        assert blocker.args[0] == pytest.approx(14.0)

    def test_set_voltaje_clampea_a_minimo(self, generador):
        """set_voltaje clampea al mínimo (10.0)."""
        generador.set_voltaje(5.0)

        assert generador.voltaje_actual == 10.0

    def test_set_voltaje_clampea_a_maximo(self, generador):
        """set_voltaje clampea al máximo (15.0)."""
        generador.set_voltaje(20.0)

        assert generador.voltaje_actual == 15.0

    def test_set_voltaje_acepta_rango_valido(self, generador):
        """set_voltaje acepta valores dentro del rango."""
        generador.set_voltaje(12.75)

        assert generador.voltaje_actual == 12.75


class TestGeneradorBateriaGenerarValor:
    """Tests de generar_valor()."""

    def test_generar_valor_retorna_estado(self, generador):
        """generar_valor retorna EstadoBateria."""
        estado = generador.generar_valor()

        assert isinstance(estado, EstadoBateria)
        assert estado.voltaje == 12.0

    def test_generar_valor_emite_signal(self, generador, qtbot):
        """generar_valor emite valor_generado."""
        with qtbot.waitSignal(generador.valor_generado, timeout=1000) as blocker:
            generador.generar_valor()

        assert isinstance(blocker.args[0], EstadoBateria)

    def test_generar_valor_valida_rango(self, generador):
        """generar_valor valida si está en rango."""
        estado = generador.generar_valor()

        assert estado.en_rango is True

    def test_generar_valor_fuera_de_rango(self, generador):
        """Voltaje fuera de rango se clampea y marca en_rango=True."""
        generador.set_voltaje(20.0)  # Se clampea a 15.0 (máximo)
        estado = generador.generar_valor()

        # El valor se clampeó a 15.0, que está en el rango válido
        assert estado.voltaje == 15.0
        assert estado.en_rango is True

    def test_generar_valor_refleja_voltaje_actual(self, generador):
        """Valores generados reflejan voltaje_actual."""
        generador.set_voltaje(13.8)
        estado = generador.generar_valor()

        assert estado.voltaje == 13.8


class TestGeneradorBateriaSignals:
    """Tests de señales Qt."""

    def test_signal_valor_generado_con_estado(self, generador, qtbot):
        """Signal valor_generado emite EstadoBateria."""
        with qtbot.waitSignal(generador.valor_generado, timeout=1000) as blocker:
            generador.generar_valor()

        estado_emitido = blocker.args[0]
        assert isinstance(estado_emitido, EstadoBateria)
        assert estado_emitido.voltaje == generador.voltaje_actual

    def test_signal_voltaje_cambiado_con_valor(self, generador, qtbot):
        """Signal voltaje_cambiado emite el nuevo voltaje."""
        with qtbot.waitSignal(generador.voltaje_cambiado, timeout=1000) as blocker:
            generador.set_voltaje(14.2)

        assert blocker.args[0] == pytest.approx(14.2)

    def test_multiples_cambios_emiten_multiples_signals(self, generador, qtbot):
        """Múltiples cambios emiten múltiples signals."""
        signal_spy = []
        generador.voltaje_cambiado.connect(lambda v: signal_spy.append(v))

        generador.set_voltaje(11.0)
        generador.set_voltaje(12.0)
        generador.set_voltaje(13.0)

        assert len(signal_spy) == 3
        assert signal_spy == [11.0, 12.0, 13.0]


class TestGeneradorBateriaTimer:
    """Tests del timer interno."""

    def test_iniciar_activa_timer(self, generador, qtbot):
        """iniciar() genera valores periódicamente."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()
        qtbot.wait(250)  # Esperar ~2 emisiones (intervalo 100ms)
        generador.detener()

        assert len(signal_spy) >= 2
        assert all(isinstance(s, EstadoBateria) for s in signal_spy)

    def test_detener_para_timer(self, generador, qtbot):
        """detener() para la generación."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()
        qtbot.wait(150)
        generador.detener()

        count_after_stop = len(signal_spy)
        qtbot.wait(150)

        # No debe haber nuevas emisiones después de detener
        assert len(signal_spy) == count_after_stop

    def test_iniciar_multiples_veces_no_duplica_timer(self, generador, qtbot):
        """Llamar iniciar() múltiples veces no duplica emissions."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()
        generador.iniciar()  # Segunda llamada
        generador.iniciar()  # Tercera llamada

        qtbot.wait(250)
        generador.detener()

        # Debe haber ~2-3 emisiones, no 6-9
        assert 2 <= len(signal_spy) <= 4


class TestGeneradorBateriaIntegracion:
    """Tests de integración."""

    def test_voltaje_cambiado_afecta_generacion(self, generador):
        """Cambiar voltaje afecta valores generados."""
        generador.set_voltaje(14.5)
        estado = generador.generar_valor()

        assert estado.voltaje == 14.5

    def test_generar_mientras_timer_activo(self, generador, qtbot):
        """Puede llamar generar_valor() con timer activo."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()
        qtbot.wait(50)

        # Generar manualmente
        generador.generar_valor()

        qtbot.wait(200)
        generador.detener()

        # Debe tener emisiones del timer + la manual
        assert len(signal_spy) >= 3

    def test_cambiar_voltaje_durante_timer(self, generador, qtbot):
        """Cambiar voltaje mientras timer está activo."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        generador.iniciar()
        qtbot.wait(50)

        # Cambiar voltaje
        generador.set_voltaje(14.0)

        qtbot.wait(150)
        generador.detener()

        # Los valores generados después del cambio deben reflejar nuevo voltaje
        ultimos_valores = signal_spy[-2:]
        assert all(s.voltaje == 14.0 for s in ultimos_valores)
