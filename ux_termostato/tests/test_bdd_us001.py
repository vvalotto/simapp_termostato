"""
Step definitions para BDD de US-001 - Ver temperatura ambiente actual.

Este módulo implementa los steps de Gherkin usando pytest-bdd para validar
los escenarios de aceptación de la historia de usuario US-001.
"""

import time
import pytest
from unittest.mock import Mock
from pytest_bdd import scenarios, given, when, then, parsers

from app.presentacion.paneles.display.modelo import DisplayModelo
from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.controlador import DisplayControlador


# Cargar todos los escenarios del feature file
scenarios('features/US-001-ver-temperatura-ambiente.feature')


# ============================================================================
# Fixtures de contexto
# ============================================================================

@pytest.fixture
def contexto(qapp):
    """
    Fixture de contexto compartido para todos los escenarios.

    Contiene referencias a los componentes del sistema MVC y estado compartido.
    """
    return {
        'modelo': None,
        'vista': None,
        'controlador': None,
        'aplicacion_iniciada': False,
        'conexion_activa': False,
        'temperatura_recibida': None,
        'timestamp_actualizacion': None,
    }


# ============================================================================
# Given steps - Precondiciones
# ============================================================================

@given("la aplicación ux_termostato está iniciada")
def aplicacion_iniciada(contexto):
    """Precondición: La aplicación está iniciada."""
    contexto['aplicacion_iniciada'] = True


@given("la configuración está cargada correctamente")
def configuracion_cargada(contexto):
    """Precondición: La configuración está cargada."""
    # Para estos tests, no necesitamos configuración real
    pass


@given("el termostato está encendido")
def termostato_encendido(contexto):
    """Precondición: El termostato está encendido."""
    modelo = DisplayModelo(
        temperatura=0.0,
        modo_vista="ambiente",
        encendido=True,
        error_sensor=False
    )
    vista = DisplayVista()
    vista.show()
    controlador = DisplayControlador(modelo, vista)

    contexto['modelo'] = modelo
    contexto['vista'] = vista
    contexto['controlador'] = controlador


@given("el termostato está apagado")
def termostato_apagado(contexto):
    """Precondición: El termostato está apagado."""
    modelo = DisplayModelo(
        temperatura=0.0,
        modo_vista="ambiente",
        encendido=False,
        error_sensor=False
    )
    vista = DisplayVista()
    vista.show()
    controlador = DisplayControlador(modelo, vista)

    contexto['modelo'] = modelo
    contexto['vista'] = vista
    contexto['controlador'] = controlador


@given("hay conexión activa con el Raspberry Pi")
def conexion_activa(contexto):
    """Precondición: Hay conexión activa con RPi."""
    contexto['conexion_activa'] = True

    # Si el controlador no existe, inicializarlo (escenarios que omiten "termostato está encendido")
    if contexto['controlador'] is None:
        modelo = DisplayModelo(
            temperatura=0.0,
            modo_vista="ambiente",
            encendido=True,
            error_sensor=False
        )
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        contexto['modelo'] = modelo
        contexto['vista'] = vista
        contexto['controlador'] = controlador


@given("NO hay conexión con el Raspberry Pi")
def sin_conexion(contexto):
    """Precondición: No hay conexión con RPi."""
    contexto['conexion_activa'] = False
    # Simular display apagado (sin conexión)
    contexto['controlador'].set_encendido(False)


@given(parsers.parse('el display muestra actualmente "{temperatura}°C"'))
def display_muestra_temperatura(contexto, temperatura):
    """Precondición: El display muestra una temperatura específica."""
    # Si el controlador no existe, inicializarlo primero
    if contexto['controlador'] is None:
        modelo = DisplayModelo(
            temperatura=0.0,
            modo_vista="ambiente",
            encendido=True,
            error_sensor=False
        )
        vista = DisplayVista()
        vista.show()
        controlador = DisplayControlador(modelo, vista)

        contexto['modelo'] = modelo
        contexto['vista'] = vista
        contexto['controlador'] = controlador

    temp_valor = float(temperatura)
    contexto['controlador'].actualizar_temperatura(temp_valor)


@given('el display muestra "---"')
def display_muestra_guiones(contexto):
    """Precondición: El display muestra '---' (sin conexión)."""
    contexto['controlador'].set_encendido(False)


# ============================================================================
# When steps - Acciones
# ============================================================================

@when(parsers.parse('se recibe temperatura de {temperatura}°C desde el servidor'))
def recibe_temperatura(contexto, temperatura):
    """Acción: Se recibe temperatura del servidor."""
    temp_valor = float(temperatura)
    contexto['temperatura_recibida'] = temp_valor
    contexto['timestamp_actualizacion'] = time.time()

    # Simular recepción desde servidor
    estado_servidor = Mock()
    estado_servidor.temp_actual = temp_valor
    estado_servidor.temp_deseada = temp_valor
    estado_servidor.falla_sensor = False

    contexto['controlador'].actualizar_desde_estado(estado_servidor)


@when(parsers.parse('se recibe nueva temperatura de {temperatura}°C'))
def recibe_nueva_temperatura(contexto, temperatura):
    """Acción: Se recibe nueva temperatura (actualización)."""
    recibe_temperatura(contexto, temperatura)


