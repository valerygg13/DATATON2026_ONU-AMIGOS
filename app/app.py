"""Interfaz de StatCore GT. Ejecutar: python -m streamlit run app/app.py."""
import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.config import cargar_config
from src.dataguard.validators import cargar_base
from src.sintetico import generar_personas
from src.statengine.indicadores import DIMENSIONES
from src.statshield.guardrails import DesagregacionNoAutorizada
from src.pipeline import BaseNoValida, preparar_base, ejecutar_pipeline
from statai_panel import mostrar_statai
from src.fuentes import preparar_archivo, huella, MAX_BYTES
from estilos import aplicar_estilos, encabezado, portada

DEMO = 'Demo — datos sintéticos (no oficiales)'
BASE_REFERENCIA = 'Base de datos Personas ENEIC I 2026.sav'
INDICADORES = {'Participación laboral': 'participacion', 'Ingreso laboral medio mensual': 'ingreso',
               'Brecha relativa de ingresos por sexo': 'brecha'}
UNIDADES = {'participacion': 'Participación (%)', 'ingreso': 'Ingreso medio (Q)', 'brecha': 'Brecha (%)'}
ETIQUETAS = {'sexo': 'Sexo', 'dominio': 'Dominio', 'area': 'Área', 'advertencia': 'Advertencia',
             'media_hombres': 'Ingreso medio hombres (Q)', 'media_mujeres': 'Ingreso medio mujeres (Q)',
             'n_hombres': 'Casos hombres', 'n_mujeres': 'Casos mujeres'}
AVISO = 'La brecha de ingresos es descriptiva: no demuestra discriminación ni controla por horas, ocupación o escolaridad.'
PAGINAS = ['Inicio', 'Explorador', 'DataGuard', 'StatShield', 'StatAI']
NOMBRES = {'Inicio':'Inicio', 'Explorador':'Explorar estadísticas', 'DataGuard':'Calidad de datos', 'StatShield':'Metodología', 'StatAI':'Asistente StatAI'}

st.set_page_config(page_title='StatCore GT', layout='wide', page_icon='📊')
aplicar_estilos()
VARIABLES, REGLAS = cargar_config()
CRUCES = REGLAS['cruces']


@st.cache_data(show_spinner='DataGuard está revisando la base...')
def preparar_datos(fuente, version_archivo, variables, reglas):
    if fuente == DEMO:
        df, incidencias = preparar_base(generar_personas(), variables, reglas)
        return df, incidencias, variables, None
    contenido = (RAIZ / 'data' / 'raw' / fuente).read_bytes()
    return preparar_archivo(fuente, contenido, variables, reglas, multiperiodo=True)


def calcular(df, indicador, by=None, filtros=None):
    r, dimensiones = ejecutar_pipeline(df, indicador, by or [], VARIABLES, REGLAS, filtros)
    r = r.copy()
    if indicador == 'participacion':
        r['valor'] *= 100
    return r, dimensiones


def formato(valor, unidad='%'):
    if valor is None or valor != valor:
        return 'No disponible'
    return f'Q{valor:,.2f}' if unidad == 'Q' else f'{valor:.2f}%'


def navegar(pagina):
    st.session_state['pagina'] = pagina


def calidad(incidencias):
    st.metric('Incidencias detectadas', len(incidencias))
    if incidencias:
        for i in incidencias:
            st.warning(str(i))
    else:
        st.success('No se detectaron incidencias en las reglas implementadas.')
    st.caption('Este control no certifica la calidad integral de la encuesta ni la precisión muestral.')


