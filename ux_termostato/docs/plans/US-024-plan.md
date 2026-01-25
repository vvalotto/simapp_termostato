# Plan de Implementación - US-024: Ventana Principal

## Información de la Historia

- **ID:** US-024
- **Título:** Implementar Ventana Principal
- **Puntos:** 5
- **Prioridad:** CRÍTICA
- **Épica:** Arquitectura e Integración
- **Estado:** En Desarrollo
- **Branch:** `development/simulador-ux-US024`

---

## Descripción

**Como** desarrollador del sistema
**Quiero** implementar la ventana principal de la aplicación
**Para** tener un punto de entrada único que coordine todo

---

## Criterios de Aceptación

- [ ] Clase `VentanaPrincipalUX` hereda de `QMainWindow`
- [ ] Constructor recibe Factory
- [ ] Ciclo de vida completo: `_inicializar()` → `_configurar_ventana()` → `_crear_componentes()` → `_crear_coordinator()` → `_crear_ui()`
- [ ] Método `iniciar()` público que muestra la ventana e inicia servidor
- [ ] Método `cerrar()` que limpia recursos
- [ ] Override `closeEvent()` para cleanup
- [ ] Manejo de errores con try/catch
- [ ] Logging apropiado en cada fase
- [ ] Tests de integración (100% coverage)
- [ ] Pylint ≥ 8.0

---

## Ciclo de Vida de la Ventana

```
__init__(factory)
    ↓
_inicializar()
    ↓
_configurar_ventana()      # Título, tamaño, tema
    ↓
_crear_componentes()        # Factory → Paneles, Servidor, Cliente
    ↓
_crear_coordinator()        # UXCoordinator + conectar_signals()
    ↓
_crear_ui()                 # UICompositor → setCentralWidget()
    ↓
iniciar()                   # Servidor.start() + show()
    ↓
[Usuario cierra ventana]
    ↓
closeEvent()
    ↓
cerrar()                    # Servidor.stop() + cleanup
```

---

## Componentes a Implementar

### 1. VentanaPrincipalUX

**Archivo:** `app/presentacion/ui_principal.py`

**Atributos:**
```python
class VentanaPrincipalUX(QMainWindow):
    def __init__(self, factory: ComponenteFactoryUX):
        self._factory = factory
        self._componentes = {}          # Dict de paneles MVC
        self._servidor_estado = None    # ServidorEstado
        self._cliente_comandos = None   # ClienteComandos
        self._coordinator = None        # UXCoordinator
        self._compositor = None         # UICompositor
```

**Métodos:**
1. `__init__(factory)` - Constructor
2. `_inicializar()` - Orquestador principal
3. `_configurar_ventana()` - Configuración de ventana
4. `_crear_componentes()` - Creación de paneles y servicios
5. `_crear_coordinator()` - Creación y conexión de señales
6. `_crear_ui()` - Ensamblado de UI
7. `iniciar()` - Inicio público
8. `cerrar()` - Cleanup
9. `closeEvent(event)` - Override Qt

---

## Tasks de Implementación

### Fase 1: Implementación ✅

- [x] **Task 1.1:** Estructura básica de VentanaPrincipalUX (30 min)
  - [x] Clase heredando de QMainWindow
  - [x] Constructor con factory
  - [x] Atributos privados
  - [x] Llamada a `_inicializar()`

- [x] **Task 1.2:** Método `_configurar_ventana()` (30 min)
  - [x] Título: "UX Termostato Desktop"
  - [x] Tamaño: 600x800 (mínimo 500x700)
  - [x] Centrar en pantalla
  - [x] Aplicar tema oscuro (load_dark_theme)
  - [x] Logging

- [x] **Task 1.3:** Método `_crear_componentes()` (45 min)
  - [x] Crear todos los paneles via `factory.crear_todos_paneles()`
  - [x] Almacenar en `self._componentes`
  - [x] Crear ServidorEstado via factory
  - [x] Crear ClienteComandos via factory
  - [x] Logging de componentes creados

