# StatCore GT

Motor modular de inteligencia estadística confiable — Datatón INE 2026, Categoría 2 (Tecnológica y ciencias de datos).

Transforma microdatos públicos del INE en indicadores verificables mediante validación de calidad,
cálculo ponderado y control metodológico. Caso de aplicación: brechas de género y autonomía
económica en Guatemala (empleo e ingresos).

## Componentes

| Componente | Carpeta | Función |
|---|---|---|
| DataGuard | `src/dataguard/` | Valida estructura, códigos especiales, rangos y ponderadores |
| StatEngine | `src/statengine/` | Cálculo reproducible de indicadores ponderados por sexo y dominio |
| StatShield | `src/statshield/` | Bloquea cruces no permitidos, advierte tamaño muestral/precisión |
| StatAI (opcional) | `src/statai/` | Interpretación de preguntas vía catálogo de consultas permitidas |
| Interfaz | `app/` | Streamlit + Plotly: filtros, resultados, exportación |

## Fuente de datos

**ENEIC (Encuesta Nacional de Empleo e Ingresos Continua)**, INE Guatemala — sucesora de la ENEI
a partir de 2024T4. Usamos el trimestre más reciente disponible (ENEIC I 2026).

- Portal: https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/
- Bases: Hogares y Personas, formatos `.sav` y `.xlsx`, con diccionario de variables.
- Variables clave ya confirmadas en el diccionario (ver `data/README.md` para el detalle):
  `FACTOR` (ponderador), `DOMINIO`, `P02A02` (sexo), `PET`, `PEA`, `OCUPADOS`, `DESOCUPADOS`,
  `INACTIVOS`, `YLAB_PUBLI` (ingreso laboral), `P05D01` (sueldo/salario bruto).

Los archivos de datos **no se versionan** en este repo (ver `.gitignore`); cada quien los descarga
a `data/raw/` siguiendo `data/README.md`.

## Indicadores del MVP

1. **Participación laboral**: PEA / PET, ponderado, por dominio autorizado.
2. **Ingreso laboral medio**: promedio ponderado del ingreso laboral, con tratamiento documentado
   de faltantes y ceros.
3. **Brecha relativa de ingreso**: (media masculina − media femenina) / media masculina × 100.
   Medida descriptiva, no estimación causal.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
streamlit run app/app.py
pytest                     # pruebas de DataGuard, StatEngine y StatShield
```

La interfaz lista las bases que haya en `data/raw/` (`.sav`, `.xlsx` o `.csv` de la base
Personas). Si no hay ninguna, ofrece un **modo demo con datos sintéticos** (`src/sintetico.py`)
con la misma estructura y codificación de ENEIC; sus resultados no son oficiales y no deben
publicarse.

## Estado

- **Fase 1** (completa): datos confirmados, fórmulas y contratos (`docs/`).
- **Fase 2** (completa): DataGuard, StatEngine (3 indicadores), StatShield e interfaz Streamlit con filtros, tabla, gráfico, advertencias y bloqueo de desagregaciones.

## Equipo y fases de trabajo

Ver [Issues](../../issues) y [Milestones](../../milestones) del repo — organizados según el cronograma del Datatón (23–26 nov 2026) y por rol: Datos, Estadística, Desarrollo web, Integración.

## Licencia y cumplimiento

Proyecto desarrollado durante el Datatón INE 2026. Usa como fuente principal datos públicos del
INE Guatemala (ine.gob.gt). Respeta el secreto estadístico: no intenta identificar personas,
hogares o empresas. No incluye credenciales ni llaves de acceso.
