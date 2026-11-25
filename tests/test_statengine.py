import numpy as np
import pandas as pd
import pytest

from src.config import cargar_config
from src.statengine.indicadores import (
    agregar_dimensiones,
    brecha_relativa_ingreso,
    ingreso_laboral_medio,
    participacion_laboral,
)

VARIABLES, _ = cargar_config()
NAN = np.nan


@pytest.fixture
def mini():
    """Base mínima calculable a mano (flags 1/NaN como en ENEIC)."""
    df = pd.DataFrame(
        {
            "P02A02":     [1,   1,   1,   2,   2,   2,   2],
            "DOMINIO":    [1,   1,   3,   1,   3,   3,   3],
            "P00A10":     [1,   1,   2,   1,   2,   2,   2],
            "FACTOR":     [100, 300, 200, 100, 100, 200, 50],
            "PET":        [1,   1,   1,   1,   1,   1,   NAN],
            "PEA":        [1,   1,   NAN, 1,   NAN, 1,   NAN],
            "OCUPADOS":   [1,   1,   NAN, 1,   NAN, 1,   NAN],
            "YLAB_PUBLI": [1000, 3000, NAN, 2000, NAN, NAN, NAN],
        }
    )
    return agregar_dimensiones(df, VARIABLES)


def test_agregar_dimensiones_etiqueta(mini):
    assert list(mini["sexo"].unique()) == ["Hombre", "Mujer"]
    assert set(mini["dominio"]) == {"Urbano Metropolitano", "Rural Nacional"}


def test_participacion_total_ponderada(mini):
    r = participacion_laboral(mini, "FACTOR")
    # PEA: 100+300+100+200 = 700; PET: 100+300+200+100+100+200 = 1000
    assert r.loc[0, "valor"] == pytest.approx(0.7)
    assert r.loc[0, "n_no_ponderado"] == 6


def test_participacion_por_sexo(mini):
    r = participacion_laboral(mini, "FACTOR", ["sexo"]).set_index("sexo")
    assert r.loc["Hombre", "valor"] == pytest.approx(400 / 600)
    assert r.loc["Mujer", "valor"] == pytest.approx(300 / 400)
    assert r.loc["Mujer", "n_no_ponderado"] == 3  # la fila fuera de PET no cuenta
    assert list(r.columns) == ["valor", "n_no_ponderado"]


def test_ingreso_excluye_faltantes_no_imputa_cero(mini):
    r = ingreso_laboral_medio(mini, "FACTOR", ["sexo"]).set_index("sexo")
    assert r.loc["Hombre", "valor"] == pytest.approx((100 * 1000 + 300 * 3000) / 400)
    # Mujer ocupada sin ingreso (NaN) queda fuera: media = 2000, no 2000*100/300
    assert r.loc["Mujer", "valor"] == pytest.approx(2000)
    assert r.loc["Mujer", "n_no_ponderado"] == 1


def test_ingreso_excluir_ceros(mini):
    mini.loc[0, "YLAB_PUBLI"] = 0
    con_ceros = ingreso_laboral_medio(mini, "FACTOR", ["sexo"]).set_index("sexo")
    sin_ceros = ingreso_laboral_medio(mini, "FACTOR", ["sexo"], excluir_ceros=True).set_index("sexo")
    assert con_ceros.loc["Hombre", "valor"] == pytest.approx(300 * 3000 / 400)
    assert sin_ceros.loc["Hombre", "valor"] == pytest.approx(3000)


def test_brecha_por_sexo(mini):
    ingreso = ingreso_laboral_medio(mini, "FACTOR", ["sexo"])
    b = brecha_relativa_ingreso(ingreso)
    assert len(b) == 1
    assert b.loc[0, "valor"] == pytest.approx((2500 - 2000) / 2500 * 100)
    assert b.loc[0, "n_no_ponderado"] == 1  # el menor de los dos grupos


def test_brecha_por_sexo_y_dominio(mini):
    ingreso = ingreso_laboral_medio(mini, "FACTOR", ["sexo", "dominio"])
    b = brecha_relativa_ingreso(ingreso).set_index("dominio")
    assert b.loc["Urbano Metropolitano", "valor"] == pytest.approx(20.0)
    # En Rural Nacional ningún hombre tiene ingreso: no hay brecha calculable
    assert "Rural Nacional" not in b.index or np.isnan(b.loc["Rural Nacional", "valor"])


def test_brecha_media_masculina_cero_no_se_calcula():
    ingreso = pd.DataFrame({"sexo": ["Hombre", "Mujer"], "valor": [0.0, 1500.0], "n_no_ponderado": [40, 40]})
    assert np.isnan(brecha_relativa_ingreso(ingreso).loc[0, "valor"])


def test_brecha_requiere_sexo():
    with pytest.raises(ValueError):
        brecha_relativa_ingreso(pd.DataFrame({"valor": [1.0], "n_no_ponderado": [1]}))
