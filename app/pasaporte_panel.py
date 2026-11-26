import streamlit as st
from src.statpassport import crear_pasaporte, exportar_csv, exportar_ficha

def mostrar_pasaporte(tabla, **contexto):
    ficha = crear_pasaporte(tabla, **contexto)
    with st.expander('StatPassport | Ficha metodológica y descarga', expanded=True):
        st.write(f"**{ficha['indicador']}** · {ficha['edicion']}")
        st.write('**Fórmula:** ' + ficha['formula'])
        st.write('**Universo:** ' + ficha['universo'])
        st.write('**Ponderador:** ' + ficha['ponderador'])
        st.write('**Desagregación:** ' + (', '.join(ficha['desagregacion_efectiva']) or 'Total seleccionado'))
        st.write('**Filtros:** ' + ('; '.join(k + ': ' + ', '.join(map(str,v)) for k,v in ficha['filtros'].items()) or 'Sin filtros'))
        st.write(f"**Incidencias de la base:** {len(ficha['incidencias_base'])}")
        for aviso in ficha['limitaciones']:
            st.caption(aviso)
        a,b = st.columns(2)
        a.download_button('Descargar resultados CSV', exportar_csv(tabla,ficha), 'statcore_resultados.csv', 'text/csv', key='passport_csv')
        b.download_button('Descargar ficha metodológica JSON', exportar_ficha(ficha), 'statcore_pasaporte.json', 'application/json', key='passport_json')
