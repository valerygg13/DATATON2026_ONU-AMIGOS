
"""Reconocimiento controlado de variantes lingüísticas en español."""
import re

PATRONES = {
    'participacion_mujeres': [
        r'(?:cual es |cuanto es )?(?:la )?(?:tasa de )?participacion laboral (?:de la mujer|de las mujeres|femenina)(?: en guatemala)?',

        r'que porcentaje de (?:las )?mujeres participa[n]? en el mercado laboral(?: en guatemala)?',

        r'cuantas de cada 100 mujeres participan en el mercado laboral',

        r'que porcentaje de mujeres tiene participacion laboral',
    ],

    'participacion_por_sexo': [
        r'(?:cual es )?(?:la )?(?:tasa de )?participacion laboral (?:por sexo|por genero|de hombres y mujeres)(?: en guatemala)?',

        r'que porcentaje de hombres y mujeres participa[n]? en el mercado laboral',

        r'compara la participacion laboral de hombres y mujeres',
    ],

    'participacion_dominio': [
        r'(?:cual es )?(?:la )?participacion laboral por (?:sexo|genero) y dominio',
        r'participacion laboral por dominio y sexo',
    ],

    'ingreso_por_sexo': [
        r'(?:cual es )?(?:el )?ingreso laboral (?:medio|promedio) (?:por sexo|por genero|de hombres y mujeres)(?: en guatemala)?',

        r'cuanto ganan en promedio los hombres y las mujeres',

        r'compara los ingresos laborales de hombres y mujeres',
    ],

    'brecha_total': [
        r'(?:cual es )?(?:la )?brecha (?:salarial|de ingresos|de ingresos laborales) entre hombres y mujeres(?: en guatemala)?',

        r'cual es la diferencia porcentual de ingresos entre hombres y mujeres',

        r'que porcentaje menos ganan las mujeres que los hombres',
    ],

    'brecha_dominio': [
        r'(?:cual es )?(?:la )?brecha (?:salarial|de ingresos) por dominio',
    ],

    'brecha_mayor': [
        r'en que dominio (?:hay|existe|se observa) (?:una |la )?mayor brecha (?:salarial|de ingresos)',

        r'que dominio tiene la mayor brecha de ingresos',
    ],
}


def interpretar_variantes(pregunta_normalizada):
    """Reconoce únicamente variantes completas y autorizadas."""
    coincidencias = set()

    for intencion, patrones in PATRONES.items():
        for patron in patrones:
            if re.fullmatch(patron, pregunta_normalizada):
                coincidencias.add(intencion)

    if len(coincidencias) == 1:
        return next(iter(coincidencias))

    return None

