"""Identificación estricta de períodos, sin inferir procedencia oficial."""
from copy import deepcopy
import pandas as pd
import math
from src.config import cargar_yaml
from src.pipeline import BaseNoValida


def detectar_perfil(df, variables):
    if df.empty:
        raise BaseNoValida('La base no contiene registros.')
    periodo = {}
    for c in ('ANIO', 'TRIMESTRE'):
        if c not in df:
            raise BaseNoValida(f'Falta el metadato {c}.')
        s = pd.to_numeric(df[c], errors='coerce')
        if s.isna().any() or s.nunique() != 1:
            raise BaseNoValida(f'{c}: valores faltantes, inválidos o períodos mezclados.')
        valor = float(s.iloc[0])
        if not math.isfinite(valor) or not valor.is_integer() or valor <= 0:
            raise BaseNoValida(f'{c}: se requiere un entero positivo.')
        if c == 'ANIO' and not 1900 <= valor <= 9999:
            raise BaseNoValida('ANIO: año fuera del rango admitido.')
        periodo[c] = int(valor)
    for clave, perfil in cargar_yaml('perfiles.yaml')['perfiles'].items():
        if periodo == perfil['periodo']:
            cfg = deepcopy(variables)
            cfg['fuente'].update(edicion=perfil['edicion'], periodo=perfil['periodo'], perfil=clave,
                                 estado=perfil['estado'])
            cfg['fuente'].pop('fecha_descarga', None)
            return cfg, perfil
    # Un código interno no equivale necesariamente a un trimestre calendario.
    perfil = {
        'edicion': f"{periodo['ANIO']} · código de período {periodo['TRIMESTRE']}",
        'periodo': periodo,
        'estado': 'experimental_automatico',
        'referencia_participacion': {},
        'decimales_referencia': None,
    }
    cfg = deepcopy(variables)
    cfg['fuente'].update(edicion=perfil['edicion'], periodo=periodo,
                         perfil=f"auto_{periodo['ANIO']}_{periodo['TRIMESTRE']}",
                         estado=perfil['estado'])
    cfg['fuente'].pop('fecha_descarga', None)
    return cfg, perfil
