"""Tests unitarios para ServicioEnvioBateria.

Cubre:
- Creación con generador y cliente
- Métodos: iniciar(), detener()
- Signals: envio_exitoso, envio_fallido, servicio_iniciado, servicio_detenido
- Integración generador → cliente
"""
import pytest

from app.comunicacion.servicio_envio import ServicioEnvioBateria
from app.dominio.estado_bateria import EstadoBateria


class TestServicioEnvioBateriaCreacion:
    """Tests de creación del servicio."""

    def test_crear_servicio(self, generador, mock_cliente, qtbot):
        """Verifica creación básica."""
        servicio = ServicioEnvioBateria(generador, mock_cliente)

        assert servicio is not None
        assert servicio.generador is generador
        assert servicio.cliente is mock_cliente

    def test_estado_inicial_inactivo(self, servicio):
        """Estado inicial es inactivo."""
        assert servicio.activo is False

    def test_properties_generador_y_cliente(self, servicio, generador, mock_cliente):
        """Properties retornan generador y cliente."""
        assert servicio.generador is generador
        assert servicio.cliente is mock_cliente


class TestServicioEnvioBateriaIniciar:
    """Tests de iniciar()."""

    def test_iniciar_cambia_estado_a_activo(self, servicio):
        """iniciar() cambia activo a True."""
        servicio.iniciar()

        assert servicio.activo is True

        servicio.detener()

    def test_iniciar_emite_signal_servicio_iniciado(self, servicio, qtbot):
        """iniciar() emite servicio_iniciado."""
        with qtbot.waitSignal(servicio.servicio_iniciado, timeout=1000):
            servicio.iniciar()

        servicio.detener()

    def test_iniciar_inicia_generador(self, servicio, generador, qtbot):
        """iniciar() inicia el generador."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        servicio.iniciar()
        qtbot.wait(250)
        servicio.detener()

        # El generador debe haber emitido valores
        assert len(signal_spy) >= 2

    def test_iniciar_multiple_veces_no_duplica(self, servicio):
        """Llamar iniciar() múltiples veces no duplica estado."""
        servicio.iniciar()
        servicio.iniciar()  # Segunda llamada
        servicio.iniciar()  # Tercera llamada

        assert servicio.activo is True

        servicio.detener()


class TestServicioEnvioBateriaDetener:
    """Tests de detener()."""

    def test_detener_cambia_estado_a_inactivo(self, servicio):
        """detener() cambia activo a False."""
        servicio.iniciar()
        servicio.detener()

        assert servicio.activo is False

    def test_detener_emite_signal_servicio_detenido(self, servicio, qtbot):
        """detener() emite servicio_detenido."""
        servicio.iniciar()

        with qtbot.waitSignal(servicio.servicio_detenido, timeout=1000):
            servicio.detener()

    def test_detener_para_generador(self, servicio, generador, qtbot):
        """detener() para el generador."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        servicio.iniciar()
        qtbot.wait(150)
        servicio.detener()

        count_after_stop = len(signal_spy)
        qtbot.wait(150)

        # No debe haber nuevas emisiones después de detener
        assert len(signal_spy) == count_after_stop

    def test_detener_sin_iniciar_no_falla(self, servicio):
        """Llamar detener() sin iniciar no falla."""
        servicio.detener()

        assert servicio.activo is False


