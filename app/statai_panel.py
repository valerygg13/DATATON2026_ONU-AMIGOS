"""Panel opcional de consultas locales, separado del explorador manual."""
import streamlit as st
from src.statai.catalogo import CONSULTAS_PERMITIDAS, consultar
from src.statshield.guardrails import DesagregacionNoAutorizada


def mostrar_statai(df, variables, reglas, fuente, demo):
    with st.expander('StatAI — Consultas en lenguaje natural', expanded=False):
        st.caption('Catálogo cerrado de preguntas en español. No utiliza un LLM. Consulta la base seleccionada completa, sin los filtros del explorador manual.')
        st.caption('Datos sintéticos, no oficiales.' if demo else f'Archivo seleccionado: {fuente}. Verifique su edición y procedencia.')
        opciones = ['Escribir mi pregunta'] + [c['descripcion'] for c in CONSULTAS_PERMITIDAS] + ['¿Cuál es la brecha de ingresos por municipio?']
        ejemplo = st.selectbox('Pregunta de ejemplo', opciones, key='ai_ejemplo')
        pregunta = st.text_input('Escribe tu consulta', key='ai_pregunta') if ejemplo == opciones[0] else ejemplo
        if not pregunta.strip():
            return
        try:
            salida = consultar(pregunta, df, variables, reglas)
        except DesagregacionNoAutorizada as e:
            st.error(f'Consulta bloqueada: {e}')
            return
        if salida is None:
            st.warning('Pregunta fuera del catálogo. Selecciona un ejemplo o utiliza el explorador manual.')
            return
        c, r, by = salida
        st.write(c['descripcion'])
        tabla = r.copy()
        if c['indicador'] == 'participacion':
            tabla['valor'] *= 100
        unidad = 'Q' if c['indicador'] == 'ingreso' else '%'
        st.dataframe(tabla.rename(columns={'valor': f'Resultado ({unidad})'}), hide_index=True)
        validos = tabla.dropna(subset=['valor'])
        if validos.empty:
            st.warning('No existe resultado calculable o publicable.')
        elif c.get('mayor'):
            maximo = validos['valor'].max()
            grupos = ', '.join(validos.loc[validos['valor'].eq(maximo), 'dominio'].astype(str))
            st.write(f'Mayor brecha entre los dominios con valor disponible: {grupos}, {maximo:.2f}%.')
        elif len(validos) == 1:
            st.metric('Resultado', f"{validos.iloc[0]['valor']:.2f} {unidad}")
        if c['indicador'] == 'brecha':
            st.info('Brecha descriptiva; no demuestra causalidad ni discriminación por sí sola.')
        st.caption('Precisión muestral no evaluada. Consulte las advertencias de la tabla.')
