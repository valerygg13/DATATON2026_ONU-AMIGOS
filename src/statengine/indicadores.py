"""StatEngine: cálculo reproducible de indicadores ponderados por sexo y dominio.

Todas las funciones reciben un DataFrame ya validado por DataGuard y el nombre de la
columna de ponderador (ver config/variables.yaml: base_personas.ponderador).

Las columnas de `by` son nombres lógicos (`sexo`, `dominio`, `area`) que agrega
`agregar_dimensiones`. Fórmulas: docs/indicadores.md.
"""

from __future__ import annotations

import pandas as pd

DIMENSIONES = ("sexo", "dominio", "area")


def agregar_dimensiones(df: pd.DataFrame, variables: dict) -> pd.DataFrame:
    """Copia de df con columnas `sexo`, `dominio`, `area` etiquetadas según config/variables.yaml.

    Códigos sin etiqueta (o NaN tras DataGuard) quedan como NaN y no entran a ningún grupo.
    """
    mapeo = variables["base_personas"]
    df = df.copy()
    for dim in DIMENSIONES:
        columna = mapeo.get(dim)
        if columna in df.columns:
            etiquetas = variables.get(f"etiquetas_{dim}", {})
            df[dim] = pd.to_numeric(df[columna], errors="coerce").map(etiquetas)
    return df


def _agregar(df: pd.DataFrame, by: list[str] | None, calcular) -> pd.DataFrame:
    """Aplica `calcular(grupo) -> (valor, n)` por grupo de `by` (o al total si by está vacío)."""
    by = list(by or [])
    if not by:
        valor, n = calcular(df)
        return pd.DataFrame([{"valor": valor, "n_no_ponderado": n}])
    filas = []
    for clave, grupo in df.groupby(by, dropna=True, observed=True):
        clave = clave if isinstance(clave, tuple) else (clave,)
        valor, n = calcular(grupo)
        filas.append({**dict(zip(by, clave)), "valor": valor, "n_no_ponderado": n})
    return pd.DataFrame(filas, columns=by + ["valor", "n_no_ponderado"])


def participacion_laboral(
    df: pd.DataFrame, ponderador: str, by: list[str] | None = None, pet: str = "PET", pea: str = "PEA"
) -> pd.DataFrame:
    """PEA / PET ponderado, agregado por `by` (ej. ['sexo'] o ['sexo', 'dominio']).

    valor = Σ FACTOR (PEA == 1) / Σ FACTOR (PET == 1), como proporción 0–1.
    n_no_ponderado = personas en PET del grupo.
    """
    def calcular(g: pd.DataFrame):
        en_pet = g[pet] == 1
        denominador = g.loc[en_pet, ponderador].sum()
        numerador = g.loc[en_pet & (g[pea] == 1), ponderador].sum()
        valor = numerador / denominador if denominador > 0 else float("nan")
        return valor, int(en_pet.sum())

    return _agregar(df, by, calcular)


def ingreso_laboral_medio(
    df: pd.DataFrame,
    ponderador: str,
    by: list[str] | None = None,
    ingreso: str = "YLAB_PUBLI",
    ocupados: str = "OCUPADOS",
    excluir_ceros: bool = False,
) -> pd.DataFrame:
    """Promedio ponderado del ingreso laboral en la población elegible.

    Población elegible: OCUPADOS == 1 con `ingreso` no nulo.
    - Faltantes (NaN): se excluyen del numerador y del denominador; nunca se imputan
      como cero, porque un cero falso infla artificialmente la brecha.
    - Ceros reportados: se incluyen por defecto (son ingreso declarado). Con
      `excluir_ceros=True` se excluyen, y debe declararse en la ficha metodológica.
    n_no_ponderado = ocupados con ingreso válido en el grupo.
    """
    def calcular(g: pd.DataFrame):
        y = pd.to_numeric(g[ingreso], errors="coerce")
        elegible = (g[ocupados] == 1) & y.notna()
        if excluir_ceros:
            elegible &= y != 0
        pesos = g.loc[elegible, ponderador]
        total = pesos.sum()
        valor = (pesos * y[elegible]).sum() / total if total > 0 else float("nan")
        return valor, int(elegible.sum())

    return _agregar(df, by, calcular)


def brecha_relativa_ingreso(df_ingreso_por_sexo: pd.DataFrame) -> pd.DataFrame:
    """(media_masculina - media_femenina) / media_masculina * 100, si el denominador es válido.

    Medida descriptiva, no estimación causal de discriminación.

    Recibe la salida de `ingreso_laboral_medio` con `sexo` en `by`; el resto de columnas de
    agregación (ej. `dominio`) se conservan, una fila por combinación. `n_no_ponderado` es el
    menor de los dos grupos (el que limita la precisión), para que StatShield advierta si
    cualquiera de los dos queda bajo el umbral. Si la media masculina es 0 o falta un sexo,
    `valor` es NaN.
    """
    if "sexo" not in df_ingreso_por_sexo.columns:
        raise ValueError("brecha_relativa_ingreso requiere el ingreso medio agregado por 'sexo'.")
    otras = [c for c in df_ingreso_por_sexo.columns if c not in ("sexo", "valor", "n_no_ponderado", "advertencia")]
    claves = otras or ["_total"]
    df = df_ingreso_por_sexo.assign(_total=0, sexo=df_ingreso_por_sexo["sexo"].replace({1: "Hombre", 2: "Mujer"}))
    h = df[df["sexo"] == "Hombre"].set_index(claves)[["valor", "n_no_ponderado"]].add_suffix("_h")
    m = df[df["sexo"] == "Mujer"].set_index(claves)[["valor", "n_no_ponderado"]].add_suffix("_m")
    union = h.join(m, how="outer")

    media_h, media_m = union["valor_h"], union["valor_m"]
    valida = (media_h > 0) & media_m.notna()
    resultado = pd.DataFrame(
        {
            "valor": ((media_h - media_m) / media_h * 100).where(valida),
            "n_no_ponderado": union[["n_no_ponderado_h", "n_no_ponderado_m"]].min(axis=1).fillna(0).astype(int),
            "media_hombres": media_h,
            "media_mujeres": media_m,
            "n_hombres": union["n_no_ponderado_h"].fillna(0).astype(int),
            "n_mujeres": union["n_no_ponderado_m"].fillna(0).astype(int),
        }
    )
    if otras:
        return resultado.reset_index()
    return resultado.reset_index(drop=True)
