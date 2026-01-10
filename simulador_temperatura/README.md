# Simulador de Temperatura

Cliente TCP para simulación de temperatura en tiempo real. Genera valores de temperatura simulados y los envía al sistema embebido ISSE_Termostato en Raspberry Pi.

## Descripción

El Simulador de Temperatura es parte del sistema HIL (Hardware-in-the-Loop) ISSE_Simuladores. Permite:

- Generar temperaturas con variación senoidal configurable
- Control manual de temperatura
- Visualización en tiempo real con gráfico
- Conexión TCP al puerto 12000 del termostato

```
┌─────────────────────────────┐         ┌─────────────────────┐
│  Simulador de Temperatura   │  TCP    │  ISSE_Termostato    │
│  (PyQt6 Desktop)            │────────▶│  (Raspberry Pi)     │
│                             │ :12000  │                     │
└─────────────────────────────┘         └─────────────────────┘
```

## Requisitos

- Python 3.12+
- PyQt6 6.7.0
- pyqtgraph 0.13.3

## Instalación

```bash
# Desde el directorio raíz del proyecto
cd simulador_temperatura

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
| **Estado** | Muestra temperatura actual, modo (auto/manual), estado conexión |
| **Control** | Ajusta amplitud, período, temperatura base o modo manual |
| **Gráfico** | Visualización en tiempo real de la temperatura |
| **Conexión** | Configura IP y puerto, botones conectar/desconectar |

### Modos de Operación

**Modo Automático (Senoidal)**
```
T(t) = T_base + Amplitud × sin(2π × t / Período)
```

**Modo Manual**
- Temperatura fija definida por el usuario

## Arquitectura

El proyecto implementa una arquitectura en capas con patrones MVC, Factory y Coordinator.

```
simulador_temperatura/
├── run.py                    # Entry point
├── app/
│   ├── factory.py            # Creación de componentes
│   ├── coordinator.py        # Conexión de señales
│   ├── configuracion/        # ConfigManager
│   ├── dominio/              # GeneradorTemperatura, VariacionSenoidal
│   ├── comunicacion/         # ClienteTemperatura, ServicioEnvio
│   └── presentacion/         # UI + Paneles MVC
│       └── paneles/          # Estado, Control, Gráfico, Conexión
├── tests/                    # 283 tests unitarios
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
pytest tests/test_generador_temperatura.py -v
```

## Calidad de Código

```bash
# Calcular métricas
python quality/scripts/calculate_metrics.py app

# Validar quality gates
python quality/scripts/validate_gates.py quality/reports/quality_*.json

# Generar reporte
python quality/scripts/generate_report.py quality/reports/quality_*.json
```

### Métricas Actuales

| Métrica | Valor | Umbral |
|---------|-------|--------|
| Pylint Score | 9.52/10 | ≥ 8.0 |
| Complejidad Ciclomática | 1.36 | ≤ 10 |
| Índice Mantenibilidad | 70.10 | > 20 |
| Tests | 283 | - |
| Grade | A | - |

## Protocolo de Comunicación

```
Formato:    "<temperatura>\n"
Ejemplo:    "23.50\n"
Encoding:   UTF-8
Puerto:     12000
Patrón:     Efímero (conectar → enviar → cerrar)
```

## Configuración

### config.json
```json
{
  "ip_raspberry": "192.168.1.100",
  "puerto": 12000,
  "intervalo_envio_ms": 1000,
  "temperatura_inicial": 22.0,
  "variacion_amplitud": 5.0,
  "variacion_periodo": 60.0
}
```

### Variables de Entorno (.env)
```
RASPBERRY_IP=192.168.1.100
RASPBERRY_PORT=12000
```

## Documentación

- [Arquitectura Detallada](docs/arquitectura.md)
- [Informe de Calidad de Diseño](quality/reports/informe_calidad_diseno.md)

## Contribución

Este proyecto sigue los quality gates definidos:
- Pylint ≥ 8.0
- Complejidad Ciclomática promedio ≤ 10
- Índice de Mantenibilidad > 20

Ejecutar tests y quality checks antes de cada commit.

## Licencia

Proyecto interno ISSE - Universidad Nacional de San Luis
