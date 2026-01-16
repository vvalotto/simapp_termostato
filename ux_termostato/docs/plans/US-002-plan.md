# Plan de Implementación: US-002 - Ver estado del climatizador

## Información de la Historia

**US:** US-002
**Título:** Ver estado del climatizador
**Prioridad:** Alta
**Puntos:** 5
**Producto:** ux_termostato
**Fecha inicio:** 2026-01-16
**Estado:** EN PROGRESO

---

## Resumen

**Como** usuario del termostato
**Quiero** ver el estado actual del climatizador (calentando, enfriando, reposo)
**Para** saber si el sistema está actuando para alcanzar la temperatura deseada

---

## Componentes a Implementar

### 1. Panel Climatizador - MVC Completo

#### 1.1 ClimatizadorModelo (Modelo de datos)

**Ubicación:** `app/presentacion/paneles/climatizador/modelo.py`
**Patrón:** Dataclass inmutable (frozen=True)
**Estimación:** 10 min

**Responsabilidad:**
- Almacenar estado del climatizador: modo (calentando/enfriando/reposo/apagado), encendido

**Tareas:**
- [ ] Crear archivo con estructura base
- [ ] Definir dataclass ClimatizadorModelo
- [ ] Agregar campos: modo, encendido
- [ ] Implementar validación de modos válidos
- [ ] Agregar docstrings

**Referencia:** Ver DisplayModelo (US-001)

---

#### 1.2 ClimatizadorVista (Vista UI)

**Ubicación:** `app/presentacion/paneles/climatizador/vista.py`
**Patrón:** QWidget puro, sin lógica
**Estimación:** 40 min

**Responsabilidad:**
- Renderizar 3 indicadores visuales (Calor 🔥, Reposo 🌬️, Frío ❄️)
- Aplicar estilos según estado (colores, bordes, animaciones)
- Destacar indicador activo, apagar inactivos

**Tareas:**
- [ ] Crear archivo con estructura base
- [ ] Heredar de QWidget
- [ ] Crear 3 widgets indicadores:
  - indicador_calor (QWidget con QLabel para icono y texto)
  - indicador_reposo (QWidget con QLabel)
  - indicador_frio (QWidget con QLabel)
- [ ] Implementar método actualizar(modelo: ClimatizadorModelo)
- [ ] Aplicar stylesheet con colores:
  - Calor activo: naranja #f97316, fondo rgba(249,115,22,0.2)
  - Reposo activo: verde #22c55e, fondo rgba(34,197,94,0.2)
  - Frío activo: azul #3b82f6, fondo rgba(59,130,246,0.2)
  - Inactivo: gris #64748b, fondo rgba(100,116,139,0.3)
- [ ] Agregar animación pulsante CSS para calor y frío
- [ ] Agregar docstrings

**Referencia:** Ver DisplayVista (US-001) y widgets en compartido/widgets/

---

#### 1.3 ClimatizadorControlador (Lógica de presentación)

**Ubicación:** `app/presentacion/paneles/climatizador/controlador.py`
**Patrón:** QObject, coordina modelo ↔ vista, emite señales
**Estimación:** 20 min

**Responsabilidad:**
- Actualizar modelo cuando cambia estado del climatizador
- Llamar vista.actualizar() cuando modelo cambia
- Emitir señales para otros componentes
- Manejar transiciones de estado

**Tareas:**
- [ ] Crear archivo con estructura base
- [ ] Heredar de QObject
- [ ] Implementar métodos:
  - actualizar_estado(modo: str)
  - set_encendido(encendido: bool)
  - actualizar_desde_estado(estado_termostato)
- [ ] Definir señales (estado_cambiado)
- [ ] Agregar docstrings

**Referencia:** Ver DisplayControlador (US-001)

---

#### 1.4 Archivo __init__.py

**Ubicación:** `app/presentacion/paneles/climatizador/__init__.py`
**Estimación:** 2 min

**Tareas:**
- [ ] Crear archivo
- [ ] Exportar ClimatizadorModelo, ClimatizadorVista, ClimatizadorControlador

---

## Tests

### 2. Tests Unitarios - ClimatizadorModelo

**Ubicación:** `tests/test_climatizador_modelo.py`
**Estimación:** 15 min

**Tareas:**
- [ ] Clase TestCreacion
  - test_crear_con_valores_default
  - test_crear_con_valores_custom
  - test_validar_modos_validos
