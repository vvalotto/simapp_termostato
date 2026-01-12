#!/usr/bin/env python3
"""Punto de entrada para el Simulador de Batería.

Integra la UI con el generador de batería y el cliente TCP
para enviar valores de voltaje al ISSE_Termostato.

Usa el patrón Factory para crear componentes y Coordinator para
conectar las señales entre ellos.
"""
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication

from app.configuracion.config import ConfigManager
from app.factory import ComponenteFactory
from app.coordinator import SimuladorCoordinator
from app.presentacion import UIPrincipalCompositor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AplicacionSimulador:
    """Clase principal que integra todos los componentes del simulador.

    Usa Factory para crear componentes y Coordinator para conectar señales.
    Esta clase solo gestiona el ciclo de vida de la aplicación.
    """

    def __init__(self):
        """Inicializa la aplicación cargando configuración y creando componentes."""
        # Cargar configuración
        self._config_manager = ConfigManager()
        self._config = self._config_manager.cargar()

        logger.info(
            "Configuración cargada: IP=%s, Puerto=%d",
            self._config.host,
            self._config.puerto
        )

        # Crear factory
        self._factory = ComponenteFactory(self._config)

        # Crear componentes de dominio
        self._generador = self._factory.crear_generador()

        # Crear cliente y servicio iniciales
        self._cliente = self._factory.crear_cliente()
        self._servicio = self._factory.crear_servicio(
            self._generador, self._cliente
        )

        # Crear controladores MVC
        controladores = self._factory.crear_controladores()
        self._ctrl_estado = controladores['estado']
        self._ctrl_control = controladores['control']
        self._ctrl_conexion = controladores['conexion']

        # Crear UI con controladores
        self._ventana = UIPrincipalCompositor(
            ctrl_estado=self._ctrl_estado,
            ctrl_control=self._ctrl_control,
            ctrl_conexion=self._ctrl_conexion,
        )

        # Crear coordinator para conectar señales
        self._coordinator = SimuladorCoordinator(
            generador=self._generador,
            ctrl_estado=self._ctrl_estado,
            ctrl_control=self._ctrl_control,
            ctrl_conexion=self._ctrl_conexion,
        )

        # Conectar señales del coordinator para manejar conexión/desconexión
        self._coordinator.conexion_solicitada.connect(self._on_conectar)
        self._coordinator.desconexion_solicitada.connect(self._on_desconectar)

        # Estado de la simulación
        self._simulacion_activa = False
        logger.info("Aplicación inicializada - Presione 'Conectar' para iniciar")

    def _on_conectar(self):
        """Callback cuando se solicita conectar."""
        # Obtener IP y puerto del coordinator
        nueva_ip = self._coordinator.ip_configurada
        nuevo_puerto = self._coordinator.puerto_configurado

        logger.info("Conectando a %s:%d", nueva_ip, nuevo_puerto)

        # Recrear cliente con nueva configuración
        self._cliente = self._factory.crear_cliente(
            host=nueva_ip,
            port=nuevo_puerto
        )

        # Recrear servicio con nuevo cliente
        self._servicio = self._factory.crear_servicio(
            self._generador,
            self._cliente
        )

        # Reconectar coordinator al nuevo servicio
        self._coordinator.set_servicio(self._servicio)

        # Iniciar servicio
        self._servicio.iniciar()
        self._simulacion_activa = True
        logger.info("Servicio de envío iniciado -> %s:%d", nueva_ip, nuevo_puerto)

    def _on_desconectar(self):
        """Callback cuando se solicita desconectar."""
        if self._simulacion_activa:
            self._servicio.detener()
            self._simulacion_activa = False
            logger.info("Servicio de envío detenido")

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
