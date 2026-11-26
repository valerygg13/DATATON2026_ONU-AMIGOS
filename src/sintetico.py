"""Base Personas sintética con la misma estructura y codificación que ENEIC I 2026.

Solo para pruebas y modo demo de la interfaz cuando no hay datos reales en data/raw/.
Los valores NO representan a Guatemala; nunca publicar resultados calculados con esta base.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generar_personas(n: int = 3000, semilla: int = 2026) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    sexo = rng.choice([1, 2], n)
    edad = rng.integers(0, 90, n)
    dominio = rng.choice([1, 2, 3], n, p=[0.3, 0.3, 0.4])
    area = np.where(dominio == 3, 2, 1)

    pet = edad >= 15
    tasa_actividad = np.where(sexo == 1, 0.8, 0.45)
    pea = pet & (rng.random(n) < tasa_actividad)
    ocupado = pea & (rng.random(n) < 0.97)
    desocupado = pea & ~ocupado
    inactivo = pet & ~pea

    base = np.where(sexo == 1, 3600, 2900) * np.where(dominio == 1, 1.5, 1.0)
    ingreso = np.round(rng.lognormal(np.log(base), 0.5), 2)
    sin_ingreso = rng.random(n) < 0.08  # ej. trabajador familiar no remunerado
    ylab = np.where(ocupado & ~sin_ingreso, ingreso, np.nan)

    def flag(mascara):
        return np.where(mascara, 1.0, np.nan)

    return pd.DataFrame(
        {
            "ANIO": 2026,
            "TRIMESTRE": 6,
            "DOMINIO": dominio,
            "NUM_HOGAR": rng.integers(1, n // 4, n),
            "FACTOR": np.round(rng.uniform(150, 900, n), 4),
            "P00A10": area,
            "P02A02": sexo,
            "P02A03": edad,
            "P05D01": np.where(np.isnan(ylab), np.nan, np.round(ylab * 0.9, 2)),
            "YLAB_PUBLI": ylab,
            "PET": flag(pet),
            "PEA": flag(pea),
            "OCUPADOS": flag(ocupado),
            "DESOCUPADOS": flag(desocupado),
            "INACTIVOS": flag(inactivo),
        }
    )