- [ ] Clase TestInmutabilidad
  - test_es_inmutable (frozen=True)
- [ ] Clase TestValidacion
  - test_modo_invalido_lanza_error

---

### 3. Tests Unitarios - ClimatizadorVista

**Ubicación:** `tests/test_climatizador_vista.py`
**Estimación:** 30 min

**Tareas:**
- [ ] Clase TestCreacion (con qapp fixture)
  - test_crear_vista
  - test_widgets_indicadores_existen
  - test_iconos_correctos
- [ ] Clase TestActualizacion
  - test_actualizar_modo_calentando
  - test_actualizar_modo_enfriando
  - test_actualizar_modo_reposo
  - test_actualizar_cuando_apagado
- [ ] Clase TestEstilos
  - test_colores_activo_calor
  - test_colores_activo_reposo
  - test_colores_activo_frio
  - test_colores_inactivos
  - test_animacion_presente_calor
  - test_animacion_presente_frio
  - test_sin_animacion_reposo
- [ ] Clase TestTransiciones
  - test_transicion_calor_a_reposo
  - test_transicion_reposo_a_frio
  - test_solo_un_indicador_activo

---

### 4. Tests Unitarios - ClimatizadorControlador

**Ubicación:** `tests/test_climatizador_controlador.py`
**Estimación:** 20 min

**Tareas:**
- [ ] Clase TestCreacion
  - test_crear_controlador
  - test_modelo_inicial
  - test_vista_asociada
- [ ] Clase TestMetodos
  - test_actualizar_estado_calentando
  - test_actualizar_estado_enfriando
  - test_actualizar_estado_reposo
  - test_set_encendido
  - test_actualizar_desde_estado_termostato
- [ ] Clase TestSignals
  - test_emite_signal_al_cambiar_estado
- [ ] Clase TestValidacion
  - test_estado_invalido_lanza_error

---

### 5. Tests de Integración

**Ubicación:** `tests/test_climatizador_integracion.py`
**Estimación:** 25 min

**Tareas:**
- [ ] TestIntegracionMVC
  - test_flujo_completo_modelo_vista_controlador
  - test_transiciones_entre_estados
- [ ] TestIntegracionConServidor
  - test_actualizacion_desde_servidor_simulado
  - test_cambio_estado_en_tiempo_real
- [ ] TestIntegracionEstadosEspeciales
  - test_cambio_estado_encendido_apagado
  - test_todos_estados_del_climatizador
- [ ] TestIntegracionSignals
  - test_signals_se_emiten_correctamente

---

### 6. Actualizar fixtures en conftest.py

**Ubicación:** `tests/conftest.py`
**Estimación:** 10 min

**Tareas:**
- [ ] Agregar fixture climatizador_modelo
- [ ] Agregar fixture climatizador_vista
- [ ] Agregar fixture climatizador_controlador
- [ ] Agregar fixture climatizador_controlador_custom

---

### 7. Tests BDD - Implementación de Steps

**Ubicación:** `tests/test_bdd_us002.py`
**Estimación:** 40 min

**Tareas:**
- [ ] Implementar Given steps (contexto, estados)
- [ ] Implementar When steps (acciones, cambios de estado)
- [ ] Implementar Then steps (aserciones visuales, colores, animaciones)
- [ ] Validar que 11 escenarios pasen

---

## Validación

### 8. Quality Gates

**Estimación:** 10 min

**Tareas:**
- [ ] Ejecutar Pylint en app/presentacion/paneles/climatizador/
  - Target: ≥ 8.0
- [ ] Calcular métricas con radon
  - CC promedio ≤ 10
  - MI promedio > 20
- [ ] Ejecutar pytest con coverage
  - Target: ≥ 95%
- [ ] Validar que todos los tests pasen

---

## Documentación

### 9. Actualizar Documentación

**Estimación:** 10 min

**Tareas:**
- [ ] Actualizar plan con progreso real
- [ ] Generar reporte final: docs/reports/US-002-report.md
- [ ] Documentar lecciones aprendidas

---

## Checklist de Progreso

### Implementación Core
- [x] ClimatizadorModelo implementado (10 min) ✅
- [x] ClimatizadorVista implementado (40 min) ✅
- [x] ClimatizadorControlador implementado (20 min) ✅
- [x] __init__.py creado (2 min) ✅

