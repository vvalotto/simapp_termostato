"""Tests unitarios para el Simulador de Batería.

Esta suite de tests cubre todas las capas del simulador:
- Dominio: EstadoBateria, GeneradorBateria
- Comunicación: ClienteBateria, ServicioEnvioBateria
- Configuración: ConfigSimuladorBateria, ConfigManager
- Presentación MVC: Modelos, Vistas, Controladores
- Orquestación: ComponenteFactory, SimuladorCoordinator

Ejecutar tests:
    pytest tests/ -v
    pytest tests/ --cov=app --cov-report=html

Coverage objetivo: ≥80%
"""
