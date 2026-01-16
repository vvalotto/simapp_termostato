# Feature: US-001 - Ver temperatura ambiente actual

Feature: Ver temperatura ambiente actual
  Como usuario del termostato
  Quiero ver la temperatura ambiente actual en un display grande y claro
  Para conocer en todo momento las condiciones de mi hogar

  Background:
    Given la aplicación ux_termostato está iniciada
    And la configuración está cargada correctamente

  Scenario: Display muestra temperatura cuando hay conexión activa
    Given el termostato está encendido
    And hay conexión activa con el Raspberry Pi
    When se recibe temperatura de 22.5°C desde el servidor
    Then el display muestra "22.5" en formato X.X
    And el label superior muestra "Temperatura Ambiente"
    And el fondo del display es verde oscuro (LCD simulado)
    And la fuente del valor es grande (≥48px)

  Scenario: Display actualiza temperatura en tiempo real
    Given el display muestra actualmente "22.5°C"
    And hay conexión activa con el Raspberry Pi
    When se recibe nueva temperatura de 23.0°C
    Then el display actualiza inmediatamente a "23.0"
    And no hay delay visible (< 100ms)

  Scenario: Display muestra indicador cuando no hay conexión
    Given el termostato está encendido
    And NO hay conexión con el Raspberry Pi
    Then el display muestra "---" en lugar de temperatura
    And el label muestra "APAGADO" o similar

  Scenario: Display mantiene formato correcto con decimales
    Given hay conexión activa con el Raspberry Pi
    When se recibe temperatura de 20.0°C
    Then el display muestra "20.0" (con un decimal)
    When se recibe temperatura de 25.5°C
    Then el display muestra "25.5"

  Scenario: Display es legible con temperatura extrema
    Given hay conexión activa con el Raspberry Pi
    When se recibe temperatura de -5.5°C
    Then el display muestra "-5.5" correctamente
    And el valor negativo es visible y legible

  Scenario: Display responde a cambio de estado de encendido
    Given el termostato está apagado
    And el display muestra "---"
    When el usuario enciende el termostato
    And se recibe temperatura de 22.0°C
    Then el display muestra "22.0"
    And el label cambia a "Temperatura Ambiente"
