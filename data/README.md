# Datos

Este proyecto usa la **ENEIC** (Encuesta Nacional de Empleo e Ingresos Continua) del INE
Guatemala como fuente principal. Los archivos de microdatos no se versionan en Git; descárgalos
manualmente y colócalos en `data/raw/`.

## Dónde descargar

https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/ → pestaña **ENEIC 2026** (o la
edición trimestral que el equipo confirme como definitiva) → sección "Bases de datos":

- `Base de datos Hogares ENEIC <trimestre> <año>.xlsx` (o `.sav`)
- `Base de datos Personas ENEIC <trimestre> <año>.xlsx` (o `.sav`)
- `Diccionario Hogares ENEIC <trimestre> <año>.xlsx`
- `Diccionario Personas ENEIC <trimestre> <año>.xlsx`

**Registrar siempre, al descargar:** edición/trimestre exacto y fecha de descarga (va en la ficha
metodológica — ver `docs/`).

## Variables clave confirmadas (base Personas)

| Variable | Posición | Etiqueta |
|---|---|---|
| `ANIO` | 1 | Año |
| `TRIMESTRE` | 2 | N° de trimestre |
| `DOMINIO` | 3 | Dominio de estudio |
| `NUM_HOGAR` | 4 | Número de hogar |
| `FACTOR` | 5 | Factor de expansión (ponderador) |
| `P00A10` | 6 | Área |
| `P02A02` | 12 | Sexo |
| `P02A03` | 13 | Edad |
| `P05D01` | 105 | Sueldo/salario mensual bruto (trabajo principal) |
| `YLAB_PUBLI` | 263 | Ingreso laboral (versión pública) |
| `PET` | 264 | Población en edad de trabajar |
| `PEA` | 265 | Población económicamente activa |
| `OCUPADOS` | 266 | Población ocupada |
| `DESOCUPADOS` | 267 | Población desocupada |
| `INACTIVOS` | 269 | Población económicamente inactiva |

`PET`, `PEA`, `OCUPADOS`, `DESOCUPADOS`, `INACTIVOS` ya vienen calculadas por el INE — no hace
falta derivarlas desde las preguntas crudas de la boleta (P05A02...P05H12) salvo que el equipo
quiera auditar/explicar el cálculo.

## Seis cuidados del INE (checklist DataGuard/StatShield)

Fuente: presentación DCE, Datatón INE 2026.

1. Aplicar el factor de expansión (`FACTOR`) — sin él se describe la muestra, no el país.
2. Respetar el dominio de estudio (`DOMINIO`) — no desagregar por debajo del nivel que el diseño permite.
3. Cuidar cruces con pocos casos — advertir cuando el `n` no ponderado sea muy bajo.
4. Limpiar códigos especiales ("no sabe"/"no responde", típicamente 98/99) antes de calcular.
5. Usar las definiciones oficiales del INE (actividad, ingreso, etc.), no inventar las propias.
6. Citar fuente, edición y fecha de descarga; nunca intentar identificar personas u hogares.

## Datos de referencia para validar resultados

- Sección "Indicadores" de la misma página de ENEIC (series históricas oficiales por tema).
- `ine.gob.gt/genero-y-pueblos/` → Compendio Estadístico con Enfoque de Género — útil para la
  prueba de aceptación "reproducir un indicador publicado para la misma edición/dominio".
