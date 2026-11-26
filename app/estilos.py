"""Identidad visual de StatCore GT, inspirada en el kit del Datatón."""
import streamlit as st


def aplicar_estilos():
    st.markdown('''<style>
    .block-container {max-width: 1520px; padding: 2.3rem 2.4rem 3rem;}
    [data-testid="stAppViewContainer"] {background: #F0F4F9;}
    [data-testid="stSidebar"] {border-right: 1px solid #D8E3EE;}
    [data-testid="stSidebar"] > div:first-child {padding-top: 2rem;}
    .sc-brand {display:flex; align-items:center; gap:14px; margin-bottom: 8px;}
    .sc-brand-mark {width:48px;height:48px;display:grid;place-items:center;background:#004080;border-radius:12px;flex-shrink:0;}
    .sc-brand-name {font-size:1.65rem;font-weight:800;color:#004080;line-height:1.1;}
    .sc-brand-sub {font-size:.86rem;color:#526579;margin-top:4px;}
    .sc-eyebrow {font-size:.75rem;letter-spacing:.12em;font-weight:700;color:#526579;margin-bottom:10px;}
    .sc-hero {position:relative;overflow:hidden;background:linear-gradient(112deg,#003468,#004080 60%,#0064B8);color:white;border-radius:18px;padding:30px 34px;margin:6px 0 12px;}
    .sc-hero h2 {color:white;font-size:clamp(1.7rem,3vw,2.8rem);margin:8px 0;padding:0;line-height:1.12;max-width:75%;}
    .sc-hero p {color:#E1EFFF;margin:8px 0 0;max-width:72%;font-size:1rem;}
    .sc-hero svg {position:absolute;right:24px;bottom:22px;width:23%;height:70%;opacity:.8;}
    [data-testid="stMetric"] {background:#FFFFFF;border:1px solid #D8E3EE;border-radius:14px;padding:18px;box-shadow:0 3px 10px #00408008;}
    [data-testid="stMetricValue"] {color:#004080;font-weight:750;}
    [data-testid="stMetricLabel"] {color:#526579;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-color:#D8E3EE;}
    .st-key-nav_bar {background:#004080;border-radius:12px;padding:8px 10px;}
    .st-key-nav_bar button {background:transparent;color:#FFFFFF;border:1px solid transparent;min-height:44px;font-weight:600;}
    .st-key-nav_bar button[kind="primary"] {background:#FFFFFF;color:#004080;border-color:#FFFFFF;}
    .st-key-nav_bar button:hover {background:#E7F1FF;color:#004080;border-color:#E7F1FF;}
    .st-key-nav_bar button:focus-visible {outline:3px solid #A7D4FF;outline-offset:2px;}
    .sc-module {font-size:.73rem;font-weight:700;letter-spacing:.09em;color:#0061C2;text-transform:uppercase;}
    @media(max-width:700px){.block-container{padding:1.5rem 1rem 2rem;}.sc-hero{padding:23px;}.sc-hero h2,.sc-hero p{max-width:100%;}.sc-hero svg{display:none;}}
    </style>''', unsafe_allow_html=True)


def encabezado():
    st.markdown('''<div class="sc-brand"><div class="sc-brand-mark"><svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><rect x="2" y="17" width="7" height="11" rx="2" fill="#80C5FF"/><rect x="11" y="10" width="7" height="18" rx="2" fill="#0080FF"/><rect x="20" y="2" width="7" height="26" rx="2" fill="white"/></svg></div><div><div class="sc-brand-name">StatCore GT</div><div class="sc-brand-sub">De los datos abiertos a la evidencia confiable</div></div></div>''', unsafe_allow_html=True)


def portada():
    st.markdown('''<div class="sc-hero"><div style="font-size:.75rem;letter-spacing:.12em;color:#C6E2FF;font-weight:700">DATATÓN INE 2026 · EQUIPO ONU-AMIGOS</div><h2>Guatemala en datos.</h2><p>Comprende el empleo y los ingresos desde una perspectiva de género. Explora estadísticas, conoce su metodología y consulta los datos con tus propias palabras.</p><svg viewBox="0 0 180 120" aria-hidden="true"><path d="M5 110H175M5 78H175M5 46H175M5 14H175" stroke="#FFFFFF" opacity=".18"/><rect x="12" y="70" width="20" height="40" rx="4" fill="#91CBFF"/><rect x="39" y="48" width="20" height="62" rx="4" fill="#0080FF"/><rect x="66" y="61" width="20" height="49" rx="4" fill="#91CBFF"/><rect x="93" y="25" width="20" height="85" rx="4" fill="#0080FF"/><rect x="120" y="37" width="20" height="73" rx="4" fill="#91CBFF"/><rect x="147" y="9" width="20" height="101" rx="4" fill="#FFFFFF"/></svg></div>''', unsafe_allow_html=True)
