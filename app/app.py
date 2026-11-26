"""Interfaz Streamlit de StatCore GT: filtros, resultados, exportación.

Flujo (docs/contratos_modulos.md): DataGuard → StatShield → StatEngine → StatShield → tabla + gráfico.
Ejecutar desde la raíz del repo: streamlit run app/app.py
"""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.config import cargar_config  # noqa: E402
from src.dataguard.validators import cargar_base  # noqa: E402
from src.sintetico import generar_personas  # noqa: E402
from src.statengine.indicadores import DIMENSIONES  # noqa: E402
from src.statshield.guardrails import DesagregacionNoAutorizada  # noqa: E402
from src.pipeline import BaseNoValida, preparar_base, ejecutar_pipeline  # noqa: E402

DEMO = "Demo — datos sintéticos (no oficiales)"
INDICADORES = {
    "Participación laboral (PEA / PET)": "participacion",
    "Ingreso laboral medio (Q mensuales)": "ingreso",
    "Brecha relativa de ingreso por sexo (%)": "brecha",
}
AVISO_BRECHA = (
    "La brecha relativa de ingreso es una **medida descriptiva**, no una estimación causal de "
    "discriminación: no controla por ocupación, horas, escolaridad u otros factores."
)

st.set_page_config(page_title="StatCore GT", layout="wide")
VARIABLES, REGLAS = cargar_config()
PONDERADOR = VARIABLES["base_personas"]["ponderador"]


@st.cache_data(show_spinner="Cargando y validando la base (DataGuard)...")
def preparar_datos(fuente: str):
    df = generar_personas() if fuente == DEMO else cargar_base(RAIZ / "data" / "raw" / fuente)
    return preparar_base(df, VARIABLES, REGLAS)


st.title("StatCore GT")
st.caption("Motor modular de inteligencia estadística confiable — Datatón INE 2026")

# --- Barra lateral: fuente y filtros --------------------------------------------------------
with st.sidebar:
    st.header("Datos")
    archivos = sorted(
        p.name for p in (RAIZ / "data" / "raw").iterdir() if p.suffix.lower() in (".sav", ".xlsx", ".csv")
    )
    fuente = st.selectbox(
        "Base Personas", archivos + [DEMO], help="Coloca la base Personas de ENEIC en data/raw/ (ver data/README.md)."
    )
    try:
        df, incidencias = preparar_datos(fuente)
    except BaseNoValida as e:
        st.error(f"DataGuard bloqueó la base: {e}")
        st.stop()

    st.header("Consulta")
    nombre_indicador = st.selectbox("Indicador", list(INDICADORES))
    indicador = INDICADORES[nombre_indicador]
    cruces = REGLAS["cruces"]
    opciones = list(cruces["desagregaciones_permitidas"]) + list(cruces["desagregaciones_bloqueadas"])
    by = st.multiselect(
        "Desagregar por",
        opciones,
        default=["sexo"],
        help="Las dimensiones fuera del diseño muestral (ej. municipio) se rechazan con su motivo.",
    )

    st.header("Filtros")
    filtros = {}
    for dim in DIMENSIONES:
        if dim in df.columns:
            valores = sorted(df[dim].dropna().unique())
            filtros[dim] = st.multiselect(dim.capitalize(), valores, default=valores)

if fuente == DEMO:
    st.warning(
        "Modo demo: se están usando **datos sintéticos** con la estructura de ENEIC. "
        "Los resultados no representan a Guatemala."
    )
else:
    fuente_cfg = VARIABLES["fuente"]
    st.caption(
        f"Fuente: {fuente_cfg['encuesta']} {fuente_cfg['edicion']}, INE Guatemala — "
        f"descargada {fuente_cfg['fecha_descarga']}. Ponderador: {PONDERADOR}."
    )

with st.expander(f"Reporte DataGuard — {len(incidencias)} incidencia(s)", expanded=bool(incidencias)):
    if incidencias:
        for i in incidencias:
            st.write(f"- {i}")
    else:
        st.success("Sin incidencias: estructura, ponderador, códigos especiales, rangos y flags OK.")

from statai_panel import mostrar_statai

mostrar_statai(df, VARIABLES, REGLAS, fuente, fuente == DEMO)

# --- Cálculo ---------------------------------------------------------------------------------
try:
    resultado, by_efectivo = ejecutar_pipeline(df, indicador, by, VARIABLES, REGLAS, filtros)
except DesagregacionNoAutorizada as e:
    st.error(f"**StatShield bloqueó la consulta.** {e}")
    st.stop()

st.subheader(nombre_indicador)
if indicador == "brecha":
    st.info(AVISO_BRECHA)

if resultado.empty or resultado["valor"].isna().all():
    st.warning("No hay resultado calculable con los filtros seleccionados.")

for _, fila in resultado[resultado["advertencia"].notna()].iterrows():
    etiqueta = " · ".join(str(fila[d]) for d in by_efectivo) or "Total"
    st.warning(f"**{etiqueta}**: {fila['advertencia']}")

# --- Tabla y gráfico -------------------------------------------------------------------------
tabla = resultado.copy()
if indicador == "participacion":
    tabla["valor"] = tabla["valor"] * 100
etiqueta_valor = {"participacion": "Participación (%)", "ingreso": "Ingreso medio (Q)", "brecha": "Brecha (%)"}[
    indicador
]

col_tabla, col_grafico = st.columns([2, 3])
with col_tabla:
    st.dataframe(
        tabla.rename(columns={"valor": etiqueta_valor}),
        hide_index=True,
        column_config={etiqueta_valor: st.column_config.NumberColumn(format="%.2f")},
    )
with col_grafico:
    datos = tabla.dropna(subset=["valor"])
    if not datos.empty:
        if by_efectivo:
            eje_x = by_efectivo[-1] if len(by_efectivo) > 1 and "sexo" in by_efectivo else by_efectivo[0]
            color = next((d for d in by_efectivo if d != eje_x), None)
            fig = px.bar(datos, x=eje_x, y="valor", color=color, barmode="group", text_auto=".1f")
        else:
            fig = px.bar(datos.assign(grupo="Total"), x="grupo", y="valor", text_auto=".1f")
        fig.update_layout(yaxis_title=etiqueta_valor, xaxis_title=None, legend_title=None)
        st.plotly_chart(fig)
