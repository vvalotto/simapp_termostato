# PLAN DE MIGRACIÓN - ESTANDARIZACIÓN DOCUMENTACIÓN

**Fecha:** 2026-01-30
**Objetivo:** Estandarizar estructura de documentación en todos los subsistemas
**Estrategia:** Ejecución por fases con commit incremental

---

## ESTRUCTURA OBJETIVO

### Productos Completos (temperatura, batería, ux)
```
docs/
├── arquitectura.md
├── guia_uso.md
├── configuracion.md
└── informes/
    ├── informe_calidad_final.md
    └── informe_hallazgos.md
```

### Compartido (infraestructura)
```
docs/
├── api_reference.md
├── widgets_guide.md
└── networking_guide.md
```

### UX (excepción: conserva historias)
```
docs/
├── arquitectura.md
├── guia_uso.md
├── configuracion.md
├── historias/
│   └── catalogo_historias.md
└── informes/
    ├── informe_calidad_final.md
    └── informe_hallazgos.md
```

---

## FASE 1: COMPARTIDO

### Cambios en Sistema de Archivos
```bash
# Crear estructura
mkdir -p compartido/docs

# Crear documentos (placeholders)
touch compartido/docs/api_reference.md
touch compartido/docs/widgets_guide.md
touch compartido/docs/networking_guide.md
```

### Actualización sync_wiki.yml
**Agregar después de la línea 53 (sección "Guías"):**
```yaml
# Compartido - Documentación de infraestructura
cp main_repo/compartido/docs/api_reference.md wiki_repo/Compartido-API-Reference.md
cp main_repo/compartido/docs/widgets_guide.md wiki_repo/Compartido-Widgets-Guide.md
cp main_repo/compartido/docs/networking_guide.md wiki_repo/Compartido-Networking-Guide.md
```

### Archivos Afectados
- `compartido/docs/api_reference.md` [CREAR]
- `compartido/docs/widgets_guide.md` [CREAR]
- `compartido/docs/networking_guide.md` [CREAR]
- `.github/workflows/sync_wiki.yml` [MODIFICAR]

---

## FASE 2: SIMULADOR TEMPERATURA

### Cambios en Sistema de Archivos
```bash
cd simulador_temperatura/docs

# Renombrar y reorganizar
mv arquitectura_simulador_temperatura.md arquitectura.md

# Crear subdirectorio
mkdir -p informes

# Mover informes
mv informe_calidad_diseno.md informes/informe_calidad_final.md
mv informe_hallazgos_desarrollo.md informes/informe_hallazgos.md

# Crear faltantes
touch guia_uso.md
touch configuracion.md
```

### Actualización sync_wiki.yml
**Agregar después de la sección "Compartido":**
```yaml
# Simulador Temperatura
cp main_repo/simulador_temperatura/docs/arquitectura.md wiki_repo/Temperatura-Arquitectura.md
cp main_repo/simulador_temperatura/docs/guia_uso.md wiki_repo/Temperatura-Guia-Uso.md
cp main_repo/simulador_temperatura/docs/configuracion.md wiki_repo/Temperatura-Configuracion.md
cp main_repo/simulador_temperatura/docs/informes/informe_calidad_final.md wiki_repo/Temperatura-Informe-Calidad.md
cp main_repo/simulador_temperatura/docs/informes/informe_hallazgos.md wiki_repo/Temperatura-Hallazgos.md
```

### Archivos Afectados
- `simulador_temperatura/docs/arquitectura.md` [RENOMBRAR]
- `simulador_temperatura/docs/informes/` [CREAR DIR]
- `simulador_temperatura/docs/informes/informe_calidad_final.md` [MOVER]
- `simulador_temperatura/docs/informes/informe_hallazgos.md` [MOVER]
- `simulador_temperatura/docs/guia_uso.md` [CREAR]
- `simulador_temperatura/docs/configuracion.md` [CREAR]
- `.github/workflows/sync_wiki.yml` [MODIFICAR]

---

## FASE 3: SIMULADOR BATERÍA

### Cambios en Sistema de Archivos
```bash
cd simulador_bateria/docs

# Renombrar y reorganizar
mv arquitectura_simulador_bateria.md arquitectura.md

# Crear subdirectorio
mkdir -p informes

# Mover informes
mv informe_calidad_final.md informes/informe_calidad_final.md
mv reporte_calidad_diseno.md informes/informe_diseno.md

# Crear faltantes
touch guia_uso.md
touch configuracion.md
```

