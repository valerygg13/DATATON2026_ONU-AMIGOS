"""DataGuard: validación de estructura, códigos especiales, rangos y ponderadores.

Contrato: recibe un DataFrame crudo + la config de config/variables.yaml y
config/reglas_calidad.yaml, y devuelve (df_limpio, reporte_incidencias) sin alterar
automáticamente los datos salvo lo que el reporte deje explícito.
"""

from __future__ import annotations

import pandas as pd


def validar_estructura(df: pd.DataFrame, variables_esperadas: list[str]) -> list[str]:
    """Devuelve la lista de variables esperadas que faltan en df."""
    raise NotImplementedError


def detectar_codigos_especiales(df: pd.DataFrame, columna: str, codigos: dict) -> pd.Series:
    """Devuelve una máscara booleana de filas con código especial (no sabe/no responde) en columna."""
    raise NotImplementedError


def validar_ponderador(df: pd.DataFrame, columna_factor: str) -> list[str]:
    """Reporta incidencias si el ponderador tiene nulos, ceros o negativos."""
    raise NotImplementedError
