"""Integración de DataGuard, StatEngine y StatShield, independiente de la UI."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.dataguard.validators import ejecutar_dataguard
from src.statengine.indicadores import (
    agregar_dimensiones, participacion_laboral, ingreso_laboral_medio,
    brecha_relativa_ingreso,
)
from src.statshield.guardrails import aplicar_statshield, verificar_desagregacion


class BaseNoValida(ValueError):
    """La base no reúne las condiciones mínimas para calcular indicadores."""


def preparar_base(df, variables, reglas):
    limpio, incidencias = ejecutar_dataguard(df, variables, reglas)
    m = variables['base_personas']
    requeridas = [m[k] for k in ('ponderador', 'sexo', 'dominio', 'area',
                                  'pet', 'pea', 'ocupados', 'ingreso_laboral')]
    faltantes = [c for c in requeridas if c not in limpio.columns]
    if faltantes:
        raise BaseNoValida('Faltan variables indispensables: ' + ', '.join(faltantes))
    factor = pd.to_numeric(limpio[m['ponderador']], errors='coerce')
    if (factor.isna() | ~np.isfinite(factor) | (factor <= 0)).any():
        raise BaseNoValida('Existen ponderadores inválidos. Revise la base antes de calcular.')
    limpio[m['ponderador']] = factor
    return agregar_dimensiones(limpio, variables), incidencias


def ejecutar_pipeline(df, indicador, by, variables, reglas, filtros=None):
    """Recibe una base preparada; devuelve (resultado, dimensiones efectivas)."""
    by = list(by or [])
    filtros = filtros or {}
    cruces = reglas['cruces']
    verificar_desagregacion(by + list(filtros), cruces['desagregaciones_permitidas'],
                            cruces['desagregaciones_bloqueadas'])
    if len(set(by)) != len(by):
        raise ValueError('Las dimensiones no deben repetirse.')
    m = variables['base_personas']
    datos = df
    for dim, valores in filtros.items():
        datos = datos[datos[dim].isin(valores)]
    if indicador == 'participacion':
        r = participacion_laboral(datos, m['ponderador'], by, pet=m['pet'], pea=m['pea'])
    elif indicador in ('ingreso', 'brecha'):
        if indicador == 'brecha':
            by = [d for d in by if d != 'sexo']
            dimensiones = ['sexo'] + by
        else:
            dimensiones = by
        r = ingreso_laboral_medio(datos, m['ponderador'], dimensiones,
                                  ingreso=m['ingreso_laboral'], ocupados=m['ocupados'])
        if indicador == 'brecha':
            r = brecha_relativa_ingreso(r)
            r['n_no_ponderado'] = r[['n_hombres', 'n_mujeres']].min(axis=1)
    else:
        raise ValueError(f'Indicador no autorizado: {indicador}')
    r = aplicar_statshield(r, by, reglas, suprimir_bajo_minimo=indicador == 'brecha')
    if indicador == 'brecha':
        bajo = r['n_no_ponderado'] < cruces['minimo_casos_no_ponderados']
        r.loc[bajo, ['media_hombres', 'media_mujeres']] = np.nan
    return r, by
