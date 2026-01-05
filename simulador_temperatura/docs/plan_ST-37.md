# Plan de Implementación ST-37

## HU-2.6: Generador de valores de temperatura

**Epic:** ST-31 - Simulador de Temperatura
**Estado:** En curso
**Prioridad:** Medium

---

## Descripción

Como desarrollador, quiero tener un generador de valores de temperatura que integre la variación senoidal para producir valores simulados continuamente.

---

## Criterios de Aceptación

- [x] Clase `GeneradorTemperatura` en `app/dominio/`
- [x] Integra `VariacionSenoidal` (sin RuidoTermico por decisión de diseño)
- [x] Propiedad `temperatura_base` configurable
- [x] Método `set_temperatura_manual(temp)` para override manual
- [x] Método `generar_valor()` que retorna `EstadoTemperatura`
- [x] Señales Qt: `valor_generado`, `temperatura_cambiada`
- [x] Timer interno configurable para generación periódica
- [x] Modo automático (senoidal) y modo manual
- [x] Tests unitarios para cada modo (18 tests)

---

## Análisis Técnico

### Arquitectura

```
GeneradorTemperatura (QObject)
    │
    ├── VariacionSenoidal (ST-35) ✓
    │       └── calcular_temperatura(t) → float
    │
    ├── EstadoTemperatura (ST-34) ✓
    │       └── Encapsula resultado
    │
    └── ConfigSimuladorTemperatura
            └── Parámetros de configuración
```

### Modos de operación

| Modo | Descripción | Fuente de temperatura |
|------|-------------|----------------------|
| Automático | Variación senoidal continua | `VariacionSenoidal.calcular_temperatura(t)` |
| Manual | Valor fijo definido por usuario | `temperatura_manual` |

### Señales Qt

| Señal | Parámetro | Cuándo se emite |
|-------|-----------|-----------------|
| `valor_generado` | `EstadoTemperatura` | Cada vez que se genera un valor |
| `temperatura_cambiada` | `float` | Cuando cambia la temperatura (manual o auto) |

---

## Pasos de Implementación

### Paso 1: Crear la clase GeneradorTemperatura

**Archivo:** `simulador_temperatura/app/dominio/generador_temperatura.py`

```python
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from .estado_temperatura import EstadoTemperatura
from .variacion_senoidal import VariacionSenoidal

class GeneradorTemperatura(QObject):
    valor_generado = pyqtSignal(EstadoTemperatura)
    temperatura_cambiada = pyqtSignal(float)

    def __init__(self, config, parent=None):
        ...

    def iniciar(self) -> None
    def detener(self) -> None
    def generar_valor(self) -> EstadoTemperatura
    def set_temperatura_manual(self, temp: float) -> None
    def set_modo_automatico(self) -> None

    @property
    def modo_manual(self) -> bool
    @property
    def temperatura_actual(self) -> float
```

### Paso 2: Actualizar exports del módulo dominio

**Archivo:** `simulador_temperatura/app/dominio/__init__.py`

- Importar y exportar `GeneradorTemperatura`

### Paso 3: Crear tests unitarios

**Archivo:** `simulador_temperatura/tests/test_generador_temperatura.py`

Tests a implementar:

**Creación y configuración:**
1. `test_crear_generador` - Creación básica
2. `test_modo_inicial_automatico` - Verifica modo automático por defecto

**Modo automático:**
3. `test_generar_valor_automatico` - Genera valor con variación senoidal
4. `test_generar_valor_retorna_estado_temperatura` - Tipo correcto
5. `test_temperatura_varia_con_tiempo` - Valores diferentes en tiempos diferentes

**Modo manual:**
6. `test_set_temperatura_manual` - Cambia a modo manual
7. `test_generar_valor_manual` - Retorna temperatura manual
8. `test_set_modo_automatico` - Vuelve a modo automático

**Señales:**
9. `test_signal_valor_generado` - Emite señal con valor
10. `test_signal_temperatura_cambiada` - Emite señal cuando cambia

**Timer:**
11. `test_iniciar_timer` - Inicia generación periódica
12. `test_detener_timer` - Detiene generación

### Paso 4: Ejecutar tests y validar calidad

```bash
cd simulador_temperatura
pytest tests/test_generador_temperatura.py -v
pytest tests/ --cov=app --cov-report=html
python quality/scripts/calculate_metrics.py app
```

---

## Dependencias

| Componente | Archivo | Estado |
|------------|---------|--------|
| `EstadoTemperatura` | `estado_temperatura.py` | ✓ Implementado (ST-34) |
| `VariacionSenoidal` | `variacion_senoidal.py` | ✓ Implementado (ST-35) |
| `ConfigSimuladorTemperatura` | `config.py` | ✓ Existente |
| `PyQt6.QtCore` | Externa | ✓ Instalada |

---

## Configuración utilizada

```python
# Desde ConfigSimuladorTemperatura
intervalo_envio_ms: int          # Intervalo del timer
temperatura_inicial: float       # T_base para VariacionSenoidal
temperatura_minima: float        # Para validar_rango()
temperatura_maxima: float        # Para validar_rango()
variacion_amplitud: float        # Amplitud senoidal
variacion_periodo_segundos: float # Período senoidal
```

---

## Notas

- Se usa `app/dominio/` para mantener consistencia con ST-34 y ST-35
- No se implementa RuidoTermico (ST-36) por decisión de diseño
- El GeneradorTemperatura hereda de QObject para soportar señales Qt
- El timer usa el intervalo de `intervalo_envio_ms` de la configuración
- Los tests de señales Qt requieren `pytest-qt` (ya instalado)

---

## Verificación Final

- [x] Tests pasan al 100% (45/45 passed - incluye ST-34, ST-35)
- [x] Cobertura de código: 100% para GeneradorTemperatura
- [x] Quality gates cumplidos - Calificación: **A**
  - Pylint: 8.95/10 (threshold >= 8.0)
  - Cyclomatic Complexity: 1.59 (threshold <= 10)
  - Maintainability Index: 81.20 (threshold > 20)
