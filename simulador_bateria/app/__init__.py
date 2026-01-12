"""Simulador de Batería - Aplicación principal.

Arquitectura MVC con patrones Factory, Coordinator y Compositor.

Módulos:
- configuracion/: Configuración del simulador
- dominio/: Lógica de negocio (GeneradorBateria, EstadoBateria)
- comunicacion/: Cliente TCP y servicio de envío
- presentacion/: UI con paneles MVC
"""
from app.factory import ComponenteFactory
from app.coordinator import SimuladorCoordinator

__all__ = ['ComponenteFactory', 'SimuladorCoordinator']
