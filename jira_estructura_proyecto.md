# Estructura de Issues para Jira - Proyecto Simuladores Termostato

**Proyecto:** Simuladores Termostato (ST)
**Fecha de creación:** 2025-12-29

---

## EPIC 1: Infraestructura Base

**Descripción:** Crear la estructura base del proyecto incluyendo configuración compartida, networking base y componentes reutilizables.

### Tareas:

| ID | Tarea | Descripción |
|----|-------|-------------|
| ST-E1-T1 | Crear estructura de carpetas del proyecto | Crear la estructura completa de directorios según el diseño: simulador_temperatura/, simulador_bateria/, ux_termostato/, compartido/, assets/, docs/ |
| ST-E1-T2 | Configurar requirements.txt global | Crear archivo de dependencias con PyQt6, pyqtgraph, python-dotenv, pytest, pytest-qt, radon, pylint, pytest-cov |
| ST-E1-T3 | Crear config.json compartido | Implementar archivo de configuración de red con IPs, puertos y parámetros de cada simulador |
| ST-E1-T4 | Implementar base_socket_client.py | Crear clase base para clientes TCP en compartido/networking/ con conexión, envío y reconexión automática |
| ST-E1-T5 | Implementar base_socket_server.py | Crear clase base para servidores TCP en compartido/networking/ |
| ST-E1-T6 | Implementar widget LED indicator | Crear componente visual LED reutilizable en compartido/widgets/led_indicator.py |
| ST-E1-T7 | Implementar widget ConfigPanel | Crear panel de configuración reutilizable en compartido/widgets/config_panel.py |
| ST-E1-T8 | Implementar widget LogViewer | Crear visor de logs reutilizable en compartido/widgets/log_viewer.py |
| ST-E1-T9 | Crear dark_theme.qss | Implementar hoja de estilos oscura para simular dispositivo embebido |
| ST-E1-T10 | Configurar .gitignore | Crear archivo .gitignore con exclusiones para Python, PyQt6, IDE, testing y quality reports |
| ST-E1-T11 | Crear .env.example | Crear archivo de ejemplo de variables de entorno |

---

## EPIC 2: Simulador de Temperatura

**Descripción:** Desarrollar el simulador de sensor de temperatura con interfaz PyQt6 y comunicación TCP al puerto 14001.

### Tareas:

| ID | Tarea | Descripción |
|----|-------|-------------|
| ST-E2-T1 | Crear estructura simulador_temperatura | Crear directorios: app/, app/configuracion/, app/servicios/, app/general/, app/datos/, tests/, quality/ |
| ST-E2-T2 | Implementar config.py | Crear dataclass de configuración específica del simulador de temperatura |
| ST-E2-T3 | Implementar configurador.py (Singleton) | Crear patrón Singleton para gestión de configuración |
| ST-E2-T4 | Implementar generador_temperatura.py | Crear lógica de simulación: temperatura base, variación senoidal, ruido aleatorio, rangos configurables |
| ST-E2-T5 | Implementar socket_client.py | Crear cliente TCP específico que envía valores de temperatura al puerto 14001 |
| ST-E2-T6 | Implementar ui_principal.py | Crear ventana PyQt6 con controles: slider temperatura, botón conectar, display valor actual, gráfico tiempo real |
| ST-E2-T7 | Crear run.py | Implementar punto de entrada de la aplicación |
| ST-E2-T8 | Crear tests unitarios | Implementar test_generador.py y test_socket.py |
| ST-E2-T9 | Configurar pytest.ini | Crear configuración de pytest para el producto |
| ST-E2-T10 | Configurar scripts de quality | Copiar y adaptar calculate_metrics.py, validate_gates.py, generate_report.py |
| ST-E2-T11 | Ejecutar y validar quality gates | Ejecutar análisis de métricas y asegurar grado A o B |

---

## EPIC 3: Simulador de Batería

**Descripción:** Desarrollar el simulador de sensor de batería con modos de carga/descarga y comunicación TCP al puerto 14002.

### Tareas:

| ID | Tarea | Descripción |
|----|-------|-------------|
| ST-E3-T1 | Crear estructura simulador_bateria | Crear directorios: app/, app/configuracion/, app/servicios/, app/general/, app/datos/, tests/, quality/ |
| ST-E3-T2 | Implementar config.py | Crear dataclass de configuración: voltaje_max, voltaje_min, tasas de carga/descarga |
| ST-E3-T3 | Implementar configurador.py (Singleton) | Crear patrón Singleton para gestión de configuración |
| ST-E3-T4 | Implementar simulador_descarga.py | Crear lógica de descarga exponencial de batería |
| ST-E3-T5 | Implementar simulador_carga.py | Crear lógica de carga con curva característica Li-ion |
| ST-E3-T6 | Implementar socket_client.py | Crear cliente TCP que envía voltaje de batería al puerto 14002 |
| ST-E3-T7 | Implementar ui_principal.py | Crear ventana PyQt6 con: selector modo (carga/descarga), barra de nivel, botón conectar, gráfico voltaje |
| ST-E3-T8 | Crear run.py | Implementar punto de entrada de la aplicación |
| ST-E3-T9 | Crear tests unitarios | Implementar test_simulador.py y test_socket.py |
| ST-E3-T10 | Configurar pytest.ini | Crear configuración de pytest para el producto |
| ST-E3-T11 | Configurar scripts de quality | Copiar y adaptar scripts de calidad |
| ST-E3-T12 | Ejecutar y validar quality gates | Ejecutar análisis de métricas y asegurar grado A o B |

