"""Modelo del panel de configuración de conexión."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ConexionModelo:
    """Modelo del panel de conexión.

    Attributes:
        ip: Dirección IP del Raspberry Pi
        puerto_recv: Puerto para recibir estado (14001)
        puerto_send: Puerto para enviar comandos (14000)
        ip_valida: Si la IP tiene formato válido
        mensaje_error: Mensaje de error de validación (vacío si válida)
    """

    ip: str
    puerto_recv: int
    puerto_send: int
    ip_valida: bool = True
    mensaje_error: str = ""

    def __post_init__(self):
        """Valida que los puertos sean válidos."""
        # Validar puerto recv
        if not (1024 <= self.puerto_recv <= 65535):
            raise ValueError(
                f"Puerto recv inválido: {self.puerto_recv}. "
                f"Debe estar entre 1024 y 65535."
            )

        # Validar puerto send
        if not (1024 <= self.puerto_send <= 65535):
            raise ValueError(
                f"Puerto send inválido: {self.puerto_send}. "
                f"Debe estar entre 1024 y 65535."
            )

    @staticmethod
    def validar_ip(ip: str) -> tuple[bool, str]:
        """Valida formato de dirección IPv4.

        Args:
            ip: Dirección IP a validar

        Returns:
            Tupla (es_valida, mensaje_error)
            - es_valida: True si la IP es válida
            - mensaje_error: Descripción del error (vacío si válida)

        Examples:
            >>> ConexionModelo.validar_ip("192.168.1.50")
            (True, "")
            >>> ConexionModelo.validar_ip("999.999.999.999")
            (False, "Octeto fuera de rango: 999")
            >>> ConexionModelo.validar_ip("192.168.1")
            (False, "Formato inválido (xxx.xxx.xxx.xxx)")
        """
        # Regex para IPv4
        patron = r"^(\d{1,3}\.){3}\d{1,3}$"

        if not re.match(patron, ip):
            return False, "Formato inválido (xxx.xxx.xxx.xxx)"

        # Validar rango de octetos (0-255)
        octetos = ip.split(".")
        for octeto in octetos:
            valor = int(octeto)
            if not (0 <= valor <= 255):
                return False, f"Octeto fuera de rango: {octeto}"

        return True, ""
