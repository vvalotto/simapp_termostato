# PLAN DE MEJORA - DOCUMENTACIÓN

**Estado:** 🔲 Pendiente
**Creado:** 2026-01-30
**Contexto:** Post-migración de estandarización documental (PLAN_MIGRACION_DOCS.md completado)
**Objetivo:** Completar gaps documentales y reorganizar ADRs por scope semántico

---

## 📋 RESUMEN EJECUTIVO

Tras completar la estandarización de estructura documental de los 4 subsistemas (compartido, simulador_temperatura, simulador_bateria, ux_termostato), se identificaron **3 gaps críticos**:

1. ✅ **Estructura estandarizada** - Completado (FASE 1-5)
2. ❌ **Compartido sin documentación de calidad/diseño** - Módulo crítico sin informes consolidados
3. ❌ **Decisiones de diseño no documentadas** - Rationale de decisiones técnicas se pierde
4. ❌ **ADRs en docs/ raíz deberían estar en compartido/** - Mala organización semántica

**Impacto:**
- Compartido es la **base crítica** (networking + widgets + estilos) usada por los 3 productos
- Sin documentación de calidad, no hay baseline para detectar degradación
- Sin decisiones documentadas, el conocimiento se pierde con el tiempo
- ADRs de compartido en docs/ raíz dificultan navegación

---

## 🚨 GAP 1: COMPARTIDO SIN DOCUMENTACIÓN DE CALIDAD/DISEÑO

### Situación Actual

**Comparación con otros productos:**

```
simulador_temperatura/docs/informes/
├── informe_calidad_final.md    ✅ Métricas + análisis
└── informe_hallazgos.md         ✅ Lecciones aprendidas

simulador_bateria/docs/informes/
├── informe_calidad_final.md    ✅ Métricas consolidadas
└── informe_diseno.md            ✅ Análisis SOLID profundo

ux_termostato/docs/informes/
├── informe_calidad_final.md    ✅ Métricas consolidadas
└── informe_hallazgos.md         ✅ Lecciones aprendidas

compartido/docs/informes/
└── [VACÍO]                      ❌ SIN DOCUMENTACIÓN
```

### ¿Por Qué Es Crítico?

- **Compartido es código crítico** - Base de todo el proyecto
- **Mayor reutilización** - 3 productos dependen de él
- **Complejidad técnica** - Networking, widgets PyQt6, patrones avanzados
- **Sin baseline** - No hay referencia para validar cambios futuros

### Estado de Calidad Actual

**Evidencia disponible:**
- ✅ 34+ tests unitarios
- ✅ Scripts de quality gates (`compartido/quality/scripts/`)
- ✅ Reportes auto-generados (`compartido/quality/reports/`)
- ❌ **NO consolidado en informe final**
- ❌ **NO analizado desde perspectiva de diseño**

---

## 🚨 GAP 2: DECISIONES DE DISEÑO NO DOCUMENTADAS

### Ejemplos de Decisiones Sin Documentar

#### Compartido/Networking

**Decisión:** ¿Por qué dos clientes socket diferentes?

```python
EphemeralSocketClient   # Conectar → Enviar → Cerrar
BaseSocketClient        # Conexión persistente
```

**Contexto no documentado:**
- ❓ ¿Por qué simuladores usan efímero?
- ❓ ¿Cuándo usar uno vs otro?
- ❓ ¿Qué trade-offs tienen?
- ❓ ¿Se consideraron alternativas?

**Decisión real (no escrita):**
- Efímero simplifica manejo de errores
- Evita sockets colgados en simuladores
- No requiere gestión de estado de conexión
- Suficiente para comunicación unidireccional

#### Compartido/Widgets

**Decisión:** ¿Por qué LedIndicator usa composición en lugar de herencia?

```python
# Implementación actual (composición)
class LedIndicator(QWidget):
    def __init__(self):
        self._circle_widget = ...  # Composición

# Alternativa no elegida (herencia)
class LedIndicator(QPainter):
    def paintEvent(self, event):
        ...  # Dibujo directo
```

**Contexto no documentado:**
- ❓ ¿Por qué composición?
- ❓ ¿Se evaluó herencia de QPainter?
- ❓ ¿Qué ventajas/desventajas?

#### Simuladores

**Decisión:** ¿Por qué separar GeneradorTemperatura de ServicioEnvio?

```python
# Estructura actual
GeneradorTemperatura  # Lógica de negocio (dominio)
ServicioEnvio         # Comunicación (networking)

# Alternativa no elegida
class SimuladorTemperatura:  # Todo en uno
    def generar_y_enviar(self):
        temp = self.generar()
        self.enviar(temp)
```

**Contexto no documentado:**
- ❓ ¿Por qué separación?
- ❓ Beneficios de testing aislado?
- ❓ Relación con patrón MVC?

### Ubicación Propuesta

Estas decisiones deberían documentarse en:

1. **`arquitectura.md`** - Sección "Decisiones de Diseño"
   - Para decisiones estructurales del producto
   - Ejemplo: "Por qué separamos GeneradorTemperatura de ServicioEnvio"

2. **ADRs en `decisiones/`** - Si son decisiones complejas con múltiples alternativas
   - Ejemplo: "ADR-001: Elección de patrón efímero para clientes socket"

**Regla práctica:**
- Si tomaste >30min decidiendo entre alternativas → documéntalo
- Si la decisión afecta a múltiples componentes → ADR
- Si es específica de un componente → sección en arquitectura.md

---

## 🚨 GAP 3: REORGANIZACIÓN - ADRs EN docs/ QUE DEBERÍAN ESTAR EN compartido/

### Contenido Actual de docs/ Raíz

```
docs/
├── adr_001_separacion_socket_clients.md       ← específico de compartido/networking
├── adr_002_refactorizacion_socket_server.md   ← específico de compartido/networking
├── adr_003_arquitectura_widgets_compartidos.md ← específico de compartido/widgets
├── adr_004_arquitectura_presentacion_simulador_temperatura.md  ← producto
├── adr_005_arquitectura_referencia_simuladores.md  ← proyecto global
├── design_001_simuladores.md                   ← proyecto global
├── guide_001_estructura_jira.md                ← proyecto global
└── spec_001_comunicaciones.md                  ← proyecto global
```

### Análisis por Documento

| Documento | Scope | ¿Mover? | Destino | Justificación |
|-----------|-------|---------|---------|---------------|
| adr_001_separacion_socket_clients.md | networking | ✅ SÍ | compartido/docs/decisiones/ | Decisión específica de implementación de compartido |
| adr_002_refactorizacion_socket_server.md | networking | ✅ SÍ | compartido/docs/decisiones/ | Decisión específica de implementación de compartido |
| adr_003_arquitectura_widgets_compartidos.md | widgets | ✅ SÍ | compartido/docs/decisiones/ | Decisión específica de implementación de compartido |
| adr_004_arquitectura_presentacion_simulador_temperatura.md | producto | ❌ NO | docs/ | Decisión específica de producto |
| adr_005_arquitectura_referencia_simuladores.md | proyecto | ❌ NO | docs/ | Patrón global multi-producto |
| design_001_simuladores.md | proyecto | ❌ NO | docs/ | Diseño global sistema HIL |
| guide_001_estructura_jira.md | proyecto | ❌ NO | docs/ | Gestión de proyecto |
| spec_001_comunicaciones.md | proyecto | ⚠️ DEBATIBLE | docs/ | Protocolo global, pero implementado en compartido |

### Propuesta de Reorganización

**Estructura objetivo:**

```
# MOVER A compartido/docs/decisiones/
compartido/docs/decisiones/
├── adr_001_separacion_socket_clients.md
├── adr_002_refactorizacion_socket_server.md
└── adr_003_arquitectura_widgets_compartidos.md

# MANTENER EN docs/ raíz (decisiones de proyecto)
docs/
├── adr_004_arquitectura_presentacion_simulador_temperatura.md
├── adr_005_arquitectura_referencia_simuladores.md
├── design_001_simuladores.md
├── guide_001_estructura_jira.md
└── spec_001_comunicaciones.md
```

**Criterio semántico:**
- **compartido/docs/decisiones/**: ADRs específicos de implementación interna de módulos compartidos
- **docs/ raíz**: Decisiones arquitectónicas de proyecto completo (multi-producto, protocolos globales)

---

## 🎯 JERARQUÍA DOCUMENTAL PROPUESTA

### Nivel 1: Proyecto (docs/ raíz)
- **Audiencia:** Arquitectos, stakeholders, nuevos desarrolladores
- **Contenido:** Visión global, decisiones multi-producto, protocolos, procesos
- **Ejemplos:** adr_005 (patrón MVC+Factory global), design_001 (sistema HIL completo)

### Nivel 2: Módulo Compartido (compartido/docs/)
- **Audiencia:** Desarrolladores que usan/mantienen compartido
- **Contenido:** APIs, decisiones de implementación, análisis de calidad
- **Estructura objetivo:**
  ```
  compartido/docs/
  ├── api_reference.md           # ✅ Existe - ¿Qué expone?
  ├── widgets_guide.md           # ✅ Existe - ¿Cómo usar widgets?
  ├── networking_guide.md        # ✅ Existe - ¿Cómo usar networking?
  ├── arquitectura.md            # 🔲 CREAR - ¿Cómo está estructurado?
  ├── decisiones/                # 🔲 CREAR - ¿Por qué así?
  │   ├── adr_001_separacion_socket_clients.md      # MOVER
  │   ├── adr_002_refactorizacion_socket_server.md  # MOVER
  │   └── adr_003_arquitectura_widgets_compartidos.md # MOVER
  └── informes/                  # 🔲 CREAR - ¿Qué calidad tiene?
      ├── informe_calidad_final.md
      └── informe_diseno.md
  ```

### Nivel 3: Productos (simulador_*/docs/, ux_termostato/docs/)
- **Audiencia:** Desarrolladores/usuarios del producto específico
- **Contenido:** Arquitectura interna, guías de uso, configuración, calidad
- **Estado:** ✅ Estandarizado (PLAN_MIGRACION_DOCS.md completado)

