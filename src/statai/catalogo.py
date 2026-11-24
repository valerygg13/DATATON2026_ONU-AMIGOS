"""StatAI (opcional): interpreta preguntas en lenguaje natural contra un catálogo cerrado
de consultas permitidas (NO cálculo libre, NO envío de microdatos a servicios externos).

El motor debe seguir funcionando por completo sin este módulo.
"""

from __future__ import annotations

CONSULTAS_PERMITIDAS = [
    # Cada entrada mapea una intención a una llamada concreta de statengine.indicadores.
    # Ejemplo: {"id": "participacion_por_sexo", "descripcion": "...", "funcion": "participacion_laboral", "by": ["sexo"]}
]


def interpretar_pregunta(pregunta: str) -> str | None:
    """Devuelve el id de consulta del catálogo que mejor matchea `pregunta`, o None si ninguna aplica."""
    raise NotImplementedError
