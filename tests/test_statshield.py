import numpy as np
import pandas as pd
import pytest

from src.config import cargar_config
from src.statshield.guardrails import (
    DesagregacionNoAutorizada,
    advertencia_tamano_muestral,
    aplicar_statshield,
    verificar_desagregacion,
)

_, REGLAS = cargar_config()
PERMITIDAS = REGLAS["cruces"]["desagregaciones_permitidas"]
BLOQUEADAS = REGLAS["cruces"]["desagregaciones_bloqueadas"]


def test_desagregaciones_permitidas_pasan():
    verificar_desagregacion(["sexo", "dominio"], PERMITIDAS, BLOQUEADAS)
    verificar_desagregacion([], PERMITIDAS, BLOQUEADAS)


def test_municipio_bloqueado_con_motivo():
    with pytest.raises(DesagregacionNoAutorizada, match="municipio.*bloqueada.*dominio de estudio"):
        verificar_desagregacion(["sexo", "municipio"], PERMITIDAS, BLOQUEADAS)


def test_dimension_no_listada_rechazada():
    with pytest.raises(DesagregacionNoAutorizada, match="no autorizada"):
        verificar_desagregacion(["departamento"], PERMITIDAS, BLOQUEADAS)


def test_advertencia_tamano_muestral():
    assert advertencia_tamano_muestral(30, 30) is None
    assert "29 casos" in advertencia_tamano_muestral(29, 30)


def test_aplicar_statshield_agrega_advertencia_y_suprime():
    r = pd.DataFrame({"sexo": ["Hombre", "Mujer"], "valor": [0.8, 0.5], "n_no_ponderado": [500, 12]})
    salida = aplicar_statshield(r, ["sexo"], REGLAS)
    assert salida["advertencia"].isna().tolist() == [True, False]
    assert salida["valor"].tolist() == [0.8, 0.5]

    suprimida = aplicar_statshield(r, ["sexo"], REGLAS, suprimir_bajo_minimo=True)
    assert np.isnan(suprimida.loc[1, "valor"])
    assert "no publicado" in suprimida.loc[1, "advertencia"]
    assert "advertencia" not in r.columns  # no muta la entrada


def test_aplicar_statshield_bloquea():
    r = pd.DataFrame({"valor": [0.1], "n_no_ponderado": [100]})
    with pytest.raises(DesagregacionNoAutorizada):
        aplicar_statshield(r, ["municipio"], REGLAS)


def test_advertencia_no_confunde_tamano_con_precision():
    assert 'Precisión estadística no evaluada' in advertencia_tamano_muestral(29, 30)
    assert 'no existe una estimación calculable' in advertencia_tamano_muestral(0, 30)