---

## 📊 ROADMAP - FASES DE IMPLEMENTACIÓN

### 🔴 FASE 1: INFORMES DE CALIDAD COMPARTIDO (CRÍTICO)

**Objetivo:** Documentar calidad y diseño del módulo compartido

**Tareas:**

**1.1. Generar Métricas de Calidad**
```bash
cd compartido
pylint networking/ widgets/ estilos/ --output-format=json > quality/reports/pylint_report.json
radon cc networking/ widgets/ estilos/ -a > quality/reports/cc_report.txt
radon mi networking/ widgets/ estilos/ > quality/reports/mi_report.txt
pytest --cov=. --cov-report=json > quality/reports/coverage.json
```

**1.2. Crear `compartido/docs/informes/informe_calidad_final.md`**

**Contenido:**
- Resumen ejecutivo
- Métricas por módulo:
  - networking/ (Pylint, CC, MI, Coverage)
  - widgets/ (Pylint, CC, MI, Coverage)
  - estilos/ (Pylint, CC, MI, Coverage)
- Consolidado total
- Quality gates: ✅ PASS / ❌ FAIL
- Comparación con estándares del proyecto

**Plantilla:** Similar a `simulador_bateria/docs/informes/informe_calidad_final.md`

**1.3. Crear `compartido/docs/informes/informe_diseno.md`**

