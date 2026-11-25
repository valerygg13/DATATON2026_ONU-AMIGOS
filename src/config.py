"""Carga de config/variables.yaml y config/reglas_calidad.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR_CONFIG = RAIZ / "config"


def cargar_yaml(nombre: str) -> dict:
    with open(DIR_CONFIG / nombre, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cargar_config() -> tuple[dict, dict]:
    """Devuelve (variables, reglas) tal como están en config/."""
    return cargar_yaml("variables.yaml"), cargar_yaml("reglas_calidad.yaml")