def inicio(df, incidencias):
    portada()
    r, _ = calcular(df, 'participacion')
    por_sexo, _ = calcular(df, 'participacion', ['sexo'])
    valores = por_sexo.set_index('sexo')['valor'].to_dict()
    h, m = valores.get('Hombre'), valores.get('Mujer')
    cols = st.columns(4)
    st.subheader('El empleo en la base seleccionada')
    cols[0].metric('Participación total', formato(r.iloc[0]['valor'] if not r.empty else None))
    cols[1].metric('Participación masculina', formato(h))
    cols[2].metric('Participación femenina', formato(m))
    diferencia = h-m if h is not None and m is not None else float('nan')
    cols[3].metric('Brecha de participación', f'{diferencia:.2f} pp' if diferencia == diferencia else 'No disponible')
    st.caption('Indicadores calculados sobre la base seleccionada completa. Precisión muestral no evaluada.')
    if m is not None and m == m:
        st.write(f'En la base seleccionada, aproximadamente {m:.0f} de cada 100 mujeres en edad de trabajar participan en el mercado laboral (trabajan o buscan trabajo, según la definición de la encuesta).')
    for resultado in (r, por_sexo):
        for aviso in resultado['advertencia'].dropna().unique():
            st.warning(aviso)
    dominios, _ = calcular(df, 'participacion', ['dominio'])
    with st.container(border=True):
        st.subheader('Participación laboral por dominio')
        datos = dominios.dropna(subset=['valor'])
        if not datos.empty:
            fig = px.bar(datos, x='valor', y='dominio', orientation='h', text_auto='.2f', color_discrete_sequence=['#0080FF'])
            fig.update_layout(height=250, margin=dict(l=0,r=20,t=10,b=0), xaxis_title='Participación (%)', yaxis_title=None, plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF')
            fig.update_xaxes(range=[0,105])
            st.plotly_chart(fig, use_container_width=True)
        for aviso in dominios['advertencia'].dropna().unique():
            st.warning(aviso)
    st.subheader('Explora la plataforma')
    opciones = [('Explorador','Consulta indicadores, compara grupos y aplica filtros.'),
                ('DataGuard','Revisa la estructura y consistencia de la base.'),
                ('StatShield','Conoce las reglas que protegen los cálculos.'),
                ('StatAI','Consulta estadísticas mediante preguntas en español.')]
    for fila in (opciones[:2], opciones[2:]):
        for col, (nombre, descripcion) in zip(st.columns(2), fila):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div class="sc-module">{nombre}</div>', unsafe_allow_html=True)
                    st.subheader(NOMBRES[nombre])
                    st.write(descripcion)
                    st.button('Ingresar a '+NOMBRES[nombre], key='abrir_'+nombre, on_click=navegar, args=(nombre,), use_container_width=True)
    st.caption(f'DataGuard: {len(incidencias)} incidencia(s) detectada(s). Caso de aplicación: autonomía económica y brechas de género.')


def explorador(df):
    st.header('Explorador estadístico')
    st.caption('Selecciona un indicador y compara grupos de población.')
    with st.sidebar:
        st.divider()
        st.subheader('Configurar consulta')
        nombre = st.selectbox('Indicador', ['Participación laboral'] if automatico else list(INDICADORES), key='expl_indicador_auto' if automatico else 'expl_indicador')
        indicador = INDICADORES[nombre]
        opciones = list(CRUCES['desagregaciones_permitidas']) + list(CRUCES['desagregaciones_bloqueadas'])
        by = st.multiselect('Desagregar por', opciones, default=['sexo'], key='expl_by',
                            help='Las dimensiones no autorizadas se bloquean antes del cálculo.')
        filtros = {}
        for dim in DIMENSIONES:
            if dim in df.columns:
                valores = sorted(df[dim].dropna().unique())
                filtros[dim] = st.multiselect(ETIQUETAS.get(dim, dim), valores, default=valores,
                                                key=f'expl_{dim}_{identidad_fuente}')
    if indicador == 'brecha':
        st.info(AVISO)
    try:
        tabla, efectivo = calcular(df, indicador, by, filtros)
    except DesagregacionNoAutorizada as e:
        st.error(f'StatShield bloqueó la consulta. {e}')
        return
    st.subheader(nombre)
    st.caption('Consulta permitida por las reglas configuradas. Precisión muestral no evaluada.')
    validos = tabla.dropna(subset=['valor'])
    if validos.empty:
        st.warning('No hay resultado calculable o publicable con estos filtros.')
    for _, fila in tabla[tabla['advertencia'].notna()].iterrows():
        grupo = ' · '.join(str(fila[d]) for d in efectivo) or 'Total seleccionado'
        st.warning(f'{grupo}: {fila["advertencia"]}')
    if len(validos) == 1:
        st.metric(UNIDADES[indicador], formato(validos.iloc[0]['valor'], 'Q' if indicador == 'ingreso' else '%'))
    if not validos.empty:
        datos = validos.copy()
        # Una etiqueta por combinación evita superponer grupos en cruces de 3 dimensiones.
        datos['Grupo'] = datos[efectivo].astype(str).agg(' · '.join, axis=1) if efectivo else 'Total seleccionado'
        if len(efectivo) == 2 and 'sexo' in efectivo:
            eje = next(d for d in efectivo if d != 'sexo')
            fig = px.bar(datos, x=eje, y='valor', color='sexo', barmode='group', text_auto='.2f',
                         color_discrete_map={'Hombre':'#004080','Mujer':'#0080FF'})
        else:
            fig = px.bar(datos, x='Grupo', y='valor', text_auto='.2f', color_discrete_sequence=['#0080FF'])
        fig.update_layout(height=350, plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', yaxis_title=UNIDADES[indicador], xaxis_title=None, legend_title=None, margin=dict(t=25,b=25))
        if indicador == 'participacion':
            fig.update_yaxes(range=[0, 105])
        st.plotly_chart(fig, use_container_width=True)
    etiquetas = {**ETIQUETAS, 'valor': UNIDADES[indicador], 'n_no_ponderado': 'Casos del grupo menor' if indicador == 'brecha' else 'Casos elegibles'}
    vista = tabla.rename(columns=etiquetas).copy()
    if 'Advertencia' in vista:
        vista['Advertencia'] = vista['Advertencia'].fillna('Sin advertencias detectadas')
    st.dataframe(vista, hide_index=True, use_container_width=True,
                 column_config={UNIDADES[indicador]: st.column_config.NumberColumn(format='%.2f')})
    st.caption('Los casos son conteos de la muestra sin ponderar; no representan el total de personas del país.')


encabezado()
# Botones nativos: un único estado de navegación compartido con Inicio.
if st.session_state.get('pagina') not in PAGINAS:
    st.session_state['pagina'] = 'Inicio'
pagina = st.session_state['pagina']
with st.container(key='nav_bar'):
    for col, destino in zip(st.columns([1, 1.7, 1.5, 1.3, 1.5]), PAGINAS):
        col.button(NOMBRES[destino], key='nav_'+destino,
                   type='primary' if pagina == destino else 'secondary',
                   on_click=navegar, args=(destino,), use_container_width=True)
with st.sidebar:
    st.title('Configuración')
    st.caption('FUENTE DE INFORMACIÓN')
    archivos = sorted(p.name for p in (RAIZ/'data'/'raw').glob('*') if p.is_file() and p.suffix.lower() in ('.sav','.xlsx','.csv'))
    modalidad = st.radio('Origen de datos', ['Catálogo local', 'Cargar archivo', 'Modo demo'],
                         index=0 if archivos else 2, key='modalidad_fuente')
    archivo = None
    if modalidad == 'Catálogo local':
        if not archivos:
            st.info('No hay bases locales. Utiliza Cargar archivo o Modo demo.')
            st.stop()
        fuente = st.selectbox('Base Personas', archivos, key='fuente')
    elif modalidad == 'Cargar archivo':
        st.caption('Archivos públicos ENEIC. Detectamos el año y código de período; ediciones nuevas se evalúan de forma experimental. No cargues datos confidenciales.')
        archivo = st.file_uploader('Base Personas', type=['sav', 'csv', 'xlsx'], key='archivo_personas')
        st.caption('Máximo 50 MB. Procesamiento temporal en el servidor; sin guardado permanente intencional.')
        if archivo is None:
            st.session_state.pop('base_cargada', None)
            st.info('Selecciona un archivo para comenzar.')
            st.stop()
        fuente = archivo.name
    else:
        fuente = DEMO
    st.caption('La fuente se conserva al navegar.')

demo = modalidad == 'Modo demo'
subido = modalidad == 'Cargar archivo'
if not subido:
    st.session_state.pop('base_cargada', None)
if demo:
    st.warning('Modo demo · Datos sintéticos. Los resultados no representan a Guatemala.')
else:
    st.caption('Prototipo del Datatón; los cálculos no son publicaciones oficiales del INE.')
    if subido:
        st.info('Archivo aportado por el usuario; procedencia oficial no verificada.')
try:
    if subido:
        if archivo.size > MAX_BYTES:
            raise BaseNoValida('El archivo supera 50 MB.')
        contenido = archivo.getvalue()
        identidad_fuente = 'upload:' + Path(fuente).suffix.lower() + ':' + huella(contenido)
        guardado = st.session_state.get('base_cargada')
        if guardado is None or guardado[0] != identidad_fuente:
            st.session_state.pop('base_cargada', None)
            with st.spinner('Validando archivo con DataGuard...'):
                df, incidencias, VARIABLES, perfil = preparar_archivo(fuente, contenido, VARIABLES, REGLAS, multiperiodo=True)
            st.session_state['base_cargada'] = (identidad_fuente, df, incidencias, VARIABLES, perfil)
        else:
            _, df, incidencias, VARIABLES, perfil = guardado
    else:
        version = (RAIZ/'data'/'raw'/fuente).stat().st_mtime_ns if not demo else 0
        identidad_fuente = f'local:{fuente}:{version}'
        df, incidencias, VARIABLES, perfil = preparar_datos(fuente, version, VARIABLES, REGLAS)
except BaseNoValida as e:
    st.error(f'DataGuard bloqueó la base: {e}')
    st.stop()
except Exception as e:
    st.error(f'No se pudo leer o validar la base ({type(e).__name__}). Verifica formato y estructura.')
    st.stop()
automatico = not demo and perfil['estado'] == 'experimental_automatico'
if not demo:
    st.caption(f'Fuente seleccionada: {fuente} · Perfil ENEIC {perfil["edicion"]} · Ponderador: {VARIABLES["base_personas"]["ponderador"]}. Procedencia no certificada.')
    if perfil['estado'] == 'experimental':
        st.warning('Perfil 2025 experimental: participación contrastada con referencias; ingresos y brechas requieren validación metodológica adicional. No interpretar como cifras oficiales ni como cambios significativos.')
if automatico:
    st.warning('Edición no registrada: superó controles técnicos bajo las reglas de ENEIC I 2026. No se ha confirmado su metodología, representatividad ni procedencia. Solo se habilita participación laboral exploratoria; no es una cifra oficial.')
    autorizado = st.checkbox('Entiendo las limitaciones y deseo explorar bajo estos supuestos.', key='aceptar_'+identidad_fuente)
    if pagina != 'DataGuard' and not autorizado:
        st.info('Puedes revisar Calidad de datos sin aceptar los supuestos.')
        st.stop()
    if pagina == 'StatAI':
        st.info('StatAI no está habilitado para ediciones sin perfil metodológico registrado.')
        st.stop()
if st.session_state.get('ultima_fuente_id') != identidad_fuente:
    st.session_state.pop('ai_ultima', None)
    st.session_state['ultima_fuente_id'] = identidad_fuente
if subido and incidencias and pagina != 'DataGuard':
    st.warning('La base cargada tiene incidencias. Revísalas en Calidad de datos antes de interpretar los resultados.')

if pagina == 'Inicio':
    inicio(df, incidencias)
elif pagina == 'Explorador':
    explorador(df)
elif pagina == 'DataGuard':
    st.header('DataGuard | Calidad de datos')
    st.write('Revisión de estructura, ponderadores, códigos especiales, rangos y consistencia lógica.')
    a, b = st.columns(2)
    a.metric('Registros de la base preparada', f'{len(df):,}')
    with b:
        calidad(incidencias)
elif pagina == 'StatShield':
    st.header('StatShield | Protección metodológica')
    st.write('Controla las dimensiones permitidas antes del cálculo y aplica advertencias a los resultados.')
    a,b = st.columns(2)
    a.info('Dimensiones permitidas: '+', '.join(CRUCES['desagregaciones_permitidas']))
    b.warning('Dimensiones bloqueadas: '+', '.join(CRUCES['desagregaciones_bloqueadas']))
    st.metric('Umbral preventivo de casos', CRUCES['minimo_casos_no_ponderados'])
    st.caption('Este umbral no mide precisión muestral. En brechas se considera el grupo menor.')
    st.subheader('Comprueba una consulta')
    dimension = st.selectbox('Dimensión solicitada', list(CRUCES['desagregaciones_permitidas'])+list(CRUCES['desagregaciones_bloqueadas']), key='shield_dim')
    if st.button('Verificar consulta', key='shield_check'):
        try:
            resultado, _ = calcular(df, 'participacion', [dimension])
            st.success('Consulta permitida según las reglas configuradas.')
            st.dataframe(resultado.rename(columns={'valor':'Participación (%)','n_no_ponderado':'Casos elegibles', **ETIQUETAS}), hide_index=True)
        except DesagregacionNoAutorizada as e:
            st.error(f'StatShield bloqueó la consulta. {e}')
    st.subheader('Reproducibilidad: tasa de participación laboral')
    if demo:
        st.caption('La comparación no está disponible para datos sintéticos.')
    elif not perfil.get('referencia_participacion'):
        st.info('No hay referencias registradas para esta edición. No se puede evaluar la reproducibilidad oficial.')
    else:
        import pandas as pd
        total,_ = calcular(df,'participacion')
        dominios,_ = calcular(df,'participacion',['dominio'])
        valores = dominios.set_index('dominio')['valor'].to_dict()
        valores['Nacional'] = total.iloc[0]['valor'] if not total.empty else float('nan')
        referencia = perfil['referencia_participacion']
        dec = perfil['decimales_referencia']
        filas = [{'Cobertura':k,'Referencia INE (%)':v,'StatCore GT (%)':round(valores.get(k,float('nan')),dec),
                  f'Coincidencia a {dec} decimal(es)': 'Sí' if round(valores.get(k,float('nan')),dec)==v else 'No'} for k,v in referencia.items()]
        st.dataframe(pd.DataFrame(filas),hide_index=True,use_container_width=True)
        st.caption(f'Perfil ENEIC {perfil["edicion"]}. Contraste numérico de estimaciones puntuales; no certifica procedencia ni precisión muestral.')

else:
    mostrar_statai(df, VARIABLES, REGLAS, fuente, demo)

st.divider()
st.caption('StatCore GT · Equipo ONU-AMIGOS · Datatón INE 2026 · Prototipo de código abierto')
