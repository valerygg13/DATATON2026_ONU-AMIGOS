import json
import pandas as pd
from src.statpassport import crear_pasaporte, exportar_csv, exportar_ficha

def ficha(tabla, demo=False, estado='activo'):
    return crear_pasaporte(tabla,'participacion','Participación laboral','base.sav',{'estado':estado,'edicion':'I 2026','periodo':{'ANIO':2026,'TRIMESTRE':6}}, {'base_personas':{'ponderador':'FACTOR'}}, {}, {'sexo':['Mujer']}, ['sexo'], ['sexo'], [], demo, 'abc')

def test_resultado_y_filtros():
    f=ficha(pd.DataFrame({'valor':[47.25]}))
    assert f['resultados'][0]['valor']==47.25 and f['filtros']=={'sexo':['Mujer']}

def test_demo():
    f=ficha(pd.DataFrame({'valor':[44.51]}), True)
    assert f['periodo'] is None and f['estado_perfil']=='sintetico'

def test_experimental():
    f=ficha(pd.DataFrame({'valor':[67.09]}), estado='experimental_automatico')
    assert any('no registrada' in x for x in f['limitaciones'])

def test_nulos():
    f=ficha(pd.DataFrame({'valor':[float('nan')]}))
    assert json.loads(exportar_ficha(f))['resultados'][0]['valor'] is None

def test_csv():
    from io import BytesIO
    t=pd.DataFrame({'valor':[47.25], 'advertencia':['=1+1']})
    r=pd.read_csv(BytesIO(exportar_csv(t,ficha(t))))
    assert r.loc[0,'valor']==47.25 and r.loc[0,'advertencia']=="'=1+1"
