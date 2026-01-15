"""Tests unitarios para EstadoBateria.

Cubre:
- Creación con dataclass
- Método to_string() (formato TCP)
- Método validar_rango()
- Timestamp automático
"""
import pytest
from datetime import datetime
from unittest.mock import patch

from app.dominio.estado_bateria import EstadoBateria


class TestEstadoBateriaCreacion:
    """Tests de creación de EstadoBateria."""

    def test_crear_con_voltaje(self):
        """Crear EstadoBateria con voltaje."""
        estado = EstadoBateria(voltaje=12.5)

        assert estado.voltaje == 12.5
        assert isinstance(estado.timestamp, datetime)
        assert estado.en_rango is True

    def test_crear_con_todos_los_parametros(self):
        """Crear con todos los parámetros."""
        fecha = datetime(2026, 1, 13, 10, 30, 0)
        estado = EstadoBateria(
            voltaje=13.7,
            timestamp=fecha,
            en_rango=False
        )

        assert estado.voltaje == 13.7
        assert estado.timestamp == fecha
        assert estado.en_rango is False

    def test_timestamp_usa_datetime_now(self):
        """Timestamp usa datetime.now() si no se especifica."""
        # Guardar el tiempo antes de crear el estado
        antes = datetime.now()

        estado = EstadoBateria(voltaje=12.0)

        # Guardar el tiempo después de crear el estado
        despues = datetime.now()

        # El timestamp debe estar entre antes y después (rango muy pequeño)
        assert antes <= estado.timestamp <= despues
        # Verificar que es un datetime válido
        assert isinstance(estado.timestamp, datetime)


class TestEstadoBateriaFormatoTCP:
    """Tests del método to_string() para formato TCP."""

    def test_to_string_formato_correcto(self):
        """to_string() retorna formato 'X.XX\\n'."""
        estado = EstadoBateria(voltaje=12.5)
        resultado = estado.to_string()

        assert resultado == "12.50\n"

    def test_to_string_con_dos_decimales(self):
        """to_string() siempre usa 2 decimales."""
        estado = EstadoBateria(voltaje=10.0)
        resultado = estado.to_string()

        assert resultado == "10.00\n"

    def test_to_string_redondea_correctamente(self):
        """to_string() redondea a 2 decimales."""
        estado = EstadoBateria(voltaje=12.456)
        resultado = estado.to_string()

        assert resultado == "12.46\n"

    def test_to_string_termina_con_newline(self):
        """to_string() siempre termina con \\n."""
        estado = EstadoBateria(voltaje=14.8)
        resultado = estado.to_string()

        assert resultado.endswith("\n")
        assert resultado == "14.80\n"


class TestEstadoBateriaValidarRango:
    """Tests del método validar_rango()."""

    def test_validar_rango_dentro_limites(self):
        """validar_rango() retorna True si está dentro."""
        estado = EstadoBateria(voltaje=12.5)
        resultado = estado.validar_rango(10.0, 15.0)

        assert resultado is True
        assert estado.en_rango is True

    def test_validar_rango_en_limite_inferior(self):
        """validar_rango() retorna True en límite inferior."""
        estado = EstadoBateria(voltaje=10.0)
        resultado = estado.validar_rango(10.0, 15.0)

        assert resultado is True
        assert estado.en_rango is True

    def test_validar_rango_en_limite_superior(self):
        """validar_rango() retorna True en límite superior."""
        estado = EstadoBateria(voltaje=15.0)
        resultado = estado.validar_rango(10.0, 15.0)

        assert resultado is True
        assert estado.en_rango is True

    def test_validar_rango_fuera_inferior(self):
        """validar_rango() retorna False si está por debajo."""
        estado = EstadoBateria(voltaje=9.5)
        resultado = estado.validar_rango(10.0, 15.0)

        assert resultado is False
        assert estado.en_rango is False

    def test_validar_rango_fuera_superior(self):
        """validar_rango() retorna False si está por encima."""
        estado = EstadoBateria(voltaje=15.5)
        resultado = estado.validar_rango(10.0, 15.0)

        assert resultado is False
        assert estado.en_rango is False

    def test_validar_rango_actualiza_atributo(self):
        """validar_rango() actualiza el atributo en_rango."""
        estado = EstadoBateria(voltaje=20.0, en_rango=True)

        # Inicialmente True
        assert estado.en_rango is True

        # Validar fuera de rango debe cambiar a False
        estado.validar_rango(10.0, 15.0)
        assert estado.en_rango is False


class TestEstadoBateriaIntegracion:
    """Tests de integración de EstadoBateria."""

    def test_crear_validar_y_formatear(self):
        """Flujo completo: crear → validar → formatear."""
        estado = EstadoBateria(voltaje=12.75)

        # Validar
        es_valido = estado.validar_rango(10.0, 15.0)
        assert es_valido is True

        # Formatear para TCP
        mensaje = estado.to_string()
        assert mensaje == "12.75\n"

    def test_estado_fuera_rango_se_formatea_correctamente(self):
        """Estado fuera de rango aún se formatea bien."""
        estado = EstadoBateria(voltaje=20.0)

        estado.validar_rango(10.0, 15.0)
        assert estado.en_rango is False

        # El formato no depende de en_rango
        mensaje = estado.to_string()
        assert mensaje == "20.00\n"
