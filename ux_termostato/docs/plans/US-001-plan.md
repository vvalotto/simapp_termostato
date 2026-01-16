# Plan de Implementación: US-001 - Ver temperatura ambiente actual

## Información de la Historia

**US:** US-001
**Título:** Ver temperatura ambiente actual
**Prioridad:** Alta
**Puntos:** 3
**Producto:** ux_termostato
**Fecha inicio:** 2026-01-16
**Estado:** EN PROGRESO

---

## Resumen

**Como** usuario del termostato
**Quiero** ver la temperatura ambiente actual en un display grande y claro
**Para** conocer en todo momento las condiciones de mi hogar

---

## Componentes a Implementar

### 1. Panel Display - MVC Completo

#### 1.1 DisplayModelo (Modelo de datos)

**Ubicación:** `app/presentacion/paneles/display/modelo.py`
**Patrón:** Dataclass inmutable (frozen=True)
**Estimación:** 10 min

**Responsabilidad:**
- Almacenar estado del display: temperatura, modo_vista, encendido, error_sensor

**Tareas:**
- [ ] Crear archivo con estructura base
- [ ] Definir dataclass DisplayModelo
- [ ] Agregar campos: temperatura, modo_vista, encendido, error_sensor
- [ ] Implementar método validación (opcional)
- [ ] Agregar docstrings

**Referencia:** Ver `simulador_bateria/app/presentacion/paneles/estado/modelo.py`

---

#### 1.2 DisplayVista (Vista UI)

**Ubicación:** `app/presentacion/paneles/display/vista.py`
**Patrón:** QWidget puro, sin lógica
**Estimación:** 25 min

**Responsabilidad:**
- Renderizar display LCD con temperatura
- Mostrar label superior (modo)
- Aplicar estilos (fondo verde LCD, fuente grande)

**Tareas:**
- [ ] Crear archivo con estructura base
- [ ] Heredar de VistaBase (o QWidget)
- [ ] Crear widgets:
  - label_modo (QLabel para "Temperatura Ambiente")
  - label_temp (QLabel para valor, fuente 48px+)
  - label_unidad (QLabel para "°C")
  - label_error (QLabel para "ERROR", oculto por defecto)
