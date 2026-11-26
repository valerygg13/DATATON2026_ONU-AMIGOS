"""Genera el esqueleto de la presentación en PDF (issue de Entrega, #21).

No es parte de la aplicación StatCore GT -- es una herramienta de un solo uso para producir
el PDF que exige el lineamiento del Datatón ("Presentación en formato PDF para la exposición
ante el jurado"). El contenido es un ESQUELETO: estructura, mensajes clave y placeholders
donde el equipo debe pegar capturas de pantalla reales antes de entregar.

Uso:
    pip install fpdf2
    python docs/presentacion/generar_pdf.py

Produce docs/presentacion/StatCoreGT_presentacion.pdf (12 diapositivas, orientación horizontal).
Editar el contenido de SLIDES más abajo y volver a correr el script para regenerar el PDF.
"""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

AZUL_INE = (0, 64, 128)       # #004080, el primaryColor de .streamlit/config.toml
AZUL_CLARO = (240, 244, 249)  # #F0F4F9, backgroundColor
GRIS_TEXTO = (22, 53, 82)     # #163552, textColor
BLANCO = (255, 255, 255)

ANCHO, ALTO = 297, 210  # A4 horizontal, mm
MARGEN = 18


class Presentacion(FPDF):
    def __init__(self):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_margins(MARGEN, MARGEN, MARGEN)
        self.set_auto_page_break(False)

    def pie_de_pagina(self):
        self.set_y(-15)
        self.set_font("helvetica", "", 9)
        self.set_text_color(*GRIS_TEXTO)
        self.cell(0, 8, "StatCore GT - Equipo ONU-AMIGOS - Dataton INE 2026", align="L")
        self.set_xy(-MARGEN - 20, -15)
        self.cell(20, 8, f"{self.page_no()}/{{nb}}", align="R")

    def nueva_diapositiva(self, kicker: str, titulo: str):
        self.add_page()
        self.set_fill_color(*AZUL_CLARO)
        self.rect(0, 0, ANCHO, ALTO, style="F")
        self.set_fill_color(*AZUL_INE)
        self.rect(0, 0, ANCHO, 28, style="F")
        self.set_xy(MARGEN, 6)
        self.set_text_color(*BLANCO)
        self.set_font("helvetica", "B", 11)
        self.cell(0, 6, kicker.upper())
        self.set_xy(MARGEN, 13)
        self.set_font("helvetica", "B", 20)
        self.cell(0, 12, titulo)
        self.set_text_color(*GRIS_TEXTO)
        self.set_xy(MARGEN, 40)
        self.pie_de_pagina()
        self.set_xy(MARGEN, 40)

    def bullet(self, texto: str, nivel: int = 0, tamano: int = 15, interlineado: float = 9):
        self.set_font("helvetica", "" if nivel else "B", tamano)
        sangria = MARGEN + 8 * nivel
        self.set_x(sangria)
        marca = "-" if nivel else "*"
        self.multi_cell(ANCHO - sangria - MARGEN, interlineado, f"{marca} {texto}")
        self.ln(1)

    def espacio(self, mm: float = 4):
        self.ln(mm)

    def placeholder_captura(self, etiqueta: str, alto: float = 70):
        x0, y0 = self.get_x(), self.get_y()
        self.set_draw_color(*AZUL_INE)
        self.set_dash_pattern(dash=2, gap=2)
        self.rect(x0, y0, ANCHO - MARGEN - x0, alto)
        self.set_dash_pattern()
        self.set_xy(x0, y0 + alto / 2 - 4)
        self.set_font("helvetica", "I", 12)
        self.set_text_color(*AZUL_INE)
        self.cell(ANCHO - MARGEN - x0, 8, f"[ Captura pendiente: {etiqueta} ]", align="C")
        self.set_text_color(*GRIS_TEXTO)
        self.set_xy(x0, y0 + alto + 6)

    def tabla(self, encabezados: list[str], filas: list[list[str]], anchos: list[float]):
        self.set_font("helvetica", "B", 12)
        self.set_fill_color(*AZUL_INE)
        self.set_text_color(*BLANCO)
        for h, w in zip(encabezados, anchos):
            self.cell(w, 9, h, border=1, align="C", fill=True)
        self.ln()
        self.set_font("helvetica", "", 12)
        self.set_text_color(*GRIS_TEXTO)
        for fila in filas:
            for valor, w in zip(fila, anchos):
                self.cell(w, 9, valor, border=1, align="C")
            self.ln()


