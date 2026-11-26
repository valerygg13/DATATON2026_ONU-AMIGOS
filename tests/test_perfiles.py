import pytest
from src.config import cargar_config
from src.sintetico import generar_personas
from src.fuentes import preparar_archivo
from src.pipeline import BaseNoValida

@pytest.mark.parametrize('anio,trimestre,edicion', [(2025,2,'I 2025'),(2026,6,'I 2026')])
def test_perfiles(anio,trimestre,edicion):
    df = generar_personas(100)
    df['ANIO'],df['TRIMESTRE'] = anio,trimestre
    v,r = cargar_config()
    base,inc,cfg,p = preparar_archivo('x.csv',df.to_csv(index=False).encode(),v,r,multiperiodo=True)
    assert len(base)==100 and not inc
    assert cfg['fuente']['edicion']==edicion==p['edicion']
    assert v['fuente']['edicion']=='I 2026'

@pytest.mark.parametrize('caso',['fraccionario','mezclado','nulo','ausente','infinito'])
def test_periodos_invalidos(caso):
    df=generar_personas(100)
    df['ANIO'],df['TRIMESTRE']=2026,6
    if caso=='fraccionario': df['TRIMESTRE']=1.5
    elif caso=='infinito': df['TRIMESTRE']=float('inf')
    elif caso=='mezclado': df.loc[0,'TRIMESTRE']=2
    elif caso=='nulo': df.loc[0,'TRIMESTRE']=float('nan')
    else: df=df.drop(columns=['ANIO'])
    with pytest.raises(BaseNoValida):
        preparar_archivo('x.csv',df.to_csv(index=False).encode(),*cargar_config(),multiperiodo=True)

@pytest.mark.parametrize('anio,trimestre', [(2024,1),(2027,99),(2030,18)])
def test_nueva_edicion(anio,trimestre):
    df = generar_personas(100)
    df['ANIO'], df['TRIMESTRE'] = anio,trimestre
    v,r = cargar_config()
    base,inc,cfg,p = preparar_archivo('x.csv',df.to_csv(index=False).encode(),v,r,multiperiodo=True)
    assert len(base)==100 and not inc
    assert p['estado']=='experimental_automatico'
    assert p['periodo']=={'ANIO':anio,'TRIMESTRE':trimestre}
    assert not p['referencia_participacion']
    assert v['fuente']['edicion']=='I 2026'

@pytest.mark.parametrize('columna,valor', [('FACTOR',-1),('P02A02',1.5),('PEA',2)])
def test_nueva_edicion_incompatible(columna,valor):
    df = generar_personas(100)
    df['ANIO'], df['TRIMESTRE'] = 2027,9
    df[columna] = df[columna].astype(float)
    df.loc[0,columna] = valor
    with pytest.raises(BaseNoValida):
        preparar_archivo('x.csv',df.to_csv(index=False).encode(),*cargar_config(),multiperiodo=True)
