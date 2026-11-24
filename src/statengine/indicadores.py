"""StatEngine: cálculo reproducible de indicadores ponderados por sexo y dominio.

Todas las funciones reciben un DataFrame ya validado por DataGuard y el nombre de la
columna de ponderador (ver config/variables.yaml: base_personas.ponderador).
"""

from __future__ import annotations

import pandas as pd


def participacion_laboral(df: pd.DataFrame, ponderador: str, by: list[str] | None = None) -> pd.DataFrame:
    """PEA / PET ponderado, agregado por `by` (ej. ['sexo'] o ['sexo', 'dominio'])."""
    raise NotImplementedError


def ingreso_laboral_medio(df: pd.DataFrame, ponderador: str, by: list[str] | None = None) -> pd.DataFrame:
    """Promedio ponderado del ingreso laboral en la población elegible.

    Debe documentar explícitamente el tratamiento de faltantes y ceros (excluir vs. imputar).
    """
    raise NotImplementedError


def brecha_relativa_ingreso(df_ingreso_por_sexo: pd.DataFrame) -> pd.DataFrame:
    """(media_masculina - media_femenina) / media_masculina * 100, si el denominador es válido.

    Medida descriptiva, no estimación causal de discriminación.
    """
    raise NotImplementedError
