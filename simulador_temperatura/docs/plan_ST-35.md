# Plan de Implementación ST-35

## HU-2.4: Lógica de variación senoidal

**Epic:** ST-31 - Simulador de Temperatura
**Estado:** Por hacer
**Prioridad:** Medium

---

## Descripción

Como desarrollador, quiero implementar la lógica de variación senoidal para simular cambios naturales de temperatura a lo largo del tiempo.

---

## Criterios de Aceptación

- [x] Clase `VariacionSenoidal` en `app/dominio/`
- [x] Algoritmo basado en función seno: `T(t) = T_base + A * sin(2π * t / P)`
- [x] Parámetro de amplitud configurable (A)
- [x] Parámetro de período configurable (P en segundos)
- [x] Parámetro de temperatura base configurable
- [x] Método `calcular_temperatura(tiempo_actual)`
- [x] Simulación de ciclo día/noche si se desea
- [x] Tests unitarios validando la curva senoidal (13 tests)

---

## Análisis Técnico

### Fórmula matemática

```
T(t) = T_base + A * sin(2π * t / P)

Donde:
- T(t)   = Temperatura en el tiempo t
- T_base = Temperatura base (centro de la oscilación)
- A      = Amplitud (máxima desviación respecto a T_base)
- P      = Período (tiempo para completar un ciclo completo)
- t      = Tiempo transcurrido en segundos
```

### Ejemplo de ciclo día/noche

```
T_base = 20°C
A = 5°C
P = 86400 segundos (24 horas)

Resultado: Oscila entre 15°C y 25°C en un ciclo de 24 horas
```

### Parámetros de configuración actuales

| Parámetro | Valor actual | Uso propuesto |
|-----------|--------------|---------------|
| `temperatura_inicial` | 20.0 | T_base |
| `paso_variacion` | 0.1 | (no aplica) |

### Nuevos parámetros necesarios en config.json

```json
"simulador_temperatura": {
    ...
    "variacion_amplitud": 5.0,
    "variacion_periodo_segundos": 60.0
}
```

---

## Pasos de Implementación

### Paso 1: Actualizar constantes y configuración

**Archivo:** `simulador_temperatura/app/configuracion/constantes.py`

Agregar:
```python
DEFAULT_VARIACION_AMPLITUD: float = 5.0
DEFAULT_VARIACION_PERIODO: float = 60.0  # segundos
```

**Archivo:** `simulador_temperatura/app/configuracion/config.py`

Agregar campos a `ConfigSimuladorTemperatura`:
```python
variacion_amplitud: float
variacion_periodo_segundos: float
```

### Paso 2: Crear la clase VariacionSenoidal

**Archivo:** `simulador_temperatura/app/dominio/variacion_senoidal.py`

```python
import math
from dataclasses import dataclass

@dataclass
class VariacionSenoidal:
    temperatura_base: float
    amplitud: float
    periodo_segundos: float

    def calcular_temperatura(self, tiempo_segundos: float) -> float:
        """Calcula la temperatura en el tiempo dado."""
        angulo = 2 * math.pi * tiempo_segundos / self.periodo_segundos
        return self.temperatura_base + self.amplitud * math.sin(angulo)
```

### Paso 3: Actualizar exports del módulo dominio

**Archivo:** `simulador_temperatura/app/dominio/__init__.py`

- Importar y exportar `VariacionSenoidal`

### Paso 4: Crear tests unitarios

**Archivo:** `simulador_temperatura/tests/test_variacion_senoidal.py`

Tests a implementar:
1. `test_temperatura_en_tiempo_cero` - Debe retornar T_base (sin(0) = 0)
2. `test_temperatura_en_cuarto_periodo` - Debe retornar T_base + A (sin(π/2) = 1)
3. `test_temperatura_en_medio_periodo` - Debe retornar T_base (sin(π) = 0)
4. `test_temperatura_en_tres_cuartos_periodo` - Debe retornar T_base - A (sin(3π/2) = -1)
5. `test_temperatura_en_periodo_completo` - Debe retornar T_base (sin(2π) = 0)
6. `test_rango_temperatura` - Verificar que siempre está entre T_base ± A
7. `test_periodicidad` - Verificar T(t) == T(t + P)

### Paso 5: Ejecutar tests y validar calidad

```bash
cd simulador_temperatura
pytest tests/test_variacion_senoidal.py -v
pytest tests/ --cov=app --cov-report=html
python quality/scripts/calculate_metrics.py app
```

---

## Dependencias

| Componente | Archivo | Uso |
|------------|---------|-----|
| `temperatura_inicial` | `config.py` | Valor por defecto para T_base |
| `EstadoTemperatura` | `estado_temperatura.py` | Se usará para encapsular resultado |
| `math.sin`, `math.pi` | stdlib | Cálculo senoidal |

---

## Integración futura

Esta clase será usada por `GeneradorTemperatura` (ticket futuro):

```python
class GeneradorTemperatura:
    def __init__(self, variacion: VariacionSenoidal):
        self.variacion = variacion
        self.tiempo_inicio = time.time()

    def generar(self) -> EstadoTemperatura:
        tiempo = time.time() - self.tiempo_inicio
        temp = self.variacion.calcular_temperatura(tiempo)
        estado = EstadoTemperatura(temperatura=temp)
        estado.validar_rango(self.config.temp_min, self.config.temp_max)
        return estado
```

---

## Notas

- Se usa `app/dominio/` para mantener consistencia con ST-34
- El período por defecto de 60 segundos facilita las pruebas (ciclo rápido)
- Para simular día/noche real, usar período de 86400 segundos (24 horas)
- La clase es inmutable (dataclass) y stateless (no guarda tiempo interno)

---

## Verificación Final

- [x] Tests pasan al 100% (27/27 passed - incluye ST-34)
- [x] Cobertura de código: 100% para VariacionSenoidal
- [x] Quality gates cumplidos - Calificación: **A**
  - Pylint: 9.90/10 (threshold >= 8.0)
  - Cyclomatic Complexity: 1.76 (threshold <= 10)
  - Maintainability Index: 83.75 (threshold > 20)
- [x] Configuración actualizada con nuevos parámetros