- [ ] Implementar método actualizar(modelo: DisplayModelo)
- [ ] Aplicar stylesheet (fondo verde #065f46, texto claro)
- [ ] Agregar docstrings

**Referencia:** Ver widgets en `compartido/widgets/` para inspiración de estilos

---

#### 1.3 DisplayControlador (Lógica de presentación)

**Ubicación:** `app/presentacion/paneles/display/controlador.py`
**Patrón:** QObject, coordina modelo ↔ vista, emite señales
**Estimación:** 20 min

**Responsabilidad:**
- Actualizar modelo cuando cambia temperatura
- Llamar vista.actualizar() cuando modelo cambia
- Emitir señales para otros componentes
- Manejar cambios de modo vista (ambiente/deseada)

**Tareas:**
- [ ] Crear archivo con estructura base
- [ ] Heredar de ControladorBase (o QObject)
- [ ] Implementar métodos:
  - actualizar_temperatura(temp: float)
  - cambiar_modo_vista(modo: str)
  - set_encendido(encendido: bool)
  - set_error_sensor(error: bool)
- [ ] Definir señales (si aplica)
- [ ] Agregar docstrings

**Referencia:** Ver `simulador_bateria/app/presentacion/paneles/estado/controlador.py`

---

#### 1.4 Archivo __init__.py

**Ubicación:** `app/presentacion/paneles/display/__init__.py`
**Estimación:** 2 min

**Tareas:**
- [ ] Crear archivo
- [ ] Exportar DisplayModelo, DisplayVista, DisplayControlador

---

### 2. Estructura de Directorios

**Estimación:** 3 min

**Tareas:**
- [ ] Crear `app/presentacion/paneles/display/`
- [ ] Crear `tests/` si no existe
- [ ] Crear `tests/features/` si no existe

---

## Tests

### 3. Tests Unitarios - DisplayModelo

**Ubicación:** `tests/test_display_modelo.py`
**Estimación:** 15 min

**Tareas:**
- [ ] Clase TestCreacion
  - test_crear_con_valores_default
  - test_crear_con_valores_custom
- [ ] Clase TestInmutabilidad
  - test_es_inmutable (frozen=True)
- [ ] Clase TestValidacion (si aplica)

---

### 4. Tests Unitarios - DisplayVista

**Ubicación:** `tests/test_display_vista.py`
**Estimación:** 20 min

**Tareas:**
- [ ] Clase TestCreacion (con qapp fixture)
  - test_crear_vista
  - test_widgets_existen
- [ ] Clase TestActualizacion
  - test_actualizar_con_temperatura_normal
  - test_actualizar_con_error_sensor
  - test_actualizar_cuando_apagado
  - test_cambio_de_modo (ambiente/deseada)
- [ ] Clase TestEstilos
  - test_fuente_grande (≥48px)
  - test_fondo_verde_lcd

---

### 5. Tests Unitarios - DisplayControlador

**Ubicación:** `tests/test_display_controlador.py`
**Estimación:** 20 min

**Tareas:**
- [ ] Clase TestCreacion
  - test_crear_controlador
  - test_modelo_inicial
  - test_vista_asociada
- [ ] Clase TestMetodos
  - test_actualizar_temperatura
  - test_cambiar_modo_vista
  - test_set_encendido
  - test_set_error_sensor
- [ ] Clase TestSignals (si aplica)
  - test_emite_signal_al_cambiar

---

### 6. Tests de Integración

**Ubicación:** `tests/test_display_integracion.py`
**Estimación:** 25 min

**Tareas:**
- [ ] TestIntegracion
  - test_flujo_completo_modelo_vista_controlador
  - test_actualizacion_desde_servidor_simulado
  - test_cambio_estado_encendido_apagado
  - test_manejo_de_error_sensor

**Objetivo:** Validar que modelo → controlador → vista funciona end-to-end

---

### 7. Configuración de Tests

**Ubicación:** `tests/conftest.py`
**Estimación:** 10 min

**Tareas:**
- [ ] Verificar fixture qapp existe
- [ ] Agregar fixture para DisplayModelo
- [ ] Agregar fixture para DisplayVista (con qapp)
- [ ] Agregar fixture para DisplayControlador completo

---

## Integración con Arquitectura Existente

### 8. Integración con Factory (Fase posterior)

**Ubicación:** `app/factory.py`
**Estimación:** 10 min

**Tareas:**
- [ ] Agregar método _crear_ctrl_display() en ComponenteFactoryUX
- [ ] Retornar DisplayControlador completamente configurado

**Nota:** Esta tarea se hará después de validar que el panel funciona aislado

---

### 9. Integración con Coordinator (Fase posterior)

**Ubicación:** `app/coordinator.py`
**Estimación:** 10 min

**Tareas:**
- [ ] Conectar señal servidor.estado_recibido → display.actualizar_temperatura
- [ ] Conectar señal power.estado_cambiado → display.set_encendido

**Nota:** Esta tarea se hará después de validar integración con Factory

---

### 10. Integración con Compositor (Fase posterior)

**Ubicación:** `app/presentacion/ui_compositor.py`
**Estimación:** 5 min

**Tareas:**
- [ ] Agregar display.vista al layout principal
- [ ] Posicionar según mockup de UI

---

## Validación

### 11. Escenarios BDD

**Ubicación:** `tests/features/US-001-ver-temperatura-ambiente.feature`
**Estimación:** 30 min

**Tareas:**
- [ ] Implementar steps de Gherkin con pytest-bdd
- [ ] Given steps (setup de contexto)
- [ ] When steps (acciones)
- [ ] Then steps (aserciones)
- [ ] Ejecutar todos los escenarios
- [ ] Validar que 6/6 escenarios pasan

---

### 12. Quality Gates

**Estimación:** 10 min

**Tareas:**
- [ ] Ejecutar Pylint en app/presentacion/paneles/display/
  - Target: ≥ 8.0
- [ ] Calcular métricas con radon
  - CC promedio ≤ 10
  - MI promedio > 20
- [ ] Ejecutar pytest con coverage
  - Target: ≥ 95%
- [ ] Generar reporte JSON: quality/reports/US-001-quality.json

---

## Documentación

### 13. Actualizar Documentación

**Estimación:** 10 min

**Tareas:**
- [ ] Actualizar arquitectura.md (si existe) con panel Display
- [ ] Actualizar CHANGELOG.md con US-001 completada
- [ ] Generar reporte final: docs/reports/US-001-report.md

---

## Checklist de Progreso

### Implementación Core
- [x] DisplayModelo implementado (10 min) ✅
- [x] DisplayVista implementado (25 min) ✅
- [x] DisplayControlador implementado (20 min) ✅
- [x] __init__.py creado (2 min) ✅

### Testing Unitario
- [x] test_display_modelo.py (15 min) ✅
- [x] test_display_vista.py (20 min) ✅
- [x] test_display_controlador.py (20 min) ✅
- [x] conftest.py actualizado (10 min) ✅

### Testing Integración
- [x] test_display_integracion.py (25 min) ✅
- [x] Escenarios BDD implementados (30 min) ✅

### Validación
- [x] Quality gates ejecutados (10 min) ✅
- [x] Todos los tests pasan (100%) ✅ 75/75
- [x] Coverage ≥ 95% ✅ 100%

### Documentación
- [x] Docs actualizados (10 min) ✅

---

## Resumen de Estimación

| Fase | Tareas | Tiempo Estimado |
|------|--------|----------------|
| **Implementación Core** | 4 | 57 min |
| **Tests Unitarios** | 4 | 65 min |
| **Tests Integración** | 2 | 55 min |
| **Validación** | 1 | 10 min |
| **Documentación** | 1 | 10 min |
| **TOTAL** | **12** | **3h 17min** |

**Nota:** Integración con Factory/Coordinator/Compositor se hará en fase posterior (no incluido en esta estimación)

---

## Progreso

**Estado:** ✅ COMPLETADO
**Tareas completadas:** 12/12
**Progreso:** 100%
**Tiempo invertido:** ~4h 0min
**Tiempo estimado restante:** 0h 0min

---

## Dependencias

**Historias bloqueantes:** Ninguna (es base)
**Historias relacionadas:**
- US-002 (Estado climatizador) - mismo patrón MVC
- US-011 (Cambiar vista) - usa DisplayControlador.cambiar_modo_vista()

**Componentes externos necesarios:**
- compartido/widgets/ (para inspiración de estilos)
- compartido/estilos/ThemeProvider (opcional, para tema dark)

---

## Notas de Implementación

### Estilo LCD Verde

Aplicar en DisplayVista:

```python
self.setStyleSheet("""
    QWidget#displayLCD {
        background-color: #065f46;
        border: 2px solid #047857;
        border-radius: 12px;
        padding: 20px;
    }
""")
```

### Fuente Grande

```python
font = QFont()
font.setPointSize(48)  # o mayor
self.label_temp.setFont(font)
```

### Manejo de "---"

Cuando no hay conexión:
```python
if not modelo.encendido or modelo.error_sensor:
    self.label_temp.setText("---")
```

---

## Riesgos Identificados

1. **Pytest-bdd no configurado:** Si no está instalado, los escenarios BDD fallarán
   - Mitigación: Instalar con `pip install pytest-bdd`

2. **Coverage bajo inicial:** Componentes nuevos pueden no alcanzar 95% inmediato
   - Mitigación: Agregar tests de casos extremos

3. **Estilos no se ven como esperado:** QSS puede comportarse diferente según plataforma
   - Mitigación: Probar en Mac/Linux, ajustar según necesidad

---

## Lecciones Aprendidas

### ✅ Aciertos

1. **Patrón MVC bien definido**: La separación clara entre modelo, vista y controlador facilitó enormemente el testing y mantenimiento.

2. **Inmutabilidad del modelo**: Usar dataclass frozen evitó bugs de mutación accidental y simplificó el razonamiento sobre el estado.

3. **TDD efectivo**: Escribir tests exhaustivos (75 tests, coverage 100%) dio confianza total en el código.

4. **BDD validó aceptación**: Los 6 escenarios Gherkin validaron directamente los criterios de aceptación de la US.

5. **Fixtures reutilizables**: Las fixtures en conftest.py serán reutilizables para otros paneles.

### 📚 Mejoras Identificadas

1. **Pylint config**: Falsos positivos de PyQt6 requirieron disable manual. Crear `.pylintrc` con:
   ```ini
   [MESSAGES CONTROL]
   disable=no-name-in-module,too-few-public-methods
   ```

2. **pytest-bdd no instalado**: Tuvimos que instalar pytest-bdd durante implementación. Agregar a requirements.txt.

3. **Pattern reusable**: Este panel sirve como **referencia arquitectónica** perfecta para los otros 7 paneles.

### 🎯 Resultados Finales

- **Pylint**: 10.00/10 (objetivo: ≥8.0) ✅
- **CC**: 1.65 (objetivo: ≤10) ✅
- **MI**: 84.25 (objetivo: >20) ✅
- **Coverage**: 100% (objetivo: ≥95%) ✅
- **Tests**: 75/75 pasando ✅
- **Tiempo real**: ~4h (estimación: 3h17min)

### 📊 Ratio Tests/Código

- **Código**: 376 líneas
- **Tests**: 1,816 líneas
- **Ratio**: 4.83:1

Este ratio excepcional garantiza mantenibilidad a largo plazo.

---

**Última actualización:** 2026-01-16 - Implementación completada ✅
**Actualizado por:** Claude Code - Skill /implement-us