- [x] **Task 1.4:** Método `_crear_coordinator()` (30 min)
  - [x] Extraer controladores de `self._componentes`
  - [x] Crear UXCoordinator (import dinámico)
  - [x] Llamar a `coordinator.conectar_signals()`
  - [x] Almacenar en `self._coordinator`
  - [x] Logging

- [x] **Task 1.5:** Método `_crear_ui()` (30 min)
  - [x] Crear UICompositor con paneles
  - [x] Llamar a `compositor.crear_layout()`
  - [x] `setCentralWidget(widget)`
  - [x] Logging

- [x] **Task 1.6:** Método `iniciar()` (20 min)
  - [x] Iniciar ServidorEstado
  - [x] `self.show()`
  - [x] Logging: "Aplicación iniciada"
  - [x] Retorna self (chaining)

- [x] **Task 1.7:** Método `cerrar()` (30 min)
  - [x] Detener ServidorEstado
  - [x] Cerrar conexiones
  - [x] Logging: "Aplicación cerrada"
  - [x] `super().close()`

- [x] **Task 1.8:** Override `closeEvent()` (15 min)
  - [x] Llamar a `self.cerrar()`
  - [x] `event.accept()`

- [x] **Task 1.9:** Manejo de errores (30 min)
  - [x] Try/catch en `_crear_componentes()`
  - [x] Try/catch en `iniciar()`
  - [x] QMessageBox para errores críticos

**Subtotal Implementación:** ~4 horas

---

### Fase 2: Tests Unitarios 🔲

- [ ] **Task 2.1:** Setup de fixtures (45 min)
  - [ ] Fixture `qapp`
  - [ ] Fixture `config_ux`
  - [ ] Fixture `factory_ux`
  - [ ] Fixture `ventana_principal`

- [ ] **Task 2.2:** Tests de creación (1 hora)
  - [ ] test_crear_ventana_exitoso()
  - [ ] test_ventana_tiene_factory()
  - [ ] test_inicializacion_completa()
  - [ ] test_componentes_creados()

- [ ] **Task 2.3:** Tests de configuración (45 min)
  - [ ] test_titulo_ventana()
  - [ ] test_tamano_ventana()
  - [ ] test_tamano_minimo()
  - [ ] test_ventana_centrada()

- [ ] **Task 2.4:** Tests de ciclo de vida (1 hora)
  - [ ] test_iniciar_muestra_ventana()
  - [ ] test_iniciar_inicia_servidor()
  - [ ] test_cerrar_detiene_servidor()
  - [ ] test_close_event_llama_cerrar()

- [ ] **Task 2.5:** Tests de integración (1.5 horas)
  - [ ] test_ui_compositor_integrado()
  - [ ] test_coordinator_conectado()
  - [ ] test_paneles_visibles()
  - [ ] test_servidor_recibe_datos()

- [ ] **Task 2.6:** Tests de errores (45 min)
  - [ ] test_error_crear_componentes()
  - [ ] test_error_iniciar_servidor()
  - [ ] test_manejo_excepcion_graceful()

**Subtotal Tests:** ~5.5 horas

---

### Fase 3: Quality Gates 🔲

- [ ] **Task 3.1:** Ejecutar tests (15 min)
  ```bash
  pytest tests/test_ui_principal.py -v --cov=app/presentacion/ui_principal
  ```
  - [ ] Coverage ≥ 95%

- [ ] **Task 3.2:** Ejecutar pylint (15 min)
  ```bash
  pylint app/presentacion/ui_principal.py
  ```
  - [ ] Score ≥ 8.0

- [ ] **Task 3.3:** Verificar métricas (15 min)
  ```bash
  radon cc app/presentacion/ui_principal.py -a
  radon mi app/presentacion/ui_principal.py
  ```
  - [ ] CC ≤ 10
  - [ ] MI > 20

**Subtotal Quality:** ~45 min

---

### Fase 4: Git Workflow 🔲

- [ ] **Task 4.1:** Commit implementación (10 min)
  ```bash
  git add app/presentacion/ui_principal.py
  git commit -m "feat(US-024): implementar VentanaPrincipalUX"
  ```

