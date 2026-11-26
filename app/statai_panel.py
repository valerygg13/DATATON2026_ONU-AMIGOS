"""Vista de consultas controladas, sin servicios externos."""
import streamlit as st
from src.statai.catalogo import CONSULTAS_PERMITIDAS, consultar
from src.statshield.guardrails import DesagregacionNoAutorizada


def mostrar_statai(df, variables, reglas, fuente, demo):
    st.header('Pregúntale a los datos')
    st.caption('StatAI · Asistente estadístico')
    st.caption('Consultas en español mediante reconocimiento de intenciones y variantes lingüísticas controladas. No utiliza un LLM. Analiza la base completa, independientemente de los filtros del explorador.')
    st.caption('Datos sintéticos, no oficiales.' if demo else f'Archivo: {fuente}. Verifica su edición y procedencia.')
    with st.chat_message('assistant'):
        st.write('Hola. Puedo ayudarte a consultar participación laboral, ingresos y brechas entre hombres y mujeres.')
    opciones = ['Escribir mi pregunta'] + [c['descripcion'] for c in CONSULTAS_PERMITIDAS] + ['¿Cuál es la brecha de ingresos por municipio?', '¿Cuál es la brecha de ingresos por departamento?']
    with st.form('consulta_statai'):
        ejemplo = st.selectbox('Pregunta de ejemplo', opciones, key='ai_ejemplo')
        texto = st.text_input('O escribe una pregunta', key='ai_pregunta', placeholder='¿Cuál es la participación laboral de las mujeres?')
        enviado = st.form_submit_button('Consultar StatAI', type='primary', use_container_width=True)
    if enviado:
        pregunta = texto.strip() or (ejemplo if ejemplo != opciones[0] else '')
        st.session_state['ai_ultima'] = (fuente, pregunta)
    anterior = st.session_state.get('ai_ultima')
    if not anterior or anterior[0] != fuente:
        return
    pregunta = anterior[1]
    if not pregunta:
        st.info('Escribe una pregunta o selecciona un ejemplo.')
        return
    with st.chat_message('user'):
        st.write(pregunta)
    with st.chat_message('assistant'):
        try:
            salida = consultar(pregunta, df, variables, reglas)
        except DesagregacionNoAutorizada as e:
            st.error(f'Consulta bloqueada: {e}')
            return
        if salida is None:
            st.warning('No pude identificar una consulta estadística compatible. Intenta reformular tu pregunta, selecciona un ejemplo o utiliza el explorador.')
            return
        c, r, by = salida
        st.write(c['descripcion'])
        tabla = r.copy()
        if c['indicador'] == 'participacion':
            tabla['valor'] *= 100
        unidad = 'Q' if c['indicador'] == 'ingreso' else '%'
        validos = tabla.dropna(subset=['valor'])
        if validos.empty:
            st.warning('No existe resultado calculable o publicable.')
        elif c.get('mayor'):
            maximo = validos['valor'].max()
            grupos = ', '.join(validos.loc[validos['valor'].eq(maximo), 'dominio'].astype(str))
            st.metric('Mayor brecha entre resultados disponibles', f'{maximo:.2f}%')
            st.write(grupos)
        elif len(validos) == 1:
            valor = validos.iloc[0]['valor']
            st.metric('Resultado', f'Q{valor:,.2f}' if unidad == 'Q' else f'{valor:.2f}%')
        etiquetas = {'valor':f'Resultado ({unidad})','sexo':'Sexo','dominio':'Dominio','area':'Área',
                     'n_no_ponderado':'Casos del grupo menor' if c['indicador']=='brecha' else 'Casos elegibles',
                     'media_hombres':'Ingreso medio hombres (Q)','media_mujeres':'Ingreso medio mujeres (Q)',
                     'n_hombres':'Casos hombres','n_mujeres':'Casos mujeres','advertencia':'Advertencia'}
        vista = tabla.rename(columns=etiquetas)
        vista['Advertencia'] = vista['Advertencia'].fillna('Sin advertencias detectadas')
        st.dataframe(vista, hide_index=True, use_container_width=True,
                     column_config={f'Resultado ({unidad})':st.column_config.NumberColumn(format='%.2f')})
        if c['indicador'] == 'brecha':
            st.info('Brecha descriptiva; no demuestra causalidad ni discriminación por sí sola.')
        st.caption('Precisión muestral no evaluada. Consulte las advertencias de la tabla.')