---

## EPIC 4: UX Termostato

**Descripción:** Desarrollar la interfaz de usuario desktop que replica el display del termostato, recibe datos y envía comandos.

### Tareas:

| ID | Tarea | Descripción |
|----|-------|-------------|
| ST-E4-T1 | Crear estructura ux_termostato | Crear directorios: app/, app/configuracion/, app/servicios/, app/general/, app/datos/, app/widgets/, tests/, quality/ |
| ST-E4-T2 | Implementar config.py y configurador.py | Crear configuración específica del UX |
| ST-E4-T3 | Implementar widget display_lcd.py | Crear widget que simula display LCD verde con temperatura |
| ST-E4-T4 | Implementar widget clima_indicator.py | Crear indicador visual de estado: calentando (rojo), enfriando (azul), standby (gris) |
| ST-E4-T5 | Implementar widget led_indicator.py | Crear LEDs de estado: falla sensor, batería baja |
| ST-E4-T6 | Implementar widget temperature_chart.py | Crear gráfico de histórico de temperatura con pyqtgraph |
| ST-E4-T7 | Implementar estado_termostato.py | Crear modelo de datos para estado del termostato (dataclass) |
| ST-E4-T8 | Implementar socket_server.py | Crear servidor TCP en puerto 14003 que recibe JSON del termostato |
| ST-E4-T9 | Implementar socket_client.py | Crear cliente TCP al puerto 14004 para enviar comandos |
| ST-E4-T10 | Implementar ui_principal.py | Crear ventana principal integrando todos los widgets y controles |
| ST-E4-T11 | Crear run.py | Implementar punto de entrada de la aplicación |
| ST-E4-T12 | Crear tests unitarios | Implementar test_estado.py, test_widgets.py, test_networking.py |
| ST-E4-T13 | Configurar pytest.ini y quality | Configurar testing y scripts de calidad |
| ST-E4-T14 | Ejecutar y validar quality gates | Ejecutar análisis de métricas y asegurar grado A o B |

---

## EPIC 5: Integración y Refinamiento

**Descripción:** Integrar los tres productos, validar comunicación con Raspberry Pi y aplicar refinamientos finales.

### Tareas:

| ID | Tarea | Descripción |
|----|-------|-------------|
| ST-E5-T1 | Tests de integración entre simuladores | Crear tests que validen comunicación entre los 3 productos desktop |
| ST-E5-T2 | Validar comunicación con Raspberry Pi | Probar conexión real con ISSE_Termostato en Raspberry Pi |
| ST-E5-T3 | Pruebas de escenarios HIL completos | Ejecutar casos de prueba end-to-end: cambios de temperatura, batería baja, falla sensor |
| ST-E5-T4 | Aplicar estilos finales | Refinar tema oscuro y consistencia visual entre productos |
| ST-E5-T5 | Crear documentación arquitectura.md | Documentar arquitectura del sistema |
| ST-E5-T6 | Crear protocolo_comunicacion.md | Documentar protocolos TCP y formatos de mensajes |
| ST-E5-T7 | Crear manual_usuario.md | Documentar guía de uso para cada simulador |
| ST-E5-T8 | Ejecutar quality en todos los productos | Validar que todos los productos mantengan grado A o B |
| ST-E5-T9 | Crear README.md principal | Documentar instalación, configuración y uso del proyecto |
| ST-E5-T10 | Preparar release v1.0 | Tag de versión y notas de release |

---

## Resumen

| Epic | Nombre | Cantidad de Tareas |
|------|--------|-------------------|
| EPIC 1 | Infraestructura Base | 11 |
| EPIC 2 | Simulador de Temperatura | 11 |
| EPIC 3 | Simulador de Batería | 12 |
| EPIC 4 | UX Termostato | 14 |
| EPIC 5 | Integración y Refinamiento | 10 |
| **TOTAL** | | **58 tareas** |

---

## Dependencias entre Epics

```
EPIC 1 (Infraestructura Base)
    │
    ├──► EPIC 2 (Simulador Temperatura)
    │
    ├──► EPIC 3 (Simulador Batería)
    │
    └──► EPIC 4 (UX Termostato)
              │
              ▼
         EPIC 5 (Integración)
```

- EPIC 1 debe completarse antes de iniciar EPIC 2, 3 y 4
- EPIC 2, 3 y 4 pueden desarrollarse en paralelo
- EPIC 5 requiere que EPIC 2, 3 y 4 estén completados

---

## Criterios de Aceptación Globales

Cada tarea debe cumplir:
1. Código implementado y funcionando
2. Tests unitarios pasando (si aplica)
3. Quality gates pasando (grado A o B)
4. Código revisado y documentado
