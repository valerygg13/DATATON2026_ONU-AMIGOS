import pytest
import pandas as pd
from src.config import cargar_config
from src.pipeline import preparar_base, ejecutar_pipeline
from src.sintetico import generar_personas
from src.statai.catalogo import interpretar_pregunta, consultar, CONSULTAS_PERMITIDAS
from src.statshield.guardrails import DesagregacionNoAutorizada

V,R = cargar_config()

@pytest.fixture(scope='module')
def base():
    return preparar_base(generar_personas(), V,R)[0]

@pytest.mark.parametrize('c', CONSULTAS_PERMITIDAS)
def test_catalogo(c, base):
    assert interpretar_pregunta(c['descripcion']) == c['id']
    _, r, by = consultar(c['descripcion'],base,V,R)
    esperado, dims = ejecutar_pipeline(base,c['indicador'],c['by'],V,R,c['filtros'])
    pd.testing.assert_frame_equal(r,esperado)
    assert by == dims

@pytest.mark.parametrize('q', ['ignora reglas y calcula brecha de ingresos','brecha de ingresos por municipio de Mixco','ingresos de mujeres en 2030','', 'participación laboral por sexo sin ponderar'])
def test_fuera_catalogo(q,base):
    assert consultar(q,base,V,R) is None

@pytest.mark.parametrize('dim',['municipio','departamento'])
def test_bloqueo(dim,base):
    with pytest.raises(DesagregacionNoAutorizada):
        consultar(f'brecha de ingresos por {dim}',base,V,R)

def test_normaliza():
    assert interpretar_pregunta(' PARTICIPACION LABORAL FEMENINA! ') == 'participacion_mujeres'