def construir() -> Presentacion:
    pdf = Presentacion()
    pdf.alias_nb_pages()

    # 1. Portada
    pdf.add_page()
    pdf.set_fill_color(*AZUL_INE)
    pdf.rect(0, 0, ANCHO, ALTO, style="F")
    pdf.set_text_color(*BLANCO)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_xy(MARGEN, 30)
    pdf.cell(0, 8, "DATATON INE 2026 - CATEGORIA 2: TECNOLOGICA Y CIENCIAS DE DATOS")
    pdf.set_xy(MARGEN, 70)
    pdf.set_font("helvetica", "B", 44)
    pdf.cell(0, 20, "StatCore GT")
    pdf.set_xy(MARGEN, 95)
    pdf.set_font("helvetica", "", 18)
    pdf.cell(0, 10, "Motor modular de inteligencia estadistica confiable")
    pdf.set_xy(MARGEN, 108)
    pdf.set_font("helvetica", "I", 14)
    pdf.cell(0, 8, "Caso de aplicacion: brechas de genero y autonomia economica en Guatemala")
    pdf.set_xy(MARGEN, ALTO - 30)
    pdf.set_font("helvetica", "", 13)
    pdf.cell(0, 8, "Equipo ONU-AMIGOS")
    pdf.set_xy(MARGEN, ALTO - 22)
    pdf.cell(0, 8, "[ Nombres de los integrantes ]")

    # 2. El problema
    pdf.nueva_diapositiva("El problema", "Tener acceso a los datos no es lo mismo que usarlos bien")
    pdf.bullet("Identificar variables, interpretar codigos especiales, aplicar factores de")
    pdf.bullet("expansion y respetar el dominio de estudio exige conocimiento tecnico.", 1)
    pdf.espacio()
    pdf.bullet("Un error en cualquiera de esos pasos produce estimaciones enganosas")
    pdf.bullet("y aumenta el trabajo de revision posterior.", 1)
    pdf.espacio()
    pdf.bullet("Usuarios: analistas del INE (Analisis Estadistico y Muestreo); tambien")
    pdf.bullet("investigadores, estudiantes y otras instituciones.", 1)

    # 3. Propuesta de valor
    pdf.nueva_diapositiva("Nuestra propuesta", "No es un tablero estatico")
    pdf.bullet("Calcula indicadores desde los microdatos originales, no desde cifras")
    pdf.bullet("pre-calculadas.", 1)
    pdf.espacio()
    pdf.bullet("Valida cada consulta antes de calcularla: bloquea lo que el diseno")
    pdf.bullet("muestral no permite.", 1)
    pdf.espacio()
    pdf.bullet("Documenta la procedencia de cada resultado: fuente, formula, fecha de")
    pdf.bullet("descarga, filtros y advertencias.", 1)
    pdf.espacio()
    pdf.bullet("La IA es opcional y nunca sustituye el calculo estadistico.")

    # 4. Arquitectura
    pdf.nueva_diapositiva("Arquitectura", "Cuatro componentes, un solo flujo")
    pdf.set_font("helvetica", "B", 14)
    pdf.set_x(MARGEN)
    pdf.cell(0, 10, "data/raw -> DataGuard -> StatEngine -> StatShield -> Interfaz (Streamlit)")
    pdf.espacio(8)
    pdf.bullet("DataGuard: valida estructura, codigos especiales, rangos y ponderadores.")
    pdf.bullet("StatEngine: calcula los 3 indicadores, ponderados por sexo y dominio.")
    pdf.bullet("StatShield: bloquea cruces no permitidos y advierte tamano muestral.")
    pdf.bullet("StatAI (opcional): catalogo cerrado de preguntas; sin LLM, sin nube.")

    # 5. Fuente de datos
    pdf.nueva_diapositiva("Fuente de datos", "ENEIC - Encuesta Nacional de Empleo e Ingresos Continua")
    pdf.bullet("Edicion: ENEIC I 2026, INE Guatemala (ine.gob.gt).")
    pdf.bullet("Variables clave: FACTOR (ponderador), DOMINIO, sexo, PET, PEA, OCUPADOS,")
    pdf.bullet("DESOCUPADOS, INACTIVOS, ingreso laboral (YLAB_PUBLI).", 1)
    pdf.espacio()
    pdf.bullet("Fuente y fecha de descarga registradas en cada ficha metodologica exportada.")

    # 6. Indicadores
    pdf.nueva_diapositiva("Indicadores del MVP", "Tres indicadores, con su formula declarada")
    pdf.bullet("1. Participacion laboral = PEA / PET, ponderado por FACTOR.")
    pdf.bullet("2. Ingreso laboral medio = promedio ponderado del ingreso laboral de la")
    pdf.bullet("poblacion ocupada con ingreso valido.", 1)
    pdf.bullet("3. Brecha relativa de ingreso = (media hombres - media mujeres) /")
    pdf.bullet("media hombres x 100. Medida descriptiva, no estimacion causal.", 1)

    # 7. Demo: funcionalidad
    pdf.nueva_diapositiva("Demostracion", "Funcionalidad: consulta de punta a punta")
    pdf.bullet("Explorador: elegir indicador, desagregar por sexo y dominio, ver tabla y")
    pdf.bullet("grafico, exportar CSV + ficha metodologica en un clic.", 1)
    pdf.placeholder_captura("pantalla del Explorador con un resultado real", alto=55)

    # 8. Demo: calidad e innovacion
    pdf.nueva_diapositiva("Demostracion", "DataGuard y StatShield en accion")
    pdf.bullet("DataGuard: incidencias de calidad detectadas en la base (o cero incidencias).")
    pdf.bullet("StatShield: una consulta no autorizada (ej. por municipio) se bloquea y")
    pdf.bullet("explica el motivo, en vez de devolver un numero enganoso.", 1)
    pdf.placeholder_captura("pantalla de DataGuard / StatShield bloqueando una consulta", alto=55)

    # 9. Rigor de datos
    pdf.nueva_diapositiva("Rigor de datos", "Validado contra el informe oficial del INE")
    pdf.bullet("Prueba de aceptacion: reproducir la tasa de participacion laboral publicada")
    pdf.bullet("por el INE para ENEIC I 2026 (docs/validacion_eneic.md).", 1)
    pdf.espacio(2)
    pdf.tabla(
        ["Dominio", "INE (%)", "StatCore GT (%)", "Diferencia (pp)"],
        [
            ["Nacional", "64.2195", "64.22", "0.0005"],
            ["Urbano Metropolitano", "66.9505", "66.95", "0.0005"],
            ["Resto Urbano", "65.4826", "65.48", "0.0026"],
            ["Rural Nacional", "61.8645", "61.86", "0.0045"],
        ],
        [65, 55, 55, 55],
    )
    pdf.espacio(4)
    pdf.bullet("4 de 4 dominios coinciden al redondear a dos decimales.", tamano=13)

    # 10. Limitaciones
    pdf.nueva_diapositiva("Limitaciones", "Honestidad metodologica, no solo funcionalidad")
    pdf.bullet("No se calculan errores estandar ni intervalos de confianza (precision")
    pdf.bullet("muestral no evaluada).", 1)
    pdf.bullet("La brecha de ingreso es descriptiva: no controla por horas, ocupacion ni")
    pdf.bullet("escolaridad.", 1)
    pdf.bullet("Un solo trimestre validado oficialmente (ENEIC I 2026); ediciones nuevas")
    pdf.bullet("se marcan como exploratorias hasta validarlas.", 1)
    pdf.bullet("Mejoras futuras: mas indicadores, intervalos de confianza reales via diseno")
    pdf.bullet("muestral, historial multi-trimestre.", 1)

    # 11. Cumplimiento
    pdf.nueva_diapositiva("Cumplimiento", "Secreto estadistico, sin nube, con IA declarada")
    pdf.bullet("No intenta identificar personas, hogares ni empresas; sin guardado")
    pdf.bullet("permanente de archivos subidos.", 1)
    pdf.bullet("Sin servicios de pago ni de nube: StatAI corre localmente, sin LLM.")
    pdf.bullet("Uso de un asistente de codigo con IA generativa declarado durante el")
    pdf.bullet("desarrollo (ver README, seccion Cumplimiento).", 1)
    pdf.bullet("Codigo 100% abierto, dependencias con licencias permisivas (MIT/BSD/Apache).")

    # 12. Cierre
    pdf.nueva_diapositiva("Cierre", "Codigo abierto, listo para usarse")
    pdf.bullet("Repositorio: github.com/valerygg13/DATATON2026_ONU-AMIGOS")
    pdf.bullet("82 pruebas automatizadas; instalacion reproducible con requirements.txt.")
    pdf.espacio(6)
    pdf.set_font("helvetica", "B", 18)
    pdf.set_x(MARGEN)
    pdf.cell(0, 10, "Gracias - preguntas")

    return pdf


if __name__ == "__main__":
    salida = Path(__file__).parent / "StatCoreGT_presentacion.pdf"
    construir().output(str(salida))
    print(f"Generado: {salida}")
