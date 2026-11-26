"""Asistente local de consultas cerradas. No usa LLM ni ejecuta código del usuario."""
from __future__ import annotations
import re
import unicodedata
from src.pipeline import ejecutar_pipeline


def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto.casefold())
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[a-z0-9]+', texto))


CONSULTAS_PERMITIDAS = [
    dict(id='participacion_por_sexo', descripcion='¿Cuál es la participación laboral por sexo?', indicador='participacion', by=['sexo'], filtros={}, alias=['participación laboral por sexo', 'participación laboral de hombres y mujeres']),
    dict(id='participacion_mujeres', descripcion='¿Cuál es la participación laboral de las mujeres?', indicador='participacion', by=['sexo'], filtros={'sexo':['Mujer']}, alias=['participación laboral femenina', 'participación laboral de las mujeres']),
    dict(id='participacion_dominio', descripcion='¿Cuál es la participación laboral por sexo y dominio?', indicador='participacion', by=['sexo','dominio'], filtros={}, alias=['participación laboral por sexo y dominio']),
    dict(id='ingreso_por_sexo', descripcion='¿Cuál es el ingreso laboral medio por sexo?', indicador='ingreso', by=['sexo'], filtros={}, alias=['ingreso laboral medio por sexo', 'ingresos de hombres y mujeres']),
    dict(id='brecha_total', descripcion='¿Cuál es la brecha de ingresos entre hombres y mujeres?', indicador='brecha', by=[], filtros={}, alias=['brecha de ingresos', 'brecha de ingresos entre hombres y mujeres']),
    dict(id='brecha_dominio', descripcion='¿Cuál es la brecha de ingresos por dominio?', indicador='brecha', by=['dominio'], filtros={}, alias=['brecha de ingresos por dominio']),
    dict(id='brecha_mayor', descripcion='¿En qué dominio existe una mayor brecha de ingresos?', indicador='brecha', by=['dominio'], filtros={}, alias=['mayor brecha de ingresos por dominio','en qué dominio existe una mayor brecha de ingresos entre hombres y mujeres'], mayor=True),
]

# Solicitudes explícitas no autorizadas: se pasan al mismo guardrail, nunca se calculan.
BLOQUEADAS = [dict(id='bloqueada_'+dim, descripcion=f'¿Cuál es la brecha de ingresos por {dim}?', indicador='brecha', by=[dim], filtros={}, alias=[f'brecha de ingresos por {dim}']) for dim in ('municipio','departamento')]


def interpretar_pregunta(pregunta: str) -> str | None:
    """Solo acepta frases y variantes explícitas; no aproxima consultas ambiguas."""
    q = normalizar(pregunta)
    for c in CONSULTAS_PERMITIDAS + BLOQUEADAS:
        if q in {normalizar(t) for t in [c['descripcion'], *c['alias']]}:
            return c['id']
    return None


def consultar(pregunta, df, variables, reglas):
    """Devuelve consulta, resultado y dimensiones; None si no reconoce la pregunta."""
    id_consulta = interpretar_pregunta(pregunta)
    if id_consulta is None:
        return None
    c = next(c for c in CONSULTAS_PERMITIDAS + BLOQUEADAS if c['id'] == id_consulta)
    # Las consultas de demostración bloqueadas no pueden volverse autorizadas por accidente.
    if c in BLOQUEADAS:
        from src.statshield.guardrails import DesagregacionNoAutorizada
        raise DesagregacionNoAutorizada(f"StatAI no admite desagregación por {c['by'][0]}. Revise las dimensiones autorizadas.")
    r, by = ejecutar_pipeline(df, c['indicador'], c['by'], variables, reglas, c['filtros'])
    return c, r, by
