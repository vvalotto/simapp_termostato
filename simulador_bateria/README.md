# Simulador de Batería

Cliente TCP para simulación de voltaje de batería en tiempo real. Genera valores de voltaje simulados mediante control manual (slider) y los envía al sistema embebido ISSE_Termostato en Raspberry Pi.

## Descripción

El Simulador de Batería es parte del sistema HIL (Hardware-in-the-Loop) ISSE_Simuladores. Permite:

- Control manual de voltaje mediante slider (0.0V - 5.0V)
- Visualización de voltaje actual y estado de conexión
- Monitoreo de envíos exitosos y fallidos
- Conexión TCP al puerto 11000 del termostato

```
┌─────────────────────────────┐         ┌─────────────────────┐
│  Simulador de Batería       │  TCP    │  ISSE_Termostato    │
│  (PyQt6 Desktop)            │────────▶│  (Raspberry Pi)     │
│                             │ :11000  │                     │
└─────────────────────────────┘         └─────────────────────┘
```

## Requisitos

- Python 3.12+
- PyQt6 6.7.0

## Instalación

```bash
# Desde el directorio raíz del proyecto
cd simulador_bateria

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r ../requirements.txt

# Configurar conexión
cp ../.env.example ../.env
# Editar .env con la IP de tu Raspberry Pi
```

## Uso

```bash
# Ejecutar aplicación
python run.py
```

### Interfaz de Usuario

| Panel | Función |
|-------|---------|
| **Estado** | Muestra voltaje actual, estado conexión, envíos exitosos/fallidos |
| **Control** | Slider para ajustar voltaje manualmente (0.0V - 5.0V) |
| **Conexión** | Configura IP y puerto, botones conectar/desconectar |

### Modo de Operación

**Modo Manual (Slider)**
- Voltaje controlado directamente por el usuario
- Rango: 0.0V a 5.0V (sensor ADC de batería)
- Precisión: 0.1V

## Arquitectura

El proyecto implementa una arquitectura en capas con patrones MVC, Factory y Coordinator.

```
simulador_bateria/
├── run.py                    # Entry point
├── app/
│   ├── factory.py            # Creación de componentes
│   ├── coordinator.py        # Conexión de señales
│   ├── configuracion/        # ConfigManager
│   ├── dominio/              # GeneradorBateria, EstadoBateria
│   ├── comunicacion/         # ClienteBateria, ServicioEnvio
│   └── presentacion/         # UI + Paneles MVC
│       └── paneles/          # Estado, Control, Conexión
├── tests/                    # 275 tests unitarios (96% coverage)
├── quality/                  # Scripts de análisis
└── docs/                     # Documentación técnica
```

### Patrones Implementados

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **MVC** | `presentacion/paneles/` | Separación Modelo-Vista-Controlador |
| **Factory** | `factory.py` | Creación centralizada de componentes |
| **Coordinator** | `coordinator.py` | Gestión de señales PyQt6 |
| **Compositor** | `ui_compositor.py` | Composición de layout UI |

## Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html

# Test específico
pytest tests/test_generador_bateria.py -v

# Tests por clase
pytest tests/test_generador_bateria.py::TestGeneradorBateria -v
```

## Calidad de Código

```bash
# Calcular métricas
python quality/scripts/calculate_metrics.py app

# Validar quality gates
python quality/scripts/validate_gates.py quality/reports/quality_*.json

# Análisis con pylint
pylint app/
```

### Métricas Actuales

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| **Pylint Score** | 9.94/10 | ≥ 8.0 | ✅ |
| **Complejidad Ciclomática** | 1.40 | ≤ 10 | ✅ |
| **Índice Mantenibilidad** | 80.98 | > 20 | ✅ |
| **Coverage** | 96% | - | ✅ |
| **Tests** | 275 | - | ✅ |
| **Grade** | **A** | - | ✅ |

### Evaluación SOLID

| Principio | Calificación |
|-----------|--------------|
| Single Responsibility | 10/10 |
| Open/Closed | 9/10 |
| Liskov Substitution | 10/10 |
| Interface Segregation | 10/10 |
| Dependency Inversion | 9/10 |
| **TOTAL** | **9.6/10** |

## Protocolo de Comunicación

```
Formato:    "<voltaje>\n"
Ejemplo:    "4.20\n"  (batería llena)
            "3.50\n"  (batería media)
            "2.80\n"  (batería baja)
Encoding:   UTF-8
Puerto:     11000
Patrón:     Efímero (conectar → enviar → cerrar)
Rango:      0.0V - 5.0V
```

## Configuración

### config.json
```json
{
  "raspberry_pi": {
    "ip": "192.168.1.100"
  },
  "puertos": {
    "bateria": 11000
  },
  "simulador_bateria": {
    "intervalo_envio_ms": 1000,
    "voltaje_minimo": 0.0,
    "voltaje_maximo": 5.0,
    "voltaje_inicial": 4.2
  }
}
```

### Variables de Entorno (.env)
```
RASPBERRY_IP=192.168.1.100
DEBUG=false
```

## Documentación

- [Arquitectura Detallada](docs/arquitectura.md)
- [Reporte de Calidad de Diseño](docs/reporte_calidad_diseno.md)
- [Plan de Tests Unitarios](docs/plan_tests_unitarios.md)

## Comparación con Simulador Temperatura

| Aspecto | Temperatura | Batería |
|---------|-------------|---------|
| **Modo** | Manual + Automático | Solo Manual |
| **Rango** | -40°C a 85°C | 0.0V - 5.0V |
| **Puerto** | 12000 | 11000 |
| **Panel Gráfico** | ✅ Sí | ❌ No |
| **Pylint** | 9.52 | **9.94** |
| **MI** | 70.10 | **80.98** |
| **Coverage** | ~95% | **96%** |

## Contribución

Este proyecto sigue los quality gates definidos:
- Pylint ≥ 8.0
- Complejidad Ciclomática promedio ≤ 10
- Índice de Mantenibilidad > 20
- Coverage ≥ 80%

Ejecutar tests y quality checks antes de cada commit.

## Licencia

Proyecto interno ISSE - Universidad Nacional de San Luis

---

**Versión:** 1.0.0
**Estado:** ✅ Production Ready
**Última actualización:** 2026-01-16