### Testing Unitario
- [x] test_climatizador_modelo.py (15 min) ✅
- [x] test_climatizador_vista.py (30 min) ✅
- [x] test_climatizador_controlador.py (20 min) ✅
- [x] conftest.py actualizado (10 min) ✅

### Testing Integración
- [x] test_climatizador_integracion.py (25 min) ✅
- [x] test_bdd_us002.py - Steps BDD (40 min) ✅

### Validación
- [x] Quality gates ejecutados (10 min) ✅
- [x] Todos los tests pasan (100%) ✅
- [x] Coverage ≥ 95% ✅

### Documentación
- [x] Docs actualizados (10 min) ✅

---

## Resumen de Estimación

| Fase | Tareas | Tiempo Estimado |
|------|--------|-----------------|
| **Implementación Core** | 4 | 72 min |
| **Tests Unitarios** | 4 | 75 min |
| **Tests Integración** | 2 | 65 min |
| **Validación** | 1 | 10 min |
| **Documentación** | 1 | 10 min |
| **TOTAL** | **12** | **4h 12min** |

---

## Progreso

**Estado:** ✅ COMPLETADA
**Tareas completadas:** 12/12
**Progreso:** 100%
**Tiempo invertido:** 3h 52min
**Tiempo estimado restante:** 0min

---

## Dependencias

**Historias bloqueantes:** Ninguna
**Historias relacionadas:**
- US-001 (Display) - mismo patrón MVC ✅
- US-003 (Indicadores LED) - ambos son indicadores visuales

**Componentes externos necesarios:**
- DisplayModelo de US-001 (como referencia)
- Fixtures de conftest.py (ya creadas en US-001)

---

## Notas de Implementación

### Estados del Climatizador

```python
MODO_CALENTANDO = "calentando"
MODO_ENFRIANDO = "enfriando"
MODO_REPOSO = "reposo"
MODO_APAGADO = "apagado"
```

### Colores y Estilos

**Calor (activo):**
```css
border: 3px solid #f97316;
background: rgba(249, 115, 22, 0.2);
animation: pulse 2s ease-in-out infinite;
```

**Reposo (activo):**
```css
border: 3px solid #22c55e;
background: rgba(34, 197, 94, 0.2);
/* sin animación */
```

**Frío (activo):**
```css
border: 3px solid #3b82f6;
background: rgba(59, 130, 246, 0.2);
animation: pulse 2s ease-in-out infinite;
```

**Inactivo:**
```css
border: 2px solid #64748b;
background: rgba(100, 116, 139, 0.3);
```

### Animación Pulsante

```python
# En el stylesheet CSS de la vista
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
```

### Iconos

Usar emojis en QLabel:
- Calor: 🔥
- Reposo: 🌬️
- Frío: ❄️

---

## Riesgos Identificados

1. **Animaciones CSS en PyQt6:** Las animaciones CSS pueden no funcionar igual que en web
   - Mitigación: Usar QPropertyAnimation de PyQt si CSS no funciona

2. **Sincronización de animaciones:** Asegurar que solo un indicador anime a la vez
   - Mitigación: Detener animaciones al cambiar de estado

3. **Transiciones suaves:** Evitar parpadeos al cambiar de estado
   - Mitigación: Actualizar todos los indicadores en una sola llamada

---

## Lecciones Aprendidas

### 1. Animaciones QPropertyAnimation
- `QPropertyAnimation` es poderosa pero requiere gestión cuidadosa del ciclo de vida
- Almacenar referencias en atributos del widget (`_animation`) permite control fino
- Detener animaciones antes de iniciar nuevas previene fugas de memoria

### 2. CSS Dinámico con Properties
- `setProperty()` + selectores CSS = estilos flexibles sin cambiar stylesheet completo
- Forzar actualización con `unpolish()` + `polish()` es necesario
- Pattern más limpio que cambiar estilos inline

### 3. Testing de Componentes UI
- QPropertyAnimation.State requiere comparación con enums, no integers
- Fixtures compartidas en conftest.py aceleran creación de tests
- BDD scenarios complementan perfectamente tests unitarios

### 4. Inmutabilidad con Dataclasses
- Pattern `replace()` de dataclasses frozen es elegante
- Previene bugs de mutación accidental
- Facilita reasoning sobre flujo de datos

---

**Implementación completada:** 2026-01-16
**Tiempo total:** 3h 52min (vs 4h 12min estimado = -20min)
**Elaborado por:** Claude Code - Skill /implement-us
