"""DataGuard: validación de estructura, códigos especiales, rangos y ponderadores.

Contrato: recibe un DataFrame crudo + la config de config/variables.yaml y
config/reglas_calidad.yaml, y devuelve (df_limpio, reporte_incidencias) sin alterar
automáticamente los datos salvo lo que el reporte deje explícito.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def cargar_base(ruta: str | Path) -> pd.DataFrame:
    """Lee una base ENEIC en .sav, .xlsx o .csv sin transformar valores."""
    ruta = Path(ruta)
    ext = ruta.suffix.lower()
    if ext == ".sav":
        import pyreadstat

        df, _ = pyreadstat.read_sav(str(ruta), apply_value_formats=False)
        return df
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(ruta)
    if ext == ".csv":
        return pd.read_csv(ruta)
    raise ValueError(f"Formato no soportado: {ext} (usar .sav, .xlsx o .csv)")


def validar_estructura(df: pd.DataFrame, variables_esperadas: list[str]) -> list[str]:
    """Devuelve la lista de variables esperadas que faltan en df."""
    return [v for v in variables_esperadas if v not in df.columns]


def detectar_codigos_especiales(df: pd.DataFrame, columna: str, codigos: dict) -> pd.Series:
    """Devuelve una máscara booleana de filas con código especial (no sabe/no responde) en columna."""
    valores = [v for k, v in codigos.items() if k != "aplicar_a"]
    return pd.to_numeric(df[columna], errors="coerce").isin(valores)


def validar_ponderador(df: pd.DataFrame, columna_factor: str) -> list[str]:
    """Reporta incidencias si el ponderador tiene nulos, ceros o negativos."""
    if columna_factor not in df.columns:
        return [f"Ponderador '{columna_factor}' no existe en la base: no se puede expandir a población."]
    factor = pd.to_numeric(df[columna_factor], errors="coerce")
    incidencias = []
    nulos = int(factor.isna().sum())
    ceros = int((factor == 0).sum())
    negativos = int((factor < 0).sum())
    if nulos:
        incidencias.append(f"Ponderador '{columna_factor}': {nulos} valores nulos o no numéricos.")
    if ceros:
        incidencias.append(f"Ponderador '{columna_factor}': {ceros} valores en cero.")
    if negativos:
        incidencias.append(f"Ponderador '{columna_factor}': {negativos} valores negativos.")
    return incidencias


def validar_rangos(df: pd.DataFrame, rangos: dict[str, list]) -> list[str]:
    """Reporta valores no nulos fuera de [min, max] por variable."""
    incidencias = []
    for columna, (minimo, maximo) in rangos.items():
        if columna not in df.columns:
            continue
        valores = pd.to_numeric(df[columna], errors="coerce")
        fuera = int((valores.notna() & ~valores.between(minimo, maximo)).sum())
        if fuera:
            incidencias.append(f"'{columna}': {fuera} valores fuera del rango válido [{minimo}, {maximo}].")
    return incidencias


def validar_flags(df: pd.DataFrame, config_flags: dict) -> list[str]:
    """Verifica codificación 1/NaN de las variables flag y sus relaciones de inclusión."""
    incidencias = []
    columnas = [c for c in config_flags.get("columnas", []) if c in df.columns]
    for c in columnas:
        invalidos = int((df[c].notna() & (df[c] != 1)).sum())
        if invalidos:
            incidencias.append(f"Flag '{c}': {invalidos} valores distintos de 1/NaN.")

    for hijo, padre in config_flags.get("subconjuntos", {}).items():
        if hijo in columnas and padre in columnas:
            fuera = int(((df[hijo] == 1) & (df[padre] != 1)).sum())
            if fuera:
                incidencias.append(f"Flag '{hijo}': {fuera} casos marcados sin pertenecer a '{padre}'.")

    for a, b in config_flags.get("disjuntos", []):
        if a in columnas and b in columnas:
            ambos = int(((df[a] == 1) & (df[b] == 1)).sum())
            if ambos:
                incidencias.append(f"Flags '{a}' y '{b}': {ambos} casos marcados en ambos (deben ser disjuntos).")
    return incidencias


def ejecutar_dataguard(df: pd.DataFrame, variables: dict, reglas: dict) -> tuple[pd.DataFrame, list[str]]:
    """Valida la base Personas y devuelve (df_limpio, reporte_incidencias).

    Única alteración: los códigos especiales en `codigos_especiales.aplicar_a` pasan a NaN,
    y queda registrado en el reporte. No elimina filas.
    """
    mapeo = variables["base_personas"]
    incidencias = []

    faltantes = validar_estructura(df, [v for v in mapeo.values() if v])
    if faltantes:
        incidencias.append(f"Variables esperadas ausentes: {', '.join(faltantes)}.")

    incidencias += validar_ponderador(df, reglas["ponderador"]["variable"])

    df_limpio = df.copy()
    codigos = reglas.get("codigos_especiales", {})
    for columna in codigos.get("aplicar_a", []):
        if columna not in df_limpio.columns:
            continue
        mascara = detectar_codigos_especiales(df_limpio, columna, codigos)
        n = int(mascara.sum())
        if n:
            df_limpio.loc[mascara, columna] = float("nan")
            incidencias.append(f"'{columna}': {n} códigos especiales (no sabe/no responde) convertidos a NaN.")

    incidencias += validar_rangos(df_limpio, reglas.get("rangos_validos", {}))
    incidencias += validar_flags(df_limpio, reglas.get("variables_flag", {}))
    return df_limpio, incidencias
