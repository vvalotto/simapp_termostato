# Plan de Implementación - US-020: Capa de Dominio

**Historia:** Como desarrollador del sistema quiero definir modelo de dominio
**Puntos:** 5
**Prioridad:** CRÍTICA
**Estado:** ✅ COMPLETADO

---

## Descripción

Implementar la capa de dominio con:
- `EstadoTermostato`: dataclass inmutable que representa el estado completo del termostato
- Jerarquía de comandos: clases para representar acciones del usuario

**Principio:** Esta es lógica de negocio pura - sin PyQt, sin I/O, solo datos y validaciones.

---

## Componentes a Implementar

### 1. EstadoTermostato (`dominio/estado_termostato.py`)

**Responsabilidades:**
- Representar estado completo del termostato recibido del RPi
- Validar rangos de temperatura y valores de enums
- Serialización/deserialización JSON ↔ objeto Python

**Atributos:**
```python
temperatura_actual: float      # -40°C a 85°C
temperatura_deseada: float     # 15°C a 35°C
modo_climatizador: str         # "calentando" | "enfriando" | "reposo" | "apagado"
falla_sensor: bool
bateria_baja: bool
encendido: bool
modo_display: str              # "ambiente" | "deseada"
timestamp: datetime
```

**Métodos:**
- `from_json(data: dict) -> EstadoTermostato`: parsear JSON del RPi
- `to_dict() -> dict`: serialización para logging/debugging
- Validaciones automáticas en `__post_init__`

---

### 2. Comandos (`dominio/comandos.py`)

**Jerarquía:**
```
ComandoTermostato (ABC)
├── ComandoPower(estado: bool)
├── ComandoSetTemp(valor: float)
└── ComandoSetModoDisplay(modo: str)
```

**Cada comando debe:**
- Ser inmutable (frozen=True)
- Tener timestamp automático
- Implementar `to_json() -> dict` para envío al RPi
- Validar sus parámetros

---

### 3. Exports (`dominio/__init__.py`)

Exponer API pública del módulo:
```python
from .estado_termostato import EstadoTermostato
from .comandos import (
    ComandoTermostato,
    ComandoPower,
    ComandoSetTemp,
    ComandoSetModoDisplay,
)

__all__ = [
    "EstadoTermostato",
    "ComandoTermostato",
    "ComandoPower",
    "ComandoSetTemp",
    "ComandoSetModoDisplay",
]
```

---

## Tasks

### Implementación

- [x] **EstadoTermostato** (~1h) ✅
  - Dataclass con todos los atributos
  - Validaciones de rangos en `__post_init__`
  - Método `from_json()`
  - Método `to_dict()`

- [x] **Comandos** (~1h) ✅
  - Clase base `ComandoTermostato`
  - `ComandoPower`
  - `ComandoSetTemp`
  - `ComandoSetModoDisplay`
  - Validaciones específicas
  - Fix: `timestamp` con `kw_only=True` para evitar conflicto de parámetros

- [x] **__init__.py** (~5min) ✅
  - Exports públicos

### Tests Unitarios

- [x] **test_estado_termostato.py** (~1.5h) ✅ **22 tests**
  - `TestCreacion`: constructor y valores por defecto (3 tests)
  - `TestValidaciones`: rangos de temperatura, valores de enum (10 tests)
  - `TestFromJson`: parsing correcto, campos opcionales, errores (5 tests)
  - `TestToDict`: serialización correcta (2 tests)
  - `TestInmutabilidad`: frozen=True funciona (2 tests)

- [x] **test_comandos.py** (~1.5h) ✅ **27 tests**
  - `TestComandoBase`: clase abstracta no se puede instanciar (2 tests)
  - `TestComandoPower`: creación, to_json, validaciones (6 tests)
  - `TestComandoSetTemp`: validación rango 15-35°C, to_json (7 tests)
  - `TestComandoSetModoDisplay`: validación modo válido, to_json (5 tests)
  - `TestInmutabilidadComandos`: todos los comandos son frozen (5 tests)
  - `TestTimestampISO`: serialización timestamp ISO (2 tests)

---

