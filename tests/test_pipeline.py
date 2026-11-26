import numpy as np
import pytest

from src.config import cargar_config
from src.pipeline import BaseNoValida, preparar_base, ejecutar_pipeline
from src.sintetico import generar_personas
from src.statshield.guardrails import DesagregacionNoAutorizada

V, R = cargar_config()


def test_pipeline_participacion():
    df, incidencias = preparar_base(generar_personas(), V, R)
    resultado, by = ejecutar_pipeline(df, 'participacion', ['sexo'], V, R)
    assert not incidencias
    assert by == ['sexo']
    assert len(resultado) == 2
    assert resultado['valor'].between(0, 1).all()
    assert 'advertencia' in resultado


@pytest.mark.parametrize('valor', [0, -1, np.nan, np.inf])
def test_pipeline_bloquea_ponderador(valor):
    df = generar_personas()
    df.loc[0, 'FACTOR'] = valor
    with pytest.raises(BaseNoValida, match='ponderadores'):
        preparar_base(df, V, R)


def test_pipeline_bloquea_columna_ausente():
    with pytest.raises(BaseNoValida, match='PEA'):
        preparar_base(generar_personas().drop(columns='PEA'), V, R)


def test_pipeline_bloquea_municipio():
    df, _ = preparar_base(generar_personas(), V, R)
    with pytest.raises(DesagregacionNoAutorizada):
        ejecutar_pipeline(df, 'participacion', ['municipio'], V, R)


def test_pipeline_bloquea_filtro_municipal():
    df, _ = preparar_base(generar_personas(), V, R)
    with pytest.raises(DesagregacionNoAutorizada):
        ejecutar_pipeline(df, 'ingreso', [], V, R, {'municipio': ['Mixco']})


def test_pipeline_brecha_sin_un_grupo():
    df, _ = preparar_base(generar_personas(), V, R)
    r, _ = ejecutar_pipeline(df, 'brecha', ['sexo'], V, R, {'sexo': ['Hombre']})
    assert r['n_no_ponderado'].eq(0).all()
    assert r[['valor', 'media_hombres', 'media_mujeres']].isna().all().all()


def test_pipeline_rechaza_indicador_desconocido():
    df, _ = preparar_base(generar_personas(), V, R)
    with pytest.raises(ValueError, match='Indicador no autorizado'):
        ejecutar_pipeline(df, 'otro', [], V, R)
