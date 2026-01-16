# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2026-01-16

### Descripción

Primera versión estable del Simulador de Batería. Implementa arquitectura MVC con patrones Factory y Coordinator para comunicación con ISSE_Termostato vía TCP. Control manual de voltaje mediante slider con alta calidad de código (Pylint 9.94, MI 80.98, Coverage 96%).

### Agregado

- **Dominio**
  - `GeneradorBateria`: Generación de valores de voltaje en modo manual
  - `EstadoBateria`: Modelo de datos inmutable con validación de rango
  - Control manual por slider con rango 0.0V - 5.0V

- **Comunicación**
  - `ClienteBateria`: Cliente TCP efímero al puerto 11000
  - `ServicioEnvioBateria`: Integración generador + cliente con señales Qt
  - Soporte para envío síncrono y asíncrono
  - Formato de protocolo compatible con ISSE_Termostato

- **Presentación (MVC)**
  - `PanelEstado`: Visualización de voltaje actual, conexión y contadores de envíos
  - `PanelControl`: Slider de voltaje con precisión 0.1V
  - `PanelConexion`: Configuración IP/puerto y control de conexión
  - Clases base abstractas para MVC (`ModeloBase`, `VistaBase`, `ControladorBase`)

- **Arquitectura**
  - `ComponenteFactory`: Creación centralizada de componentes
  - `SimuladorCoordinator`: Gestión de señales entre componentes (Mediator pattern)
  - `UIPrincipalCompositor`: Composición de layout UI
  - Inyección de dependencias en todos los componentes

- **Configuración**
  - `ConfigManager`: Singleton para gestión de configuración
  - `ConfigSimuladorBateria`: Dataclass inmutable con configuración tipada
  - Soporte para `config.json` y variables de entorno
  - Valores por defecto para desarrollo local

- **Calidad**
  - **275 tests unitarios** con 96% de cobertura
  - Fixtures jerárquicas en `conftest.py` (5 niveles)
  - Mocks de PyQt6 y EphemeralSocketClient
  - Tests organizados por clase: `TestCreacion`, `TestMetodos`, `TestSignals`, `TestIntegracion`

- **Quality Gates**
  - Scripts de análisis: `calculate_metrics.py`, `validate_gates.py`
  - Pylint score: **9.94/10** (objetivo ≥ 8.0)
  - Complejidad ciclomática: **1.40** (objetivo ≤ 10)
  - Índice mantenibilidad: **80.98** (objetivo > 20)
  - **Grade A** en validación

- **Documentación**
  - `README.md` con instrucciones de uso y métricas
  - `docs/arquitectura.md` con diagramas UML completos
  - `docs/reporte_calidad_diseno.md` con análisis SOLID (9.6/10)
  - `docs/plan_tests_unitarios.md` con estrategia de testing

### Métricas

| Métrica | Valor |
|---------|-------|
| **Líneas de código (SLOC)** | 453 |
| **Archivos Python** | 19 |
| **Funciones** | 69 |
| **Tests** | 275 |
| **Coverage** | 96% |
| **Pylint** | 9.94/10 |
| **Complejidad Ciclomática** | 1.40 |
| **Índice Mantenibilidad** | 80.98 |
| **Quality Grade** | **A** |
| **SOLID Score** | 9.6/10 |

### Principios SOLID

| Principio | Calificación |
|-----------|--------------|
| Single Responsibility | 10/10 |
| Open/Closed | 9/10 |
| Liskov Substitution | 10/10 |
| Interface Segregation | 10/10 |
| Dependency Inversion | 9/10 |

### Cohesión y Acoplamiento

- **Cohesión:** 9.5/10 - Funcional en todos los componentes
- **Acoplamiento:** 9.0/10 - Bajo acoplamiento mediante inyección de dependencias

### Fases de Desarrollo

#### Fase 1: Dominio y Configuración
- Implementación de `GeneradorBateria` y `EstadoBateria`
- Sistema de configuración con `ConfigManager`
- Constantes y valores por defecto

#### Fase 2: Comunicación TCP
- `ClienteBateria` con patrón efímero
- `ServicioEnvioBateria` como integrador
- Integración con `EphemeralSocketClient` de `compartido/`

#### Fase 3: Presentación MVC
- Arquitectura MVC con clases base abstractas
- Panel Estado: visualización de voltaje y conexión
- Panel Control: slider manual de voltaje
- Panel Conexión: configuración de red

#### Fase 4: Integración y Factory/Coordinator
- `ComponenteFactory` para creación de componentes
- `SimuladorCoordinator` para desacoplar señales
- `UIPrincipalCompositor` para layout
- Corrección de bugs de integración

#### Fase 5: Testing y Quality Assurance
- **Fase 5.1:** 84 tests base + corrección de bugs críticos
- **Fase 5.2:** 108 tests adicionales (dominio, comunicación)
- **Fase 5.3:** Tests de presentación, objetivo 80% alcanzado
- **Fase 5.4:** 96% coverage final, quality gates aprobados

### Diferencias con Simulador Temperatura

| Aspecto | Temperatura | Batería |
|---------|-------------|---------|
| Modo | Manual + Automático | Solo Manual |
| Componente dominio | VariacionSenoidal | (No aplica) |
| Rango | -40°C a 85°C | 0.0V - 5.0V |
| Puerto TCP | 12000 | 11000 |
| Panel Gráfico | ✅ Sí | ❌ No |
| Paneles MVC | 4 | 3 |
| Pylint | 9.52 | **9.94** ⬆️ |
| MI | 70.10 | **80.98** ⬆️ |
| Coverage | ~95% | **96%** ⬆️ |

### Patrones de Diseño Aplicados

1. **Factory Pattern** - Creación centralizada de componentes
2. **Coordinator Pattern** - Mediator para señales PyQt
3. **MVC Pattern** - Separación modelo-vista-controlador
4. **Singleton Pattern** - ConfigManager con método `reiniciar()` para tests
5. **Observer Pattern** - Señales PyQt6 para comunicación asíncrona
6. **Compositor Pattern** - Composición de layout UI

---

## Plantilla para Futuras Versiones

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Agregado
- Nuevas funcionalidades

### Cambiado
- Cambios en funcionalidades existentes

### Obsoleto
- Funcionalidades que serán eliminadas

### Eliminado
- Funcionalidades eliminadas

### Corregido
- Corrección de errores

### Seguridad
- Correcciones de vulnerabilidades

### Métricas
| Métrica | Valor Anterior | Valor Actual | Cambio |
|---------|----------------|--------------|--------|
| Pylint | X.XX | X.XX | ±X.XX |
| Coverage | XX% | XX% | ±X% |
```

---

**Historial de Versiones:**
- `1.0.0` (2026-01-16) - Primera versión estable - Production Ready
