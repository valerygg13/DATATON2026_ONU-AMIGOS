import pytest
from src.config import cargar_config
from src.sintetico import generar_personas
from src.fuentes import preparar_archivo, huella
from src.pipeline import BaseNoValida

@pytest.fixture
def cfg():
    return cargar_config()

def test_csv(cfg):
    df = generar_personas(100)
    preparado, incidencias = preparar_archivo('personas.csv', df.to_csv(index=False).encode(), *cfg)
    assert len(preparado) == 100 and not incidencias
    assert 'sexo' in preparado

@pytest.mark.parametrize('nombre,contenido', [('x.exe',b'a'),('x.csv',b''),('x.csv',b'a,b\n1,2')])
def test_rechazos(cfg,nombre,contenido):
    with pytest.raises(BaseNoValida):
        preparar_archivo(nombre,contenido,*cfg)

def test_factor(cfg):
    df = generar_personas(100)
    df.loc[0,'FACTOR'] = -1
    with pytest.raises(BaseNoValida):
        preparar_archivo('x.csv',df.to_csv(index=False).encode(),*cfg)

def test_edicion(cfg):
    df = generar_personas(100)
    df['ANIO'] = 2025
    with pytest.raises(BaseNoValida):
        preparar_archivo('x.csv',df.to_csv(index=False).encode(),*cfg)

def test_huella():
    assert huella(b'a') != huella(b'b')

def test_excel(cfg):
    from io import BytesIO
    archivo = BytesIO()
    generar_personas(100).to_excel(archivo,index=False)
    preparado, incidencias = preparar_archivo('x.xlsx',archivo.getvalue(),*cfg)
    assert len(preparado) == 100 and not incidencias

def test_periodo_real_eneic_2026(cfg):
    df = generar_personas(100)
    df['ANIO'] = 2026
    df['TRIMESTRE'] = 6

    preparado, incidencias = preparar_archivo(
        'personas.csv',
        df.to_csv(index=False).encode(),
        *cfg
    )

    assert len(preparado) == 100
    assert not incidencias


def test_trimestre_incorrecto(cfg):
    df = generar_personas(100)
    df['ANIO'] = 2026
    df['TRIMESTRE'] = 1

    with pytest.raises(BaseNoValida, match='TRIMESTRE'):
        preparar_archivo(
            'personas.csv',
            df.to_csv(index=False).encode(),
            *cfg
        )


def test_periodos_mezclados(cfg):
    df = generar_personas(100)
    df['ANIO'] = 2026
    df['TRIMESTRE'] = 6
    df.loc[0, 'TRIMESTRE'] = 5

    with pytest.raises(BaseNoValida, match='TRIMESTRE'):
        preparar_archivo(
            'personas.csv',
            df.to_csv(index=False).encode(),
            *cfg
        )


def test_periodo_nulo(cfg):
    df = generar_personas(100)
    df['ANIO'] = 2026
    df['TRIMESTRE'] = 6
    df.loc[0, 'TRIMESTRE'] = float('nan')

    with pytest.raises(BaseNoValida, match='TRIMESTRE'):
        preparar_archivo(
            'personas.csv',
            df.to_csv(index=False).encode(),
            *cfg
        )