@when(parsers.parse('se recibe temperatura de {temperatura}°C'))
def recibe_temperatura_simple(contexto, temperatura):
    """Acción: Se recibe temperatura (versión simple)."""
    recibe_temperatura(contexto, temperatura)


@when("el usuario enciende el termostato")
def usuario_enciende(contexto):
    """Acción: El usuario enciende el termostato."""
    contexto['controlador'].set_encendido(True)


# ============================================================================
# Then steps - Aserciones
# ============================================================================

@then(parsers.parse('el display muestra "{valor}" en formato X.X'))
def display_muestra_valor_formato(contexto, valor):
    """Aserción: El display muestra el valor con formato correcto."""
    vista = contexto['vista']
    assert vista.label_temp.text() == valor, \
        f"Esperado: {valor}, Actual: {vista.label_temp.text()}"


@then(parsers.parse('el display muestra "{valor}"'))
def display_muestra_valor(contexto, valor):
    """Aserción: El display muestra un valor específico."""
    vista = contexto['vista']
    actual = vista.label_temp.text()

    # Normalizar comparación (remover espacios)
    assert actual.strip() == valor.strip(), \
        f"Esperado: '{valor}', Actual: '{actual}'"


@then(parsers.parse('el display muestra "{valor}" (con un decimal)'))
def display_muestra_valor_con_decimal(contexto, valor):
    """Aserción: El display muestra valor con un decimal."""
    vista = contexto['vista']
    actual = vista.label_temp.text()

    assert actual == valor, f"Esperado: {valor}, Actual: {actual}"
    # Verificar que tiene exactamente un decimal
    assert '.' in actual, "El valor debe contener un punto decimal"
    decimales = actual.split('.')[-1]
    assert len(decimales) == 1, f"Debe tener 1 decimal, tiene {len(decimales)}"


@then(parsers.parse('el display muestra "{valor}" correctamente'))
def display_muestra_valor_correctamente(contexto, valor):
    """Aserción: El display muestra el valor correctamente."""
    display_muestra_valor(contexto, valor)


@then(parsers.parse('el display muestra "{valor}" en lugar de temperatura'))
def display_muestra_en_lugar(contexto, valor):
    """Aserción: El display muestra un valor en lugar de temperatura."""
    display_muestra_valor(contexto, valor)


@then(parsers.parse('el display actualiza inmediatamente a "{valor}"'))
def display_actualiza_inmediatamente(contexto, valor):
    """Aserción: El display actualiza inmediatamente."""
    vista = contexto['vista']
    assert vista.label_temp.text() == valor

    # Verificar que la actualización fue reciente (< 100ms)
    tiempo_transcurrido = time.time() - contexto['timestamp_actualizacion']
    assert tiempo_transcurrido < 0.1, \
        f"Actualización tardó {tiempo_transcurrido:.3f}s (debe ser < 0.1s)"


@then(parsers.parse('el label superior muestra "{texto}"'))
def label_superior_muestra(contexto, texto):
    """Aserción: El label superior muestra un texto específico."""
    vista = contexto['vista']
    assert vista.label_modo.text() == texto, \
        f"Esperado: {texto}, Actual: {vista.label_modo.text()}"


@then(parsers.parse('el label muestra "{texto}" o similar'))
def label_muestra_similar(contexto, texto):
    """Aserción: El label muestra texto similar."""
    vista = contexto['vista']
    actual = vista.label_modo.text()
    assert texto.upper() in actual.upper(), \
        f"Esperado que contenga: {texto}, Actual: {actual}"


@then(parsers.parse('el label cambia a "{texto}"'))
def label_cambia_a(contexto, texto):
    """Aserción: El label cambia a un texto específico."""
    label_superior_muestra(contexto, texto)


@then("el fondo del display es verde oscuro (LCD simulado)")
def fondo_verde_oscuro(contexto):
    """Aserción: El fondo es verde oscuro."""
    vista = contexto['vista']
    stylesheet = vista.styleSheet()
    assert "#065f46" in stylesheet or "#064e3b" in stylesheet, \
        "El stylesheet debe contener colores verdes oscuros"


@then("la fuente del valor es grande (≥48px)")
def fuente_grande(contexto):
    """Aserción: La fuente es grande (≥48px)."""
    vista = contexto['vista']
    font = vista.label_temp.font()
    assert font.pointSize() >= 48, \
        f"Fuente debe ser ≥48px, actual: {font.pointSize()}px"


@then("no hay delay visible (< 100ms)")
def sin_delay_visible(contexto):
    """Aserción: No hay delay visible en la actualización."""
    # Ya validado en display_actualiza_inmediatamente
    tiempo_transcurrido = time.time() - contexto['timestamp_actualizacion']
    assert tiempo_transcurrido < 0.1, \
        f"Delay: {tiempo_transcurrido:.3f}s (debe ser < 0.1s)"


@then("el valor negativo es visible y legible")
def valor_negativo_visible(contexto):
    """Aserción: El valor negativo es visible y legible."""
    vista = contexto['vista']
    texto = vista.label_temp.text()

    # Verificar que empieza con '-'
    assert texto.startswith('-'), \
        f"El valor debe empezar con '-', actual: {texto}"

    # Verificar que el widget es visible
    assert vista.label_temp.isVisible(), \
        "El label de temperatura debe ser visible"
