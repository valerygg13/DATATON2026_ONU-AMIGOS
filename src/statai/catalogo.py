"""Asistente local de consultas cerradas. No usa LLM ni ejecuta código del usuario."""
from __future__ import annotations
import re
import unicodedata
from src.pipeline import ejecutar_pipeline
from src.statai.interprete import interpretar_variantes
from src.statai.dinamico import resolver_dinamica, aplicar_direccion


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


def resolver_consulta(pregunta):
    q = normalizar(pregunta)
    for c in CONSULTAS_PERMITIDAS + BLOQUEADAS:
        if q in {normalizar(t) for t in [c['descripcion'], *c['alias']]}:
            return c
    intencion = interpretar_variantes(q)
    for c in CONSULTAS_PERMITIDAS:
        if c['id'] == intencion:
            return c
    return resolver_dinamica(q)


def interpretar_pregunta(pregunta: str) -> str | None:
    c = resolver_consulta(pregunta)
    return c['id'] if c else None


def consultar(pregunta, df, variables, reglas):
    c = resolver_consulta(pregunta)
    if c is None:
        return None
    # Las consultas de demostración bloqueadas no pueden volverse autorizadas por accidente.
    if c in BLOQUEADAS:
        from src.statshield.guardrails import DesagregacionNoAutorizada
        raise DesagregacionNoAutorizada(f"StatAI no admite desagregación por {c['by'][0]}. Revise las dimensiones autorizadas.")
    r, by = ejecutar_pipeline(df, c['indicador'], c['by'], variables, reglas, c['filtros'])
    if c.get("direccion"):
        r = aplicar_direccion(r, c["direccion"])
    return c, r, by
