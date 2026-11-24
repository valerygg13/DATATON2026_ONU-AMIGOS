"""StatShield: bloqueo de cruces no permitidos, advertencias de tamaño muestral,
registro de definiciones usadas en cada resultado.

Lee los umbrales y desagregaciones permitidas/bloqueadas de config/reglas_calidad.yaml.
"""

from __future__ import annotations

import pandas as pd


class DesagregacionNoAutorizada(Exception):
    """Se intentó una desagregación fuera del dominio de estudio permitido."""


def verificar_desagregacion(by: list[str], permitidas: list[str], bloqueadas: list[str]) -> None:
    """Lanza DesagregacionNoAutorizada si `by` incluye alguna dimensión bloqueada."""
    raise NotImplementedError


def advertencia_tamano_muestral(n_no_ponderado: int, minimo: int) -> str | None:
    """Devuelve un mensaje de advertencia si n_no_ponderado < minimo, o None si está OK."""
    raise NotImplementedError
