"""Ficha y exportación de resultados agregados, sin microdatos."""
import json
from datetime import datetime, timezone

METODOS = {
    'participacion': ('Porcentaje', '100 × suma de pesos de PEA dentro de PET / suma de pesos de PET', 'Personas en edad de trabajar (PET).'),
    'ingreso': ('Quetzales mensuales', 'Suma de peso × ingreso / suma de pesos elegibles', 'Personas ocupadas con ingreso laboral no nulo; incluye ceros declarados.'),
    'brecha': ('Porcentaje', '100 × (media hombres − media mujeres) / media hombres', 'Personas ocupadas con ingreso no nulo; requiere ambos grupos y media masculina positiva.'),
}

def crear_pasaporte(tabla, indicador, nombre, fuente, perfil, variables, reglas, filtros, solicitado, efectivo, incidencias, demo=False, sha256=None):
    unidad, formula, universo = METODOS[indicador]
    estado = 'sintetico' if demo else perfil['estado']
    limites = ['Precisión muestral no evaluada: sin intervalos de confianza ni pruebas de significancia.', 'Resultados del prototipo; no son publicaciones oficiales del INE.', 'El umbral de casos es preventivo; no certifica precisión ni confidencialidad.']
    if demo:
        limites.append('Datos sintéticos; no representan a Guatemala.')
    else:
        limites.append('Procedencia del archivo no certificada.')
    if estado == 'experimental_automatico':
        limites.append('Edición no registrada: reglas de ENEIC I 2026 aplicadas bajo supuestos no validados; solo participación exploratoria.')
    elif estado == 'experimental':
        limites.append('Perfil experimental: ingresos y brechas requieren validación metodológica adicional.')
    if indicador == 'brecha':
        limites.append('Medida descriptiva, no causal; no controla por horas, ocupación ni escolaridad. Casos elegibles: tamaño del grupo menor.')
    return {
        'version_ficha': 1, 'generado_utc': datetime.now(timezone.utc).isoformat(),
        'indicador': nombre, 'unidad': unidad, 'formula': formula, 'universo': universo,
        'archivo': fuente, 'sha256_archivo': sha256, 'edicion': 'Demo sintético' if demo else perfil['edicion'],
        'periodo': None if demo else perfil['periodo'], 'estado_perfil': estado,
        'ponderador': variables['base_personas']['ponderador'], 'variables': variables['base_personas'],
        'reglas': reglas, 'filtros': {k:list(v) for k,v in filtros.items()},
        'desagregacion_solicitada': list(solicitado), 'desagregacion_efectiva': list(efectivo),
        'incidencias_base': [str(i) for i in incidencias], 'limitaciones': limites,
        'resultados': json.loads(tabla.to_json(orient='records', force_ascii=False, double_precision=15)),
    }

def exportar_csv(tabla, ficha):
    salida = tabla.copy()
    for campo in ('edicion','estado_perfil','indicador','unidad','archivo','sha256_archivo'):
        salida[campo] = ficha[campo]
    salida['filtros'] = json.dumps(ficha['filtros'], ensure_ascii=False, default=str)
    salida['limitaciones'] = ' | '.join(ficha['limitaciones'])
    # Evitar fórmulas ejecutables en hojas de cálculo (solo cadenas).
    for col in salida.columns:
        salida[col] = salida[col].map(lambda x: "'" + x if isinstance(x,str) and x.lstrip().startswith(('=','+','-','@')) else x)
    return salida.to_csv(index=False).encode('utf-8-sig')

def exportar_ficha(ficha):
    return json.dumps(ficha, ensure_ascii=False, indent=2, default=str, allow_nan=False).encode('utf-8')
