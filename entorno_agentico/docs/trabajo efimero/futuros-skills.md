  Skills Recomendados para Futuro                                                                
                                                                                                 
  A. Pre-Implementación (Exploración y Diseño)                                                   
                                                                                                 
  1. /explore-codebase ⭐⭐⭐                                                                    
                                                                                                 
  Propósito: Explorar y entender código existente antes de implementar                           
                                                                                                 
  Uso:                                                                                           
  /explore-codebase --focus=authentication                                                       
  /explore-codebase --related-to=US-001                                                          
  /explore-codebase --pattern=MVC --component=display                                            
                                                                                                 
  Proceso:                                                                                       
  - Buscar patrones arquitectónicos similares                                                    
  - Identificar componentes relacionados                                                         
  - Analizar dependencias                                                                        
  - Generar mapa de componentes relevantes                                                       
                                                                                                 
  Output:                                                                                        
  - .claude/exploration/US-001-codebase-map.json                                                 
  - Diagrama de componentes relacionados                                                         
  - Lista de archivos a considerar                                                               
                                                                                                 
  Valor: Evita reinventar la rueda, garantiza consistencia con código existente                  
                                                                                                 
  ---                                                                                            
  2. /analyze-impact ⭐⭐                                                                        
                                                                                                 
  Propósito: Analizar impacto de cambios propuestos                                              
                                                                                                 
  Uso:                                                                                           
  /analyze-impact US-001                                                                         
  /analyze-impact --file=app/servicios/autenticacion.py                                          
                                                                                                 
  Proceso:                                                                                       
  - Analizar dependencias (imports, llamadas)                                                    
  - Identificar tests afectados                                                                  
  - Detectar breaking changes potenciales                                                        
  - Calcular "blast radius"                                                                      
                                                                                                 
  Output:                                                                                        
  - Lista de archivos impactados                                                                 
  - Tests que deben ejecutarse                                                                   
  - Riesgos identificados                                                                        
                                                                                                 
  Valor: Previene regresiones, estima esfuerzo real                                              
                                                                                                 
  ---                                                                                            
  3. /design-solution ⭐                                                                         
                                                                                                 
  Propósito: Diseñar solución técnica detallada (más profundo que /generate-plan)                
                                                                                                 
  Uso:                                                                                           
  /design-solution US-001                                                                        
                                                                                                 
  Proceso:                                                                                       
  - Proponer múltiples opciones de diseño                                                        
  - Analizar trade-offs (performance, complejidad, mantenibilidad)                               
  - Generar diagramas (sequence, class, component)                                               
  - Recomendar opción con justificación                                                          
                                                                                                 
  Output:                                                                                        
  - Documento de diseño técnico                                                                  
  - Diagramas UML/C4                                                                             
  - Comparación de alternativas                                                                  
                                                                                                 
  Valor: Decisiones arquitectónicas documentadas y justificadas                                  
                                                                                                 
  ---                                                                                            
  B. Durante Implementación (Tareas Complementarias)                                             
                                                                                                 
  4. /refactor ⭐⭐⭐                                                                            
                                                                                                 
  Propósito: Refactorizar código existente manteniendo funcionalidad                             
                                                                                                 
  Uso:                                                                                           
  /refactor app/presentacion/paneles/display/controlador.py                                      
  /refactor --target=reduce-complexity --file=generador.py                                       
  /refactor --pattern=extract-method --function=procesar_datos                                   
                                                                                                 
  Proceso:                                                                                       
  - Identificar code smells                                                                      
  - Proponer refactorings (extract method, move class, etc.)                                     
  - Aplicar refactoring                                                                          
  - Ejecutar tests para validar                                                                  
  - Medir mejora en métricas (CC, MI)                                                            
                                                                                                 
  Output:                                                                                        
  - Código refactorizado                                                                         
  - Reporte de mejoras (antes/después)                                                           
  - Tests validados                                                                              
                                                                                                 
  Valor: Mantener calidad del código, reducir deuda técnica                                      
                                                                                                 
  ---                                                                                            
  5. /debug-assist ⭐⭐                                                                          
                                                                                                 
  Propósito: Debug asistido de errores y excepciones                                             
                                                                                                 
  Uso:                                                                                           
  /debug-assist --error="AttributeError: 'NoneType' object has no attribute 'valor'"             
  /debug-assist --stacktrace=error.log                                                           
  /debug-assist --test-failure="test_display_actualiza"                                          
                                                                                                 
  Proceso:                                                                                       
  - Analizar stacktrace                                                                          
  - Identificar causa raíz (null check faltante, race condition, etc.)                           
  - Proponer fix                                                                                 
  - Generar test de regresión                                                                    
                                                                                                 
  Output:                                                                                        
  - Análisis de causa raíz                                                                       
  - Fix propuesto                                                                                
  - Test que reproduce el bug                                                                    
                                                                                                 
  Valor: Acelera debugging, previene recurrencia                                                 
                                                                                                 
  ---                                                                                            
  6. /optimize-performance ⭐                                                                    
                                                                                                 
  Propósito: Optimizar código con problemas de performance                                       
                                                                                                 
  Uso:                                                                                           
  /optimize-performance --profile=profile.json                                                   
  /optimize-performance --bottleneck=cargar_datos                                                
                                                                                                 
  Proceso:                                                                                       
  - Analizar profile/flamegraph                                                                  
  - Identificar bottlenecks                                                                      
  - Proponer optimizaciones (caching, lazy loading, algoritmo más eficiente)                     
  - Implementar y benchmarkear                                                                   
                                                                                                 
  Output:                                                                                        
  - Código optimizado                                                                            
  - Benchmark antes/después                                                                      
  - Documentación de trade-offs                                                                  
                                                                                                 
  Valor: Performance mejorado, decisiones basadas en datos                                       
                                                                                                 
  ---                                                                                            
  C. Post-Implementación (Review y Release)                                                      
                                                                                                 
  7. /review-code ⭐⭐⭐                                                                         
                                                                                                 
  Propósito: Code review automatizado previo a PR                                                
                                                                                                 
  Uso:                                                                                           
  /review-code US-001                                                                            
  /review-code --files="app/presentacion/paneles/power/*"                                        
                                                                                                 
  Proceso:                                                                                       
  - Analizar cambios del branch                                                                  
  - Buscar: code smells, bugs potenciales, violaciones de estándares                             
  - Verificar: tests, docs, performance                                                          
  - Generar checklist de review                                                                  
                                                                                                 
  Output:                                                                                        
  - Reporte de review con issues encontrados                                                     
  - Sugerencias de mejora                                                                        
  - Checklist para reviewer humano                                                               
                                                                                                 
  Valor: Catch issues antes de PR, feedback inmediato                                            
                                                                                                 
  ---                                                                                            
  8. /generate-changelog ⭐⭐                                                                    
                                                                                                 
  Propósito: Generar changelog profesional para releases                                         
                                                                                                 
  Uso:                                                                                           
  /generate-changelog --from=v1.0.0 --to=HEAD                                                    
  /generate-changelog --milestone=Sprint-1                                                       
                                                                                                 
  Proceso:                                                                                       
  - Leer commits desde última release                                                            
  - Agrupar por tipo (features, bugfixes, breaking changes)                                      
  - Asociar a USs/tickets                                                                        
  - Generar formato Markdown                                                                     
                                                                                                 
  Output:                                                                                        
  - CHANGELOG.md actualizado                                                                     
  - Notas de release                                                                             
                                                                                                 
  Valor: Comunicación clara de cambios                                                           
                                                                                                 
  ---                                                                                            
  9. /prepare-demo ⭐                                                                            
                                                                                                 
  Propósito: Preparar demo/presentación de feature                                               
                                                                                                 
  Uso:                                                                                           
  /prepare-demo US-001                                                                           
                                                                                                 
  Proceso:                                                                                       
  - Listar funcionalidades implementadas                                                         
  - Generar script de demo                                                                       
  - Crear screenshots/videos                                                                     
  - Preparar FAQs                                                                                
                                                                                                 
  Output:                                                                                        
  - Script de demo                                                                               
  - Assets visuales                                                                              
  - Documentación de usuario                                                                     
                                                                                                 
  Valor: Facilita showcases, mejora comunicación con stakeholders                                
                                                                                                 
  ---                                                                                            
  D. Mantenimiento y Soporte                                                                     
                                                                                                 
  10. /investigate-bug ⭐⭐⭐                                                                    
                                                                                                 
  Propósito: Investigar bug reportado por usuario/QA                                             
                                                                                                 
  Uso:                                                                                           
  /investigate-bug BUG-042                                                                       
  /investigate-bug --symptoms="Display muestra --- después de 5 minutos"                         
                                                                                                 
  Proceso:                                                                                       
  - Leer descripción del bug                                                                     
  - Reproducir localmente                                                                        
  - Analizar código relacionado                                                                  
  - Proponer hipótesis de causa                                                                  
  - Sugerir fix                                                                                  
                                                                                                 
  Output:                                                                                        
  - Análisis de causa raíz                                                                       
  - Steps to reproduce                                                                           
  - Fix propuesto                                                                                
  - Tests de regresión                                                                           
                                                                                                 
  Valor: Acelera triage y resolución de bugs                                                     
                                                                                                 
  ---                                                                                            
  11. /analyze-logs ⭐                                                                           
                                                                                                 
  Propósito: Analizar logs de producción para detectar patrones                                  
                                                                                                 
  Uso:                                                                                           
  /analyze-logs --file=production.log --timerange=1h                                             
  /analyze-logs --error-pattern="ConnectionTimeout"                                              
                                                                                                 
  Proceso:                                                                                       
  - Parsear logs                                                                                 
  - Detectar errores recurrentes                                                                 
  - Identificar patrones (picos de tráfico, errores correlacionados)                             
  - Generar insights                                                                             
                                                                                                 
  Output:                                                                                        
  - Reporte de análisis                                                                          
  - Gráficos de tendencias                                                                       
  - Recomendaciones                                                                              
                                                                                                 
  Valor: Detección proactiva de problemas                                                        
                                                                                                 
  ---                                                                                            
  12. /document-decision (ADR) ⭐⭐                                                              
                                                                                                 
  Propósito: Crear Architecture Decision Record                                                  
                                                                                                 
  Uso:                                                                                           
  /document-decision --title="Usar PyQt6 para UI"                                                
  /document-decision --context=US-001 --decision="MVC con Factory/Coordinator"                   
                                                                                                 
  Proceso:                                                                                       
  - Capturar contexto                                                                            
  - Documentar alternativas consideradas                                                         
  - Justificar decisión                                                                          
  - Listar consecuencias                                                                         
                                                                                                 
  Output:                                                                                        
  - docs/adr/ADR-XXX-titulo.md                                                                   
                                                                                                 
  Valor: Decisiones arquitectónicas documentadas, onboarding más rápido                          
                                                                                                 
  ---                                                                                            
  E. Integración y Automatización                                                                
                                                                                                 
  13. /sync-jira ⭐⭐                                                                            
                                                                                                 
  Propósito: Sincronizar estado con Jira/gestor de tickets                                       
                                                                                                 
  Uso:                                                                                           
  /sync-jira US-001                                                                              
  /sync-jira --update-status=In-Progress                                                         
                                                                                                 
  Proceso:                                                                                       
  - Leer estado del tracking local                                                               
  - Actualizar ticket en Jira (estado, tiempo, comentarios)                                      
  - Adjuntar reportes/links                                                                      
                                                                                                 
  Output:                                                                                        
  - Ticket actualizado en Jira                                                                   
  - Confirmación de sync                                                                         
                                                                                                 
  Valor: Single source of truth, menos trabajo manual                                            
                                                                                                 
  ---                                                                                            
  14. /generate-migration ⭐                                                                     
                                                                                                 
  Propósito: Generar scripts de migración (DB, config, etc.)                                     
                                                                                                 
  Uso:                                                                                           
  /generate-migration --type=database --changes="add column estado_power"                        
  /generate-migration --type=config --from=v1.0 --to=v2.0                                        
                                                                                                 
  Proceso:                                                                                       
  - Detectar cambios en schemas/configs                                                          
  - Generar scripts up/down                                                                      
  - Validar sintaxis                                                                             
                                                                                                 
  Output:                                                                                        
  - Scripts de migración                                                                         
  - Rollback scripts                                                                             
                                                                                                 
  Valor: Deploys seguros, rollback garantizado                                                   
                                                                                                 
  ---                                                                                            
  15. /generate-standup-update ⭐                                                                
                                                                                                 
  Propósito: Generar update automático para standup/daily                                        
                                                                                                 
  Uso:                                                                                           
  /generate-standup-update                                                                       
  /generate-standup-update --date=yesterday                                                      
                                                                                                 
  Proceso:                                                                                       
  - Analizar commits del día                                                                     
  - Leer tracking de USs                                                                         
  - Identificar blockers (tests fallando, etc.)                                                  
  - Resumir progreso                                                                             
                                                                                                 
  Output:                                                                                        
  - Update en formato standup:                                                                   
  Yesterday: Implementé DisplayModelo y DisplayVista (US-001)                                    
  Today: Terminar DisplayControlador y tests                                                     
  Blockers: Ninguno                                                                              
                                                                                                 
  Valor: Standup más productivos, menos tiempo preparándolos                                     
                                                                                                 
  ---                                                                                            
  Priorización Recomendada                                                                       
  ┌───────────────────────┬─────────────┬─────────────────────────────────────────────────┐      
  │         Skill         │  Prioridad  │                      Razón                      │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /explore-codebase     │ ⭐⭐⭐ Alta │ Esencial para consistencia y evitar duplicación │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /refactor             │ ⭐⭐⭐ Alta │ Mantener calidad del código a largo plazo       │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /review-code          │ ⭐⭐⭐ Alta │ Catch issues temprano, mejor calidad            │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /investigate-bug      │ ⭐⭐⭐ Alta │ Acelera debugging, muy común en mantenimiento   │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /analyze-impact       │ ⭐⭐ Media  │ Útil para cambios grandes o áreas críticas      │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /sync-jira            │ ⭐⭐ Media  │ Automatiza trabajo manual, mejora reporting     │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /document-decision    │ ⭐⭐ Media  │ Documentación arquitectónica valiosa            │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /generate-changelog   │ ⭐⭐ Media  │ Comunicación de releases                        │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /debug-assist         │ ⭐⭐ Media  │ Útil pero no siempre necesario                  │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /design-solution      │ ⭐ Baja     │ Solo para features muy complejas                │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ /optimize-performance │ ⭐ Baja     │ Solo cuando hay problemas reales                │      
  ├───────────────────────┼─────────────┼─────────────────────────────────────────────────┤      
  │ Los demás             │ ⭐ Baja     │ Nice to have, no críticos                       │      
  └───────────────────────┴─────────────┴─────────────────────────────────────────────────┘      
  ---                                                                                            
  Integración con los 9 Skills Actuales                                                          
                                                                                                 
  Estos skills se integrarían así:                                                               
                                                                                                 
  ┌─────────────────────────────────────────┐                                                    
  │  PRE-IMPLEMENTACIÓN                     │                                                    
  ├─────────────────────────────────────────┤                                                    
  │ /explore-codebase                       │                                                    
  │ /analyze-impact                         │                                                    
  │ /design-solution (opcional)             │                                                    
  └─────────────────────────────────────────┘                                                    
                ↓                                                                                
  ┌─────────────────────────────────────────┐                                                    
  │  9 FASES ACTUALES                       │                                                    
  ├─────────────────────────────────────────┤                                                    
  │ validate → bdd → plan → implement       │                                                    
  │ → test → integration → bdd-validate     │                                                    
  │ → quality → docs → report               │                                                    
  │                                         │                                                    
  │  Complementarios durante:               │                                                    
  │  • /refactor (entre implement y test)   │                                                    
  │  • /debug-assist (cuando tests fallan)  │                                                    
  │  • /optimize-performance (si necesario) │                                                    
  └─────────────────────────────────────────┘                                                    
                ↓                                                                                
  ┌─────────────────────────────────────────┐                                                    
  │  POST-IMPLEMENTACIÓN                    │                                                    
  ├─────────────────────────────────────────┤                                                    
  │ /review-code                            │                                                    
  │ /sync-jira                              │                                                    
  │ /generate-changelog                     │                                                    
  │ /prepare-demo (opcional)                │                                                    
  └─────────────────────────────────────────┘                                                    
                ↓                                                                                
  ┌─────────────────────────────────────────┐                                                    
  │  MANTENIMIENTO (ciclo continuo)         │                                                    
  ├─────────────────────────────────────────┤                                                    
  │ /investigate-bug                        │                                                    
  │ /analyze-logs                           │                                                    
  │ /document-decision                      │                                                    
  └─────────────────────────────────────────┘                                                    
                                                                                                 
  ---                                                                                            
  Recomendación Final                                                                            
                                                                                                 
  Implementar en este orden:                                                                     
                                                                                                 
  1. Fase 1: Los 9 skills actuales (core del workflow)                                           
  2. Fase 2: /explore-codebase, /review-code, /refactor (calidad y consistencia)                 
  3. Fase 3: /investigate-bug, /debug-assist (soporte y mantenimiento)                           
  4. Fase 4: /sync-jira, /document-decision (integración y documentación)                        
  5. Fase 5: El resto según necesidad real