## Quality Gates

- **Coverage:** ≥ 95%
- **Pylint:** ≥ 8.0
- **Complejidad:** CC ≤ 10
- **Type hints:** 100%

---

## Estimación

**Total:** ~5 horas
- Implementación: 2h
- Tests: 3h

---

## Notas de Implementación

### Validaciones de EstadoTermostato

```python
def __post_init__(self):
    # Temperatura actual: rango sensor
    if not -40 <= self.temperatura_actual <= 85:
        raise ValueError(f"temperatura_actual fuera de rango: {self.temperatura_actual}")

    # Temperatura deseada: rango operativo
    if not 15 <= self.temperatura_deseada <= 35:
        raise ValueError(f"temperatura_deseada fuera de rango: {self.temperatura_deseada}")

    # Modo climatizador
    if self.modo_climatizador not in ["calentando", "enfriando", "reposo", "apagado"]:
        raise ValueError(f"modo_climatizador inválido: {self.modo_climatizador}")

    # Modo display
    if self.modo_display not in ["ambiente", "deseada"]:
        raise ValueError(f"modo_display inválido: {self.modo_display}")
```

### Formato JSON del RPi (Referencia)

```json
{
  "temperatura_actual": 22.5,
  "temperatura_deseada": 24.0,
  "modo_climatizador": "calentando",
  "falla_sensor": false,
  "bateria_baja": false,
  "encendido": true,
  "modo_display": "ambiente",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

### Formato JSON de Comandos (Para RPi)

**ComandoPower:**
```json
{
  "comando": "power",
  "estado": "on",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

**ComandoSetTemp:**
```json
{
  "comando": "set_temp_deseada",
  "valor": 24.5,
  "timestamp": "2026-01-23T10:30:00Z"
}
```

**ComandoSetModoDisplay:**
```json
{
  "comando": "set_modo_display",
  "modo": "deseada",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

---

## Checklist de Progreso

### Implementación
- [x] estado_termostato.py
- [x] comandos.py
- [x] __init__.py

### Tests
- [x] test_estado_termostato.py (22 tests)
- [x] test_comandos.py (27 tests)

### Quality
- [x] Coverage = 100% (64/64 statements) ✅
- [x] Pylint = 10.00/10 ✅
- [x] CC Promedio = 2.29 ✅ (límite: ≤10)
- [x] MI Promedio = 82.50 ✅ (límite: >20)
- [x] Tests pasan (49/49 ✅)

---

## Resultados Finales

### ✅ Implementación Completada

**Archivos creados:**
- `app/dominio/estado_termostato.py` (128 líneas)
- `app/dominio/comandos.py` (146 líneas)
- `app/dominio/__init__.py` (21 líneas)
- `tests/test_estado_termostato.py` (398 líneas)
- `tests/test_comandos.py` (289 líneas)

**Métricas de Calidad:**
- **Tests:** 49/49 ✅ (22 + 27)
- **Coverage:** 100% (64/64 statements) ✅
- **Pylint:** 10.00/10 ✅
- **CC Promedio:** 2.29 ✅ (objetivo: ≤10)
- **MI Promedio:** 82.50 ✅ (objetivo: >20)

**Estadísticas de Código:**
- **Código:** 295 líneas
- **Tests:** 687 líneas
- **Ratio tests/código:** 2.3:1

**Quality Gates:** ✅ **TODOS CUMPLIDOS**

### Issues Encontrados y Resueltos

**Problema:** Error de ordenamiento de parámetros en dataclasses
```
TypeError: non-default argument 'estado' follows default argument 'timestamp'
```

**Solución:** Usar `kw_only=True` en el field del timestamp:
```python
timestamp: datetime = field(default_factory=datetime.now, kw_only=True)
```

Esto permite que las subclases definan parámetros posicionales sin conflicto.

---

## Próximos Pasos

Una vez completado US-020:
- ✅ Tendremos modelo de dominio compartido
- ➡️ US-021: Implementar comunicación (usa EstadoTermostato y comandos)
- ➡️ Todos los paneles podrán usar EstadoTermostato en vez de modelos propios