- [ ] **Task 4.2:** Commit tests (10 min)
  ```bash
  git add tests/test_ui_principal.py tests/conftest.py
  git commit -m "test(US-024): agregar tests unitarios VentanaPrincipalUX"
  ```

- [ ] **Task 4.3:** Push y crear PR (10 min)
  ```bash
  git push origin development/simulador-ux-US024
  gh pr create --title "US-024: VentanaPrincipalUX" --body "..."
  ```

**Subtotal Git:** ~30 min

---

## Estimación Total

| Fase | Duración Estimada |
|------|-------------------|
| Implementación | 4.0 horas |
| Tests Unitarios | 5.5 horas |
| Quality Gates | 0.75 horas |
| Git Workflow | 0.5 horas |
| **TOTAL** | **10.75 horas** |

---

## Dependencias

### Requeridas (Completadas ✅)
- ✅ US-020: Capa Dominio
- ✅ US-021: Capa Comunicación (ServidorEstado, ClienteComandos)
- ✅ US-022: Factory + Coordinator
- ✅ US-023: UICompositor

### Bloquea
- 🔲 US-025: run.py (necesita VentanaPrincipalUX)

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Servidor no inicia correctamente | Media | Alto | Try/catch robusto + logging detallado |
| Memory leaks al cerrar | Media | Medio | Cleanup explícito de recursos Qt |
| Señales no conectadas | Baja | Alto | Tests de integración exhaustivos |
| Cierre no graceful | Media | Medio | Override closeEvent + cleanup ordenado |

---

## Notas de Implementación

### Patrón de Referencia
Seguir el patrón de `simulador_temperatura/run.py` (AplicacionSimulador):
- Constructor carga config y crea factory
- Métodos privados para cada fase del setup
- Métodos públicos para lifecycle (iniciar/cerrar)
- Logging en cada fase

### Diferencias con Simuladores
- **ux_termostato:** VentanaPrincipalUX ES la ventana (QMainWindow)
- **simuladores:** UIPrincipalCompositor es la ventana, AplicacionSimulador es wrapper
- **ux_termostato:** Servidor se inicia en `iniciar()`, no en constructor
- **ux_termostato:** Usa UICompositor (nuevo en US-023)

### Tema Oscuro
Usar ThemeProvider de `compartido/estilos`:
```python
from compartido.estilos import ThemeProvider

ThemeProvider.aplicar_tema_oscuro(self)
```

### Centrar Ventana
```python
def _centrar_ventana(self):
    qr = self.frameGeometry()
    cp = QApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())
```

---

## Checklist de Progreso

### Implementación
- [x] Estructura básica de VentanaPrincipalUX
- [x] Método `_configurar_ventana()`
- [x] Método `_crear_componentes()`
- [x] Método `_crear_coordinator()`
- [x] Método `_crear_ui()`
- [x] Método `iniciar()`
- [x] Método `cerrar()`
- [x] Override `closeEvent()`
- [x] Manejo de errores
- [x] Resolución de import circular (TYPE_CHECKING + import dinámico)

### Tests
- [ ] Fixtures de conftest.py
- [ ] Tests de creación
- [ ] Tests de configuración
- [ ] Tests de ciclo de vida
- [ ] Tests de integración
- [ ] Tests de errores

### Quality
- [ ] Coverage ≥ 95%
- [ ] Pylint ≥ 8.0
- [ ] CC ≤ 10
- [ ] MI > 20

### Git
- [ ] Branch creada ✅
- [ ] Commit de implementación
- [ ] Commit de tests
- [ ] PR creada
- [ ] PR mergeada a main

---

## Resultados Finales

**Métricas de Calidad:**
- Coverage: __%
- Pylint: __/10
- CC: __
- MI: __

**Tiempo Real:**
- Implementación: __ horas
- Tests: __ horas
- Total: __ horas
- Varianza: __%

**Estado:** 🔲 Pendiente

---

**Última actualización:** 2026-01-25
**Responsable:** Claude Code + Victor Valotto