### Actualización sync_wiki.yml
**Agregar después de la sección "Simulador Temperatura":**
```yaml
# Simulador Batería
cp main_repo/simulador_bateria/docs/arquitectura.md wiki_repo/Bateria-Arquitectura.md
cp main_repo/simulador_bateria/docs/guia_uso.md wiki_repo/Bateria-Guia-Uso.md
cp main_repo/simulador_bateria/docs/configuracion.md wiki_repo/Bateria-Configuracion.md
cp main_repo/simulador_bateria/docs/informes/informe_calidad_final.md wiki_repo/Bateria-Informe-Calidad.md
cp main_repo/simulador_bateria/docs/informes/informe_diseno.md wiki_repo/Bateria-Informe-Diseno.md
```

### Archivos Afectados
- `simulador_bateria/docs/arquitectura.md` [RENOMBRAR]
- `simulador_bateria/docs/informes/` [CREAR DIR]
- `simulador_bateria/docs/informes/informe_calidad_final.md` [MOVER]
- `simulador_bateria/docs/informes/informe_diseno.md` [RENOMBRAR+MOVER]
- `simulador_bateria/docs/guia_uso.md` [CREAR]
- `simulador_bateria/docs/configuracion.md` [CREAR]
- `.github/workflows/sync_wiki.yml` [MODIFICAR]

---

## FASE 4: UX TERMOSTATO

### Cambios en Sistema de Archivos
```bash
cd ux_termostato/docs

# ELIMINAR archivos de trabajo
rm -rf planes/
rm -rf reportes/
rm PLAN-REFACTORIZACION-UX-TERMOSTATO.md

# Crear subdirectorios
mkdir -p informes
mkdir -p historias

# Mover y renombrar
mv ANALISIS_CALIDAD_DISENO.md informes/informe_calidad_final.md
mv HISTORIAS-USUARIO-UX-TERMOSTATO.md historias/catalogo_historias.md

# Crear faltantes
touch arquitectura.md
touch guia_uso.md
touch configuracion.md
touch informes/informe_hallazgos.md
```

### Actualización sync_wiki.yml
**Agregar después de la sección "Simulador Batería":**
```yaml
# UX Termostato
cp main_repo/ux_termostato/docs/arquitectura.md wiki_repo/UX-Arquitectura.md
cp main_repo/ux_termostato/docs/guia_uso.md wiki_repo/UX-Guia-Uso.md
cp main_repo/ux_termostato/docs/configuracion.md wiki_repo/UX-Configuracion.md
cp main_repo/ux_termostato/docs/historias/catalogo_historias.md wiki_repo/UX-Historias-Usuario.md
cp main_repo/ux_termostato/docs/informes/informe_calidad_final.md wiki_repo/UX-Informe-Calidad.md
cp main_repo/ux_termostato/docs/informes/informe_hallazgos.md wiki_repo/UX-Hallazgos.md
```

### Archivos Afectados
- `ux_termostato/docs/planes/` [ELIMINAR - 11 archivos]
- `ux_termostato/docs/reportes/` [ELIMINAR - 7 archivos]
- `ux_termostato/docs/PLAN-REFACTORIZACION-UX-TERMOSTATO.md` [ELIMINAR]
- `ux_termostato/docs/informes/` [CREAR DIR]
- `ux_termostato/docs/historias/` [CREAR DIR]
- `ux_termostato/docs/informes/informe_calidad_final.md` [MOVER+RENOMBRAR]
- `ux_termostato/docs/historias/catalogo_historias.md` [MOVER+RENOMBRAR]
- `ux_termostato/docs/arquitectura.md` [CREAR]
- `ux_termostato/docs/guia_uso.md` [CREAR]
- `ux_termostato/docs/configuracion.md` [CREAR]
- `ux_termostato/docs/informes/informe_hallazgos.md` [CREAR]
- `.github/workflows/sync_wiki.yml` [MODIFICAR]

---

## FASE 5: ACTUALIZAR REFERENCIAS GLOBALES

### Actualización CLAUDE.md
Buscar y reemplazar referencias a:
- `arquitectura_simulador_temperatura.md` → `simulador_temperatura/docs/arquitectura.md`
- `arquitectura_simulador_bateria.md` → `simulador_bateria/docs/arquitectura.md`
- `HISTORIAS-USUARIO-UX-TERMOSTATO.md` → `ux_termostato/docs/historias/catalogo_historias.md`
- Actualizar sección "Development Status" para reflejar nueva estructura

### Actualización README.md
Buscar y reemplazar links a documentación antigua con nueva estructura.

