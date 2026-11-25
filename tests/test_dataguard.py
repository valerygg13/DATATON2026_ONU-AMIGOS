import numpy as np

from src.config import cargar_config
from src.dataguard.validators import (
    detectar_codigos_especiales,
    ejecutar_dataguard,
    validar_estructura,
    validar_flags,
    validar_ponderador,
)
from src.sintetico import generar_personas

VARIABLES, REGLAS = cargar_config()


def test_base_sintetica_limpia_sin_incidencias():
    df = generar_personas()
    df_limpio, incidencias = ejecutar_dataguard(df, VARIABLES, REGLAS)
    assert incidencias == []
    assert len(df_limpio) == len(df)


def test_validar_estructura_reporta_faltantes():
    df = generar_personas(50).drop(columns=["FACTOR", "PEA"])
    assert validar_estructura(df, ["FACTOR", "PEA", "PET"]) == ["FACTOR", "PEA"]


def test_validar_ponderador_nulos_ceros_negativos():
    df = generar_personas(50)
    df.loc[0, "FACTOR"] = np.nan
    df.loc[1:2, "FACTOR"] = 0
    df.loc[3, "FACTOR"] = -5
    incidencias = " ".join(validar_ponderador(df, "FACTOR"))
    assert "1 valores nulos" in incidencias
    assert "2 valores en cero" in incidencias
    assert "1 valores negativos" in incidencias


def test_codigo_99_se_convierte_a_nan_y_se_reporta_sin_tocar_original():
    df = generar_personas(100)
    df.loc[:4, "P02A02"] = 99
    mascara = detectar_codigos_especiales(df, "P02A02", REGLAS["codigos_especiales"])
    assert mascara.sum() == 5

    df_limpio, incidencias = ejecutar_dataguard(df, VARIABLES, REGLAS)
    assert df_limpio["P02A02"].isna().sum() == 5
    assert (df["P02A02"] == 99).sum() == 5
    assert any("5 códigos especiales" in i for i in incidencias)
    assert len(df_limpio) == len(df)


def test_codigo_99_no_se_limpia_en_ingreso():
    df = generar_personas(100)
    fila = df.index[df["OCUPADOS"] == 1][0]
    df.loc[fila, "YLAB_PUBLI"] = 99
    df_limpio, _ = ejecutar_dataguard(df, VARIABLES, REGLAS)
    assert df_limpio.loc[fila, "YLAB_PUBLI"] == 99


def test_rango_invalido_se_reporta():
    df = generar_personas(100)
    df.loc[0, "DOMINIO"] = 7
    _, incidencias = ejecutar_dataguard(df, VARIABLES, REGLAS)
    assert any("'DOMINIO': 1 valores fuera del rango" in i for i in incidencias)


def test_flags_codificacion_y_consistencia():
    df = generar_personas(200)
    no_pet = df.index[df["PET"].isna()][0]
    df.loc[no_pet, "PEA"] = 1                      # PEA fuera de PET
    df.loc[df.index[df["PEA"].isna()][0], "INACTIVOS"] = 0   # 0 en vez de NaN
    pea = df.index[df["PEA"] == 1][0]
    df.loc[pea, "INACTIVOS"] = 1                    # PEA e INACTIVOS a la vez
    incidencias = " ".join(validar_flags(df, REGLAS["variables_flag"]))
    assert "Flag 'INACTIVOS': 1 valores distintos de 1/NaN" in incidencias
    assert "'PEA': 1 casos marcados sin pertenecer a 'PET'" in incidencias
    assert "'PEA' y 'INACTIVOS'" in incidencias
