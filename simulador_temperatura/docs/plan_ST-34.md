# Plan de Implementación ST-34

## HU-2.3: Modelo de datos de temperatura

**Epic:** ST-31 - Simulador de Temperatura
**Estado:** En curso
**Prioridad:** Medium

---

## Descripción

Como desarrollador, quiero tener un modelo de datos que represente el estado de la temperatura para manejar la información de forma estructurada.

---

## Criterios de Aceptación

- [x] Dataclass `EstadoTemperatura` en `app/dominio/`
- [x] Atributo `temperatura`: float (temperatura actual en °C)
- [x] Atributo `timestamp`: datetime (momento de la lectura)
- [x] Atributo `en_rango`: bool (si está dentro de límites normales)
- [x] Método `to_string()` para formato de envío TCP (`"<float>\n"`)
- [x] Método `validar_rango()` según límites configurados
- [x] Tests unitarios para el modelo (14 tests)

---

## Pasos de Implementación

### Paso 1: Crear el modelo EstadoTemperatura

**Archivo:** `simulador_temperatura/app/dominio/estado_temperatura.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class EstadoTemperatura:
    temperatura: float
    timestamp: datetime = field(default_factory=datetime.now)
    en_rango: bool = True

    def to_string(self) -> str:
        """Formato para envío TCP."""
        return f"{self.temperatura:.1f}\n"

    def validar_rango(self, temp_min: float, temp_max: float) -> bool:
        """Valida si la temperatura está dentro del rango."""
        self.en_rango = temp_min <= self.temperatura <= temp_max
        return self.en_rango
```

### Paso 2: Actualizar exports del módulo dominio

**Archivo:** `simulador_temperatura/app/dominio/__init__.py`

- Importar y exportar `EstadoTemperatura`
- Agregar al `__all__`

### Paso 3: Crear tests unitarios

**Archivo:** `simulador_temperatura/tests/test_estado_temperatura.py`

Tests a implementar:
1. `test_crear_estado_temperatura` - Creación básica del dataclass
2. `test_timestamp_automatico` - Verificar que timestamp se genera automáticamente
3. `test_to_string_formato_correcto` - Formato `"23.5\n"`
4. `test_to_string_precision_decimal` - Verificar precisión de 1 decimal
5. `test_validar_rango_dentro` - Temperatura dentro de límites
6. `test_validar_rango_fuera_minimo` - Temperatura por debajo del mínimo
7. `test_validar_rango_fuera_maximo` - Temperatura por encima del máximo
8. `test_validar_rango_en_limite` - Temperatura exactamente en los límites

### Paso 4: Ejecutar tests y validar calidad

```bash
cd simulador_temperatura
pytest tests/test_estado_temperatura.py -v
pytest tests/ --cov=app --cov-report=html
python quality/scripts/calculate_metrics.py app
```

---

## Dependencias

| Componente | Archivo | Uso |
|------------|---------|-----|
| `temperatura_minima` | `config.py` | Límite inferior para validación |
| `temperatura_maxima` | `config.py` | Límite superior para validación |
| `TEMP_ABSOLUTA_MIN` | `constantes.py` | Límite técnico del sensor (-40°C) |
| `TEMP_ABSOLUTA_MAX` | `constantes.py` | Límite técnico del sensor (125°C) |

---

## Notas

- Se usa `app/dominio/` en lugar de `app/general/` para mantener consistencia con la estructura actual del proyecto
- El método `to_string()` usa precisión de 1 decimal según protocolo TCP definido
- El dataclass es mutable para permitir actualización de `en_rango` via `validar_rango()`

---

## Verificación Final

- [x] Tests pasan al 100% (14/14 passed)
- [x] Cobertura de código: 100% para EstadoTemperatura
- [x] Quality gates cumplidos - Calificación: **A**
  - Pylint: 9.88/10 (threshold >= 8.0)
  - Cyclomatic Complexity: 1.92 (threshold <= 10)
  - Maintainability Index: 87.49 (threshold > 20)
