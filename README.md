# StatCore GT

Motor modular de inteligencia estadística confiable — Datatón INE 2026, Categoría 2 (Tecnológica y ciencias de datos). Equipo ONU-AMIGOS.

## Problema y usuarios

Acceder a una base de datos pública no garantiza usarla bien: identificar variables, interpretar
códigos especiales, aplicar factores de expansión y respetar el dominio de estudio exige
conocimiento técnico. Un error en cualquiera de esos pasos produce estimaciones engañosas.

StatCore GT transforma microdatos públicos del INE en indicadores verificables mediante
validación de calidad, cálculo ponderado y control metodológico explícito — no es un tablero
estático, calcula desde los datos originales y documenta la procedencia de cada resultado.

**Usuarios principales**: analistas del INE (Análisis Estadístico y Muestreo). **Secundarios**:
investigadores, estudiantes y personal de otras instituciones que trabajen con encuestas de
hogares de Guatemala.

**Caso de aplicación**: brechas de género y autonomía económica — participación laboral, ingreso
laboral medio y brecha relativa de ingreso, usando la ENEIC.

## Arquitectura

```
data/raw/*.{sav,xlsx,csv}  →  DataGuard  →  StatEngine  →  StatShield  →  Interfaz (Streamlit)
                                                                ↑
                                                             StatAI (opcional)
```

| Componente | Carpeta | Función |
|---|---|---|
| DataGuard | `src/dataguard/` | Valida estructura, códigos especiales, rangos y ponderadores |
| StatEngine | `src/statengine/` | Cálculo reproducible de indicadores ponderados por sexo y dominio |
| StatShield | `src/statshield/` | Bloquea cruces no permitidos, advierte tamaño muestral/precisión |
| StatAI (opcional) | `src/statai/` | Interpretación de preguntas vía catálogo de consultas permitidas |
| Interfaz | `app/` | Streamlit + Plotly: filtros, resultados, exportación |

Módulos de soporte: `src/fuentes.py` (carga y valida archivos subidos por el usuario, detecta
ediciones nuevas de ENEIC de forma experimental), `src/perfiles.py` (identifica el período de la
base contra `config/perfiles.yaml`), `src/pipeline.py` (orquesta DataGuard → StatEngine →
StatShield fuera de la UI), `src/statpassport.py` (genera la ficha metodológica y exporta
CSV/JSON), `src/sintetico.py` (datos sintéticos para el modo demo).

**Tecnologías**: Python 3, pandas, NumPy, pyreadstat (lectura de `.sav`), openpyxl (`.xlsx`),
PyYAML, Streamlit + Plotly (interfaz), pytest (82 pruebas). Sin frameworks de pago ni servicios en
la nube — ver "Cumplimiento" más abajo.

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
```

## Uso de la interfaz

Al abrir `streamlit run app/app.py`, en la barra lateral se elige el **origen de datos**:

1. **Catálogo local** — bases que ya estén en `data/raw/` (ver `data/README.md`).
2. **Cargar archivo** — subir una base Personas (`.sav`/`.xlsx`/`.csv`, máx. 50 MB) desde el
   navegador; se procesa en un directorio temporal, sin guardado permanente. StatCore detecta el
   año y período (`ANIO`/`TRIMESTRE`) y, si no coincide con un perfil conocido
   (`config/perfiles.yaml`), lo trata como **edición experimental**: exige controles más
   estrictos y limita qué se puede calcular hasta que el equipo valide esa edición.
3. **Modo demo** — datos sintéticos (`src/sintetico.py`) con la misma estructura y codificación
   de ENEIC, para probar la herramienta sin una base real. Sus resultados **no representan a
   Guatemala** y no deben publicarse.

Páginas disponibles: **Inicio** (resumen), **Explorador** (consultas con filtros, tabla, gráfico
y exportación CSV/ficha metodológica — `src/statpassport.py`), **DataGuard** (incidencias de
calidad detectadas), **StatShield** (prueba en vivo de una consulta válida y una no autorizada) y
**StatAI** (catálogo cerrado de preguntas en lenguaje natural, deshabilitado para ediciones
experimentales).

```bash
pytest   # 82 pruebas: DataGuard, StatEngine, StatShield, StatAI, pipeline, perfiles, fuentes, ficha
```

## Datasets utilizados

**ENEIC I 2026** (base Personas), fuente principal. Ver `data/README.md` para variables
confirmadas y `docs/indicadores.md` para las fórmulas exactas. La prueba de reproducibilidad
contra el informe oficial del INE está documentada en `docs/validacion_eneic.md` (tasa de
participación laboral, 4/4 dominios coincidentes al redondear a dos decimales).

## Limitaciones y posibles mejoras

- **Precisión muestral no evaluada**: no se calculan errores estándar, intervalos de confianza ni
  coeficientes de variación — el umbral de casos mínimos en StatShield es preventivo, no una
  certificación de precisión.
- **Brecha de ingreso es descriptiva**, no controla por horas trabajadas, ocupación o
  escolaridad; no debe leerse como estimación causal de discriminación.
- **Un solo trimestre validado oficialmente** (ENEIC I 2026); el perfil 2025 solo está
  contrastado en participación laboral, no en ingresos. Ediciones no registradas se procesan bajo
  supuestos no validados y quedan marcadas como exploratorias en la interfaz.
- **Hogares no se usa en el MVP** (solo variables de vivienda/alquiler, fuera del alcance de los
  3 indicadores actuales).
- **Mejoras posibles**: más indicadores (otros dominios, otras encuestas), intervalos de
  confianza reales vía diseño muestral, historial multi-trimestre, y validación formal de nuevas
  ediciones antes de habilitarlas fuera del modo "exploratorio".

## Equipo y fases de trabajo

Ver [Issues](../../issues) y [Milestones](../../milestones) del repo — organizados según el cronograma del Datatón (23–27 nov 2026) y por rol: Datos, Estadística, Desarrollo web, Integración.

## Cumplimiento

- Fuente principal: datos públicos del INE Guatemala (ine.gob.gt), con fuente y fecha de descarga
  registradas (`config/variables.yaml`, ficha metodológica de cada exportación).
- Respeta el secreto estadístico: no intenta identificar personas, hogares o empresas; no se
  cargan ni se guardan microdatos de forma permanente en el servidor.
- No incluye credenciales, contraseñas ni llaves de acceso en el código.
- **Sin servicios de pago ni de nube**: todo corre localmente. StatAI es un emparejador contra un
  catálogo cerrado de preguntas (`src/statai/catalogo.py`) — no usa un LLM ni hace llamadas a
  servicios externos.
- **Uso de IA generativa durante el desarrollo**: se utilizó un asistente de código con IA
  generativa como apoyo durante el desarrollo del proyecto. El equipo puede explicar y defender
  la totalidad del código presentado.
- Dependencias de terceros y sus licencias: ver `requirements.txt` (todas de código abierto,
  licencias permisivas estándar del ecosistema Python/PyPI).