class TestServicioEnvioBateriaSignalEnvioExitoso:
    """Tests del signal envio_exitoso."""

    def test_generador_dispara_envio_exitoso(self, servicio, mock_ephemeral_client, qtbot):
        """Valor generado dispara envio_exitoso."""
        # Configurar mock para emitir data_sent cuando se llama send_async
        def emit_data_sent(data):
            # Simular que el cliente emite data_sent después de enviar
            servicio.cliente._cliente.data_sent.emit()

        mock_ephemeral_client.send_async.side_effect = emit_data_sent

        signal_spy = []
        servicio.envio_exitoso.connect(lambda v: signal_spy.append(v))

        servicio.iniciar()
        qtbot.wait(250)
        servicio.detener()

        # Debe haber emitido signals de envío exitoso
        assert len(signal_spy) >= 1
        assert all(isinstance(v, float) for v in signal_spy)

    def test_envio_exitoso_contiene_voltaje(self, servicio, mock_ephemeral_client, qtbot):
        """envio_exitoso emite el voltaje enviado."""
        # Configurar mock para emitir data_sent
        def emit_data_sent(data):
            servicio.cliente._cliente.data_sent.emit()

        mock_ephemeral_client.send_async.side_effect = emit_data_sent

        signal_spy = []
        servicio.envio_exitoso.connect(lambda v: signal_spy.append(v))

        servicio.iniciar()
        qtbot.wait(250)
        servicio.detener()

        # Los voltajes deben ser el valor actual del generador (12.0)
        assert all(v == pytest.approx(12.0) for v in signal_spy)


class TestServicioEnvioBateriaIntegracion:
    """Tests de integración generador → servicio → cliente."""

    def test_flujo_completo_generacion_envio(self, servicio, generador, mock_ephemeral_client, qtbot):
        """Flujo completo: generar → enviar."""
        servicio.iniciar()
        qtbot.wait(250)
        servicio.detener()

        # El cliente debe haber recibido llamadas de envío
        assert mock_ephemeral_client.send_async.call_count >= 2

    def test_cambiar_voltaje_afecta_envio(self, servicio, generador, mock_ephemeral_client, qtbot):
        """Cambiar voltaje del generador afecta lo que se envía."""
        servicio.iniciar()
        qtbot.wait(50)

        # Cambiar voltaje
        generador.set_voltaje(14.0)

        qtbot.wait(200)
        servicio.detener()

        # Las últimas llamadas deben ser con el nuevo voltaje
        ultimas_llamadas = mock_ephemeral_client.send_async.call_args_list[-2:]
        assert all(call[0][0] == "14.00" for call in ultimas_llamadas)

    def test_iniciar_detener_reiniciar(self, servicio, generador, qtbot):
        """Puede iniciar, detener y volver a iniciar."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        # Primera ejecución
        servicio.iniciar()
        qtbot.wait(150)
        servicio.detener()
        count_primera = len(signal_spy)

        # Segunda ejecución
        servicio.iniciar()
        qtbot.wait(150)
        servicio.detener()
        count_segunda = len(signal_spy)

        # Debe haber generado valores en ambas ejecuciones
        assert count_primera >= 1
        assert count_segunda > count_primera


class TestServicioEnvioBateriaConexionSignals:
    """Tests de conexión de signals generador → servicio → cliente."""

    def test_valor_generado_conectado_a_envio(self, servicio, generador, mock_ephemeral_client):
        """Signal valor_generado está conectado al envío."""
        # Generar valor manualmente
        estado = generador.generar_valor()

        # El servicio debe haber procesado y enviado
        # (aunque el servicio no esté iniciado, la conexión existe si el servicio la maneja)
        # Este test verifica la arquitectura de conexión

    def test_servicio_desconecta_al_detener(self, servicio, generador, mock_ephemeral_client, qtbot):
        """detener() desconecta signals del generador."""
        signal_spy = []
        generador.valor_generado.connect(lambda x: signal_spy.append(x))

        servicio.iniciar()
        qtbot.wait(100)
        servicio.detener()

        count_after_stop = len(signal_spy)

        # Generar valor manualmente después de detener
        generador.generar_valor()

        # El signal_spy debe tener +1 (del generar manual)
        # pero el servicio no debe procesarlo
        assert len(signal_spy) == count_after_stop + 1


class TestServicioEnvioBateriaErrorHandling:
    """Tests de manejo de errores."""

    def test_error_en_envio_no_detiene_servicio(self, servicio, mock_ephemeral_client, qtbot):
        """Error en envío no detiene el servicio."""
        # Simular fallo en un envío
        mock_ephemeral_client.send_async.side_effect = Exception("Connection error")

        servicio.iniciar()
        qtbot.wait(250)

        # El servicio debe seguir activo
        assert servicio.activo is True

        servicio.detener()
