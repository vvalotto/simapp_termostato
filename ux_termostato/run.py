#!/usr/bin/env python3
"""Punto de entrada para la UX Termostato Desktop.

Aplicación PyQt6 que muestra la interfaz de usuario del termostato
y se comunica con el Raspberry Pi via TCP.

Arquitectura:
- Factory: crea todos los componentes (paneles, servidor, cliente)
- Coordinator: conecta señales entre componentes
- VentanaPrincipalUX: orquesta el ciclo de vida completo

Uso:
    python run.py

Configuración:
    - config.json: valores por defecto
    - .env: sobrescribe valores (opcional)
"""

import sys
import logging
import os
from pathlib import Path

# pylint: disable=wrong-import-position
# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication

from app.configuracion import ConfigUX
from app.factory import ComponenteFactoryUX
from app.presentacion import VentanaPrincipalUX
# pylint: enable=wrong-import-position

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Versión de la aplicación
VERSION = "1.0.0"


def cargar_configuracion() -> ConfigUX:
    """Carga la configuración de la aplicación.

    Lee valores de config.json y los sobrescribe con variables de entorno
    si están definidas en .env.

    Returns:
        ConfigUX: Configuración cargada

    Raises:
        ValueError: Si la configuración tiene valores inválidos
    """
    import json

    # Leer config.json
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    ux_config = config_data.get('ux_termostato', {})
    raspberry = config_data.get('raspberry_pi', {})
    puertos = config_data.get('puertos', {})

    # Valores de config.json con sobrescritura por variables de entorno
    ip_raspberry = os.getenv('RASPBERRY_IP', raspberry.get('ip', '127.0.0.1'))
    puerto_recv = int(os.getenv('PUERTO_RECV', puertos.get('visualizador_temperatura', 14001)))
    puerto_send = int(os.getenv('PUERTO_SEND', puertos.get('selector_temperatura', 14000)))

    # Crear configuración
    config = ConfigUX(
        ip_raspberry=ip_raspberry,
        puerto_recv=puerto_recv,
        puerto_send=puerto_send,
        intervalo_recepcion_ms=ux_config.get('intervalo_recepcion_ms', 1000),
        intervalo_actualizacion_ui_ms=ux_config.get('intervalo_actualizacion_ui_ms', 100),
        temperatura_min_setpoint=ux_config.get('temperatura_minima_setpoint', 15.0),
        temperatura_max_setpoint=ux_config.get('temperatura_maxima_setpoint', 35.0),
        temperatura_setpoint_inicial=ux_config.get('temperatura_setpoint_inicial', 24.0),
    )

    logger.info(
        "Configuración cargada: IP=%s, Puerto Recv=%d, Puerto Send=%d",
        config.ip_raspberry,
        config.puerto_recv,
        config.puerto_send
    )

    return config


def crear_aplicacion() -> QApplication:
    """Crea la QApplication de Qt.

    Verifica si ya existe una instancia para evitar errores
    en entornos de testing.

    Returns:
        QApplication: Instancia de la aplicación Qt
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("UX Termostato")
    app.setOrganizationName("ISSE")

    logger.debug("QApplication creada: %s", app.applicationName())
    return app


def main():
    """Función principal de la aplicación.

    Orquesta:
    1. Carga de configuración
    2. Creación de QApplication
    3. Creación de Factory y VentanaPrincipalUX
    4. Inicio de la ventana
    5. Event loop

    Exit codes:
        0: Éxito o interrupción por usuario
        1: Error fatal
    """
    try:
        logger.info("=" * 60)
        logger.info("Iniciando UX Termostato Desktop v%s", VERSION)
        logger.info("PID: %d", os.getpid())
        logger.info("=" * 60)

        # 1. Cargar configuración
        config = cargar_configuracion()

        # 2. Crear QApplication
        app = crear_aplicacion()

        # 3. Crear Factory
        logger.info("Creando factory de componentes...")
        factory = ComponenteFactoryUX(config)

        # 4. Crear Ventana Principal
        logger.info("Creando ventana principal...")
        ventana = VentanaPrincipalUX(factory)

        # 5. Iniciar ventana (inicia servidor + muestra UI)
        logger.info("Iniciando ventana principal...")
        ventana.iniciar()

        logger.info("=" * 60)
        logger.info("✓ Aplicación iniciada correctamente")
        logger.info("  - Ventana mostrada")
        logger.info("  - Servidor escuchando en puerto %d", config.puerto_recv)
        logger.info("  - Cliente configurado para %s:%d", config.ip_raspberry, config.puerto_send)
        logger.info("=" * 60)
        logger.info("Event loop iniciado. Presione Ctrl+C para salir.")

        # 6. Event loop
        exit_code = app.exec()

        logger.info("Event loop finalizado con código %d", exit_code)
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Aplicación interrumpida por usuario (Ctrl+C)")
        logger.info("=" * 60)
        sys.exit(0)

    except Exception as e:  # pylint: disable=broad-except
        logger.error("=" * 60)
        logger.error("ERROR FATAL: %s", e, exc_info=True)
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
