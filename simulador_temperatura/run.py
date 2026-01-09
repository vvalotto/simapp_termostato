#!/usr/bin/env python3
"""Punto de entrada para el Simulador de Temperatura.

Integra la UI con el generador de temperatura y el cliente TCP
para enviar valores al ISSE_Termostato.
"""
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication

from app.configuracion.config import ConfigManager
from app.presentacion import UIPrincipal, ConfigConexion
from app.presentacion.control_temperatura import ParametrosSenoidal
from app.dominio.generador_temperatura import GeneradorTemperatura
from app.dominio.variacion_senoidal import VariacionSenoidal
from app.comunicacion.cliente_temperatura import ClienteTemperatura
from app.comunicacion.servicio_envio import ServicioEnvioTemperatura

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AplicacionSimulador:
    """Clase principal que integra todos los componentes del simulador."""

    def __init__(self):
        """Inicializa la aplicación cargando configuración y creando componentes."""
        # Cargar configuración
        self._config_manager = ConfigManager()
        self._config = self._config_manager.cargar()

        logger.info(
            "Configuración cargada: IP=%s, Puerto=%d",
            self._config.ip_raspberry,
            self._config.puerto
        )

        # Crear componentes de dominio
        self._generador = GeneradorTemperatura(self._config)

        # Crear cliente TCP
        self._cliente = ClienteTemperatura(
            host=self._config.ip_raspberry,
            port=self._config.puerto
        )

        # Crear servicio de integración
        self._servicio = ServicioEnvioTemperatura(
            generador=self._generador,
            cliente=self._cliente
        )

        # Crear UI con configuración de conexión
        config_conexion = ConfigConexion(
            ip=self._config.ip_raspberry,
            puerto=self._config.puerto
        )
        self._ventana = UIPrincipal(config_conexion=config_conexion)

        # Conectar señales
        self._conectar_ui_con_generador()
        self._conectar_generador_con_ui()
        self._conectar_servicio_con_ui()
        self._conectar_config_panel()

        # El servicio NO inicia automáticamente, espera al botón Conectar
        self._simulacion_activa = False
        logger.info("Aplicación inicializada - Presione 'Conectar' para iniciar")

    def _conectar_ui_con_generador(self):
        """Conecta las señales de la UI con el generador."""
        # Cuando cambian los parámetros senoidales en la UI
        self._ventana.parametros_cambiados.connect(self._on_parametros_cambiados)

        # Cuando cambia la temperatura manual en la UI
        self._ventana.temperatura_manual_cambiada.connect(
            self._generador.set_temperatura_manual
        )

        # Cuando cambia el modo en la UI
        self._ventana.control_temperatura.modo_cambiado.connect(
            self._on_modo_cambiado
        )

    def _conectar_generador_con_ui(self):
        """Conecta las señales del generador con la UI."""
        # Cuando se genera un nuevo valor, actualizar gráfico y display
        self._generador.valor_generado.connect(self._on_valor_generado)

    def _conectar_servicio_con_ui(self):
        """Conecta las señales del servicio con la UI."""
        # Cuando se envía exitosamente
        self._servicio.envio_exitoso.connect(self._on_envio_exitoso)

        # Cuando falla el envío
        self._servicio.envio_fallido.connect(self._on_envio_fallido)

    def _conectar_config_panel(self):
        """Conecta las señales del panel de configuración."""
        self._ventana.conexion_solicitada.connect(self._on_conectar)
        self._ventana.desconexion_solicitada.connect(self._on_desconectar)

    def _on_conectar(self):
        """Callback cuando se solicita conectar."""
        # Obtener IP y puerto del panel de configuración
        nueva_ip = self._ventana.obtener_ip()
        nuevo_puerto = self._ventana.obtener_puerto()

        logger.info("Conectando a %s:%d", nueva_ip, nuevo_puerto)

        # Reiniciar contadores
        self._ventana.reiniciar_contadores()

        # Recrear cliente con nueva configuración
        self._cliente = ClienteTemperatura(
            host=nueva_ip,
            port=nuevo_puerto
        )

        # Recrear servicio con nuevo cliente
        self._servicio = ServicioEnvioTemperatura(
            generador=self._generador,
            cliente=self._cliente
        )

        # Reconectar señales del servicio
        self._servicio.envio_exitoso.connect(self._on_envio_exitoso)
        self._servicio.envio_fallido.connect(self._on_envio_fallido)

        # Iniciar servicio
        self._servicio.iniciar()
        self._simulacion_activa = True
        logger.info("Servicio de envío iniciado -> %s:%d", nueva_ip, nuevo_puerto)

    def _on_desconectar(self):
        """Callback cuando se solicita desconectar."""
        if self._simulacion_activa:
            self._servicio.detener()
            self._simulacion_activa = False
            self._ventana.actualizar_estado_conexion(False)
            logger.info("Servicio de envío detenido")

    def _on_parametros_cambiados(self, parametros: ParametrosSenoidal):
        """Callback cuando cambian los parámetros senoidales."""
        # Actualizar la variación senoidal del generador
        self._generador._variacion = VariacionSenoidal(
            temperatura_base=parametros.temperatura_base,
            amplitud=parametros.amplitud,
            periodo_segundos=parametros.periodo,
        )
        self._generador.set_modo_automatico()
        logger.debug(
            "Parámetros actualizados: base=%.1f, amp=%.1f, periodo=%.1f",
            parametros.temperatura_base,
            parametros.amplitud,
            parametros.periodo
        )

    def _on_modo_cambiado(self, es_manual: bool):
        """Callback cuando cambia el modo de operación."""
        if es_manual:
            temperatura = self._ventana.control_temperatura.temperatura_manual
            self._generador.set_temperatura_manual(temperatura)
            logger.info("Modo manual activado: %.1f°C", temperatura)
        else:
            self._generador.set_modo_automatico()
            logger.info("Modo automático activado")

    def _on_valor_generado(self, estado):
        """Callback cuando se genera un nuevo valor de temperatura."""
        temperatura = estado.temperatura
        self._ventana.agregar_punto_grafico(temperatura)
        self._ventana.actualizar_temperatura_display(temperatura)

    def _on_envio_exitoso(self, temperatura: float):
        """Callback cuando se envía exitosamente al servidor."""
        self._ventana.actualizar_estado_conexion(True)
        self._ventana.incrementar_envios_exitosos()
        logger.debug("Enviado exitosamente: %.2f°C", temperatura)

    def _on_envio_fallido(self, mensaje: str):
        """Callback cuando falla el envío al servidor."""
        self._ventana.actualizar_estado_conexion(False)
        self._ventana.incrementar_envios_fallidos()
        logger.warning("Error de envío: %s", mensaje)

    def mostrar(self):
        """Muestra la ventana principal."""
        self._ventana.show()

    def detener(self):
        """Detiene el servicio de envío."""
        if self._simulacion_activa:
            self._servicio.detener()
            self._simulacion_activa = False
            logger.info("Servicio detenido")


def main():
    """Función principal de la aplicación."""
    app = QApplication(sys.argv)

    simulador = AplicacionSimulador()
    simulador.mostrar()

    # Asegurar limpieza al cerrar
    app.aboutToQuit.connect(simulador.detener)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