**Contenido:**
- Análisis SOLID por módulo
- Evaluación de cohesión (0-10)
- Evaluación de acoplamiento (0-10)
- Patrones de diseño aplicados:
  - **networking/**: Strategy (clientes), Template Method (BaseSocketClient)
  - **widgets/**: Composition (widgets), Observer (signals/slots PyQt)
  - **estilos/**: Singleton (ThemeProvider)
- Trade-offs y justificaciones
- Recomendaciones de mejora

**Plantilla:** Similar a `simulador_bateria/docs/informes/informe_diseno.md` (análisis más profundo)

**Criterios de aceptación:**
- [ ] Métricas generadas para todos los módulos
- [ ] informe_calidad_final.md creado y consolidado
- [ ] informe_diseno.md con análisis SOLID completo
- [ ] Quality gates documentados

**Esfuerzo estimado:** 3-4 horas

---

### 🟡 FASE 2: ARQUITECTURA COMPARTIDO (IMPORTANTE)

**Objetivo:** Documentar estructura y organización del módulo compartido

**Tareas:**

**2.1. Crear `compartido/docs/arquitectura.md`**

**Contenido:**
- **Introducción:** Propósito de compartido (código reutilizable)
- **Estructura de Módulos:**
  ```
  compartido/
  ├── networking/        # Clientes y servidores TCP
  ├── widgets/           # Componentes PyQt6 reutilizables
  ├── estilos/           # Temas y constantes visuales
  └── quality/           # Scripts y reportes de calidad
  ```
- **Responsabilidades por Módulo:**
  - networking: Abstracciones de comunicación TCP
  - widgets: Componentes UI comunes
  - estilos: Consistencia visual
- **Dependencias:**
  - networking → Python socket, typing
  - widgets → PyQt6, networking (validación)
  - estilos → PyQt6.QtGui
- **Patrones de Diseño:**
  - Strategy: Diferentes estrategias de socket
  - Template Method: BaseSocketClient como plantilla
  - Composition: Widgets compuestos
  - Singleton: ThemeProvider
- **Sección "Decisiones de Diseño":**
  - ¿Por qué separar networking/widgets/estilos?
  - ¿Por qué EphemeralSocketClient vs BaseSocketClient?
  - ¿Por qué widgets con composición?
  - ¿Por qué ThemeProvider como singleton?

**Criterios de aceptación:**
- [ ] Estructura de módulos documentada
- [ ] Responsabilidades claras
- [ ] Patrones identificados
- [ ] Decisiones de diseño explicadas

**Esfuerzo estimado:** 2-3 horas

---

### 🟡 FASE 3: REORGANIZAR ADRs (IMPORTANTE)

**Objetivo:** Mover ADRs específicos de compartido de docs/ raíz a compartido/docs/decisiones/

**Tareas:**

**3.1. Crear estructura de decisiones**
```bash
mkdir -p compartido/docs/decisiones
```

**3.2. Mover ADRs específicos**
```bash
git mv docs/adr_001_separacion_socket_clients.md compartido/docs/decisiones/
git mv docs/adr_002_refactorizacion_socket_server.md compartido/docs/decisiones/
git mv docs/adr_003_arquitectura_widgets_compartidos.md compartido/docs/decisiones/
```

**3.3. Actualizar referencias**
- Buscar en todos los .md referencias a estos ADRs
- Actualizar rutas: `docs/adr_001_...` → `compartido/docs/decisiones/adr_001_...`
- Archivos a revisar:
  - CLAUDE.md
  - README.md
  - Otros docs/ que referencien estos ADRs
  - compartido/docs/arquitectura.md (si los referencia)

**3.4. Actualizar sync_wiki.yml**
- Cambiar rutas de origen en workflow de sincronización
- Asegurar que wiki se actualiza desde nuevas ubicaciones

**Criterios de aceptación:**
- [ ] ADRs movidos a compartido/docs/decisiones/
- [ ] Referencias actualizadas en todos los .md
- [ ] sync_wiki.yml actualizado
- [ ] No hay links rotos

**Esfuerzo estimado:** 1-2 horas

---

### 🟢 FASE 4: DOCUMENTAR DECISIONES EN PRODUCTOS (MEJORA)

**Objetivo:** Agregar sección "Decisiones de Diseño" en arquitectura.md de cada producto

**Tareas:**

**4.1. simulador_temperatura/docs/arquitectura.md**

Agregar sección:
```markdown
## Decisiones de Diseño

### ¿Por qué separar GeneradorTemperatura de ServicioEnvio?

**Alternativas consideradas:**
1. Clase única SimuladorTemperatura que genera y envía
2. Separación en dominio (GeneradorTemperatura) y comunicación (ServicioEnvio)

**Decisión:** Opción 2 - Separación en capas

**Justificación:**
- Testing aislado: Generador se prueba sin red
- Reutilización: ServicioEnvio puede usarse con otros generadores
- Adherencia a SRP (Single Responsibility Principle)
- Facilita modo automático/manual sin afectar envío

**Trade-offs:**
- Más clases (mayor complejidad estructural)
- Coordinación vía signals (overhead mínimo)
```

**4.2. simulador_bateria/docs/arquitectura.md**

Similar a temperatura (decisiones análogas).

**4.3. ux_termostato/docs/arquitectura.md**

Decisiones específicas:
- ¿Por qué comunicación bidireccional (ServidorEstado + ClienteComandos)?
- ¿Por qué UX es cliente sin estado?
- ¿Por qué separar dominio/comunicación/presentación?

**Criterios de aceptación:**
- [x] Sección "Decisiones de Diseño" en cada arquitectura.md
- [x] Al menos 2-3 decisiones documentadas por producto
- [x] Formato: Alternativas → Decisión → Justificación → Trade-offs
- [x] Todos los diagramas en formato Mermaid (no ASCII art)

**Esfuerzo estimado:** 2-3 horas
**Estado:** ✅ COMPLETADO (2026-02-01)

---

## ✅ CRITERIOS DE ACEPTACIÓN GLOBALES

### Compartido

- [ ] `compartido/docs/informes/informe_calidad_final.md` creado
- [ ] `compartido/docs/informes/informe_diseno.md` creado
- [ ] `compartido/docs/arquitectura.md` creado
- [ ] `compartido/docs/decisiones/` creado con 3 ADRs movidos
- [ ] Métricas de calidad consolidadas (Pylint, CC, MI, Coverage)
- [ ] Análisis SOLID completo

### Reorganización

- [ ] ADRs específicos movidos de docs/ a compartido/docs/decisiones/
- [ ] Referencias actualizadas en todos los .md
- [ ] sync_wiki.yml actualizado
- [ ] No hay links rotos

### Productos

- [x] Sección "Decisiones de Diseño" en simulador_temperatura/docs/arquitectura.md (4 decisiones)
- [x] Sección "Decisiones de Diseño" en simulador_bateria/docs/arquitectura.md (4 decisiones)
- [x] Sección "Decisiones de Diseño" en ux_termostato/docs/arquitectura.md (3 decisiones)

### Documentación de Proceso

- [ ] Este PLAN_MEJORA_DOCUMENTACION.md actualizado con progreso
- [ ] Commits con mensajes descriptivos (docs: ...)
- [ ] CLAUDE.md actualizado si cambia estructura

---

## 📂 ESTRUCTURA FINAL OBJETIVO

### Raíz
```
/
├── PLAN_MIGRACION_DOCS.md           # ✅ Completado
├── PLAN_MEJORA_DOCUMENTACION.md     # 🔲 En progreso
├── CLAUDE.md
├── README.md
├── config.json
└── docs/                            # Decisiones de PROYECTO
    ├── adr_004_arquitectura_presentacion_simulador_temperatura.md
    ├── adr_005_arquitectura_referencia_simuladores.md
    ├── design_001_simuladores.md
    ├── guide_001_estructura_jira.md
    └── spec_001_comunicaciones.md
```

### Compartido
```
compartido/
├── docs/
│   ├── api_reference.md           # ✅ Existe
│   ├── widgets_guide.md           # ✅ Existe
│   ├── networking_guide.md        # ✅ Existe
│   ├── arquitectura.md            # 🔲 FASE 2
│   ├── decisiones/                # 🔲 FASE 3
│   │   ├── adr_001_separacion_socket_clients.md
│   │   ├── adr_002_refactorizacion_socket_server.md
│   │   └── adr_003_arquitectura_widgets_compartidos.md
│   └── informes/                  # 🔲 FASE 1
│       ├── informe_calidad_final.md
│       └── informe_diseno.md
├── networking/
├── widgets/
├── estilos/
└── quality/
    ├── scripts/
    └── reports/
```

### Productos (ya estandarizados)
```
{producto}/docs/
├── arquitectura.md            # ✅ + sección "Decisiones" (FASE 4)
├── guia_uso.md                # ✅
├── configuracion.md           # ✅
├── [historias/]               # ✅ (solo UX)
└── informes/                  # ✅
    ├── informe_calidad_final.md
    └── informe_hallazgos.md (o informe_diseno.md)
```

---

## 🔗 REFERENCIAS

### Documentos Relacionados
- `PLAN_MIGRACION_DOCS.md` - Migración completada (estandarización estructura)
- `CLAUDE.md` - Guía del proyecto (sección Architecture)
- `.github/workflows/sync_wiki.yml` - Workflow de sincronización

### Plantillas de Referencia
- **Informe Calidad:** `simulador_bateria/docs/informes/informe_calidad_final.md`
- **Informe Diseño:** `simulador_bateria/docs/informes/informe_diseno.md`
- **Arquitectura:** `simulador_temperatura/docs/arquitectura.md`

### Scripts Útiles
```bash
# Generar métricas
cd compartido
python quality/scripts/calculate_metrics.py .
python quality/scripts/validate_gates.py quality/reports/*.json

# Buscar referencias rotas
grep -r "docs/adr_001" --include="*.md" .
grep -r "docs/adr_002" --include="*.md" .
grep -r "docs/adr_003" --include="*.md" .
```

---

## 📝 NOTAS PARA PRÓXIMA SESIÓN

### Contexto de Decisión
- Análisis realizado: 2026-01-30
- Basado en observación del usuario sobre gaps post-migración
- Consenso: Compartido es código crítico que requiere misma calidad documental que productos

### Preguntas Pendientes
- ¿spec_001_comunicaciones.md debería moverse a compartido o quedarse en docs/?
  - Argumento a favor: Protocolo implementado en compartido/networking
  - Argumento en contra: Es especificación global de proyecto, no decisión de implementación

### Próximos Pasos Sugeridos
1. Comenzar con FASE 1 (informes de calidad compartido) - Mayor impacto
2. Luego FASE 2 (arquitectura compartido) - Complementa informes
3. Después FASE 3 (reorganizar ADRs) - Limpieza semántica
4. Finalmente FASE 4 (decisiones en productos) - Nice to have

---

**ESTADO:** 🔲 Pendiente de ejecución
**ÚLTIMA ACTUALIZACIÓN:** 2026-01-30
