import pytest
import pandas as pd
from src.statai.dinamico import resolver_dinamica, aplicar_direccion
from src.statai.catalogo import normalizar

@pytest.mark.parametrize('q,indicador,filtros',[
 ('¿Qué porcentaje de hombres participa en el mercado laboral?','participacion',{'sexo':['Hombre']}),
 ('¿Cuál es la participación laboral masculina?','participacion',{'sexo':['Hombre']}),
 ('¿Cuánto ganan las mujeres del área rural?','ingreso',{'sexo':['Mujer'],'area':['Rural']}),
 ('¿Cuánto ganan los hombres del área urbana?','ingreso',{'sexo':['Hombre'],'area':['Urbana']}),
 ('¿Cuál es la participación laboral femenina en el área rural?','participacion',{'sexo':['Mujer'],'area':['Rural']}),
 ('¿Cuál es la brecha de ingresos en el área urbana?','brecha',{'area':['Urbana']}),
 ('¿Cuál es la participación laboral nacional?','participacion',{}),
 ('¿Cuánto ganan las mujeres del dominio resto urbano?','ingreso',{'sexo':['Mujer'],'dominio':['Resto Urbano']}),
])
def test_dinamica(q,indicador,filtros):
    c=resolver_dinamica(normalizar(q)); assert c['indicador']==indicador; assert c['filtros']==filtros

@pytest.mark.parametrize('q',['cuanto ganan mujeres indigenas','participacion laboral masculina en mixco','cuanto ganaran los hombres en 2030','por que ganan menos las mujeres','participacion laboral masculina sin ponderar','cuanto ganan mujeres menores de 25 años'])
def test_rechazo(q):
    assert resolver_dinamica(normalizar(q)) is None

@pytest.mark.parametrize('direccion,esperado',[(('Mujer','Hombre','mas'),-25),(('Hombre','Mujer','mas'),100/3),(('Mujer','Hombre','menos'),25)])
def test_direccion(direccion,esperado):
    r=pd.DataFrame({'valor':[25.,None,25.],'media_hombres':[100.,100.,100.],'media_mujeres':[75.,75.,0.]})
    out=aplicar_direccion(r,direccion)
    assert out.valor.iloc[0]==pytest.approx(esperado)
    assert pd.isna(out.valor.iloc[1])
    if direccion[1]=='Mujer': assert pd.isna(out.valor.iloc[2])

@pytest.mark.parametrize('q',['participacion laboral masculina en el dominio rural','ingreso laboral medio de mujeres en el area resto urbano','participacion laboral nacional en el area rural'])
def test_no_confunde_geografia(q):
    assert resolver_dinamica(normalizar(q)) is None


def test_integracion_pipeline():
    from src.config import cargar_config
    from src.pipeline import preparar_base, ejecutar_pipeline
    from src.sintetico import generar_personas
    from src.statai.catalogo import consultar
    v,reglas=cargar_config()
    df,_=preparar_base(generar_personas(),v,reglas)
    c,r,by=consultar('cuanto ganan las mujeres del area rural',df,v,reglas)
    esperado,dims=ejecutar_pipeline(df,'ingreso',['sexo'],v,reglas,{'sexo':['Mujer'],'area':['Rural']})
    pd.testing.assert_frame_equal(r,esperado)
    assert by==dims