### Verificación Final
```bash
# Buscar referencias rotas
grep -r "arquitectura_simulador" .
grep -r "HISTORIAS-USUARIO" .
grep -r "PLAN-REFACTORIZACION" .
grep -r "docs/plans" .
grep -r "docs/reportes" .
```

### Archivos Afectados
- `CLAUDE.md` [MODIFICAR]
- `README.md` [MODIFICAR]
- `.github/workflows/sync_wiki.yml` [VERIFICAR]

---

## RESUMEN DE ELIMINACIONES

**Archivos que se ELIMINARÁN PERMANENTEMENTE:**
- `ux_termostato/docs/planes/` (11 archivos):
  - us_001_plan.md a us_025_plan.md
  - sprint_2_plan.md
- `ux_termostato/docs/reportes/` (7 archivos):
  - us_001_report.md, us_002_report.md, etc.
  - analisis_calidad_diseno_us020_us021.md
  - quality_report_us021.txt
- `ux_termostato/docs/PLAN-REFACTORIZACION-UX-TERMOSTATO.md`

**Total:** 19 archivos eliminados (quedan en git history)

---

## COMMITS PROPUESTOS

**Fase 1:**
```
docs(compartido): crear estructura de documentación

- Agregar docs/api_reference.md (placeholder)
- Agregar docs/widgets_guide.md (placeholder)
- Agregar docs/networking_guide.md (placeholder)
- Actualizar sync_wiki.yml con sección compartido
```

**Fase 2:**
```
docs(temperatura): estandarizar estructura

- Renombrar arquitectura_simulador_temperatura.md → arquitectura.md
- Reorganizar informes en subdirectorio informes/
- Crear guia_uso.md y configuracion.md (placeholders)
- Actualizar sync_wiki.yml
```

**Fase 3:**
```
docs(bateria): estandarizar estructura

- Renombrar arquitectura_simulador_bateria.md → arquitectura.md
- Reorganizar informes en subdirectorio informes/
- Crear guia_uso.md y configuracion.md (placeholders)
- Actualizar sync_wiki.yml
```

**Fase 4:**
```
docs(ux): estandarizar estructura y limpiar archivos de trabajo

- Eliminar carpetas planes/ y reportes/ (archivos de trabajo)
- Eliminar PLAN-REFACTORIZACION-UX-TERMOSTATO.md
- Reorganizar ANALISIS_CALIDAD_DISENO.md → informes/informe_calidad_final.md
- Mover HISTORIAS-USUARIO-UX-TERMOSTATO.md → historias/catalogo_historias.md
- Crear arquitectura.md, guia_uso.md, configuracion.md (placeholders)
- Actualizar sync_wiki.yml
```

**Fase 5:**
```
docs: actualizar referencias a documentación reorganizada

- Actualizar links en CLAUDE.md
- Actualizar links en README.md
- Verificar y corregir referencias rotas
```

---

## CHECKLIST DE EJECUCIÓN

```
🔲 FASE 1: Compartido
   🔲 Crear compartido/docs/
   🔲 Crear placeholders (api_reference, widgets_guide, networking_guide)
   🔲 Actualizar sync_wiki.yml
   🔲 Revisión manual
   🔲 Commit

🔲 FASE 2: Simulador Temperatura
   🔲 Renombrar arquitectura
   🔲 Crear informes/ y mover archivos
   🔲 Crear placeholders (guia_uso, configuracion)
   🔲 Actualizar sync_wiki.yml
   🔲 Revisión manual
   🔲 Commit

🔲 FASE 3: Simulador Batería
   🔲 Renombrar arquitectura
   🔲 Crear informes/ y mover archivos
   🔲 Crear placeholders (guia_uso, configuracion)
   🔲 Actualizar sync_wiki.yml
   🔲 Revisión manual
   🔲 Commit

🔲 FASE 4: UX Termostato
   🔲 Eliminar planes/, reportes/, PLAN-REFACTORIZACION
   🔲 Crear informes/ e historias/
   🔲 Mover y renombrar archivos
   🔲 Crear placeholders (arquitectura, guia_uso, configuracion, hallazgos)
   🔲 Actualizar sync_wiki.yml
   🔲 Revisión manual
   🔲 Commit

🔲 FASE 5: Referencias Globales
   🔲 Actualizar CLAUDE.md
   🔲 Actualizar README.md
   🔲 Buscar y corregir referencias rotas
   🔲 Verificación final
   🔲 Commit final
```

---

**ESTADO:** ⏸️  Pendiente de ejecución
**ÚLTIMA ACTUALIZACIÓN:** 2026-01-30
