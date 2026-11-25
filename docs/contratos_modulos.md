# Contratos entre módulos — Issue #5

Define qué entra y qué sale de cada módulo para que Datos, Estadística, Web e Integración
puedan trabajar en paralelo sin bloquearse entre sí.

```
data/raw/*.xlsx  →  DataGuard  →  StatEngine  →  StatShield  →  Interfaz (Streamlit)
```

## 1. DataGuard → StatEngine

**Entrada de DataGuard**: DataFrame crudo (`pandas.read_excel` de la base Personas u Hogares) +
`config/variables.yaml` + `config/reglas_calidad.yaml`.

**Salida de DataGuard**: tupla `(df_limpio, reporte_incidencias)`

- `df_limpio`: `pandas.DataFrame` con las mismas columnas de entrada, sin alterar valores salvo
  los códigos especiales (99) que queden explícitamente marcados como `NaN` según la variable
  (ver `docs/indicadores.md`, nota sobre codificación de flags). No elimina filas.
- `reporte_incidencias`: `list[str]` — cada incidencia detectada (variable esperada faltante,
  ponderador con nulos/ceros, etc.), en texto legible para mostrar en la UI o el README.

## 2. StatEngine → StatShield

**Entrada de StatEngine**: `df_limpio` de DataGuard + nombre del ponderador (`FACTOR`) +
lista `by` de columnas de agregación (ej. `["sexo"]`, `["sexo", "dominio"]`).

`by` usa nombres lógicos (`sexo`, `dominio`, `area`). `agregar_dimensiones(df_limpio, variables)`
crea esas columnas con las etiquetas de `config/variables.yaml` (ej. `P02A02 = 1` → `"Hombre"`)
sin modificar las columnas originales.

**Salida de StatEngine**: `pandas.DataFrame` con una fila por combinación de `by`, y como mínimo
estas columnas:

| columna | tipo | significado |
|---|---|---|
| `valor` | float | el indicador calculado (proporción, promedio o %) |
| `n_no_ponderado` | int | cantidad de observaciones crudas detrás del valor |
| `...by` | las columnas de `by` pasadas | ej. `sexo`, `dominio` |

Esta misma forma la usan `participacion_laboral`, `ingreso_laboral_medio` y
`brecha_relativa_ingreso` — StatShield y la Interfaz no necesitan saber cuál de los tres
indicadores están consumiendo, solo este contrato de columnas.

`brecha_relativa_ingreso` recibe la salida de `ingreso_laboral_medio` con `sexo` en `by`; su
salida ya no tiene `sexo` (una fila por combinación de las demás dimensiones) y agrega las
columnas informativas `media_hombres`, `media_mujeres`, `n_hombres`, `n_mujeres`.

## 3. StatShield → Interfaz

**Entrada de StatShield**: el DataFrame de salida de StatEngine + `by` solicitado +
`config/reglas_calidad.yaml`.

**Salida de StatShield**: la misma estructura de StatEngine, más:

- Lanza `DesagregacionNoAutorizada` (no devuelve DataFrame) si `by` incluye algo en
  `desagregaciones_bloqueadas` — la Interfaz debe capturar esta excepción y mostrar el motivo al
  usuario, no un error genérico.
- Agrega columna `advertencia: str | None` por fila: mensaje si
  `n_no_ponderado < minimo_casos_no_ponderados`, si no `None`.
- Punto de entrada: `aplicar_statshield(resultado, by, reglas, suprimir_bajo_minimo=False)`.
  Con `suprimir_bajo_minimo=True` (usado para la brecha) además pone `valor = NaN` en esas
  filas. Las dimensiones que no están en `desagregaciones_permitidas` también se rechazan.
- La Interfaz llama `verificar_desagregacion` **antes** de StatEngine, para no intentar
  agrupar por columnas inexistentes (ej. `municipio`).

## 4. Interfaz → usuario

Consume el DataFrame final (con `advertencia`) y debe, como mínimo:

- Mostrar la tabla + gráfico.
- Mostrar cualquier `advertencia` de forma visible (no solo en un tooltip).
- Exportar CSV + ficha metodológica (`docs/ficha_metodologica_template.md`) con la misma
  información: fuente, edición, fecha de descarga (de `config/variables.yaml`), filtros (`by`),
  fórmula (ver `docs/indicadores.md`), `n_no_ponderado` y advertencias.

## StatAI (opcional)

Entra *antes* de StatEngine: traduce una pregunta en lenguaje natural a una llamada concreta
`(nombre_de_función, by)` contra `CONSULTAS_PERMITIDAS`. Nunca se salta DataGuard/StatShield ni
calcula nada por su cuenta — si el motor no tiene StatAI, el resto del pipeline debe seguir
funcionando igual desde la Interfaz (selector manual en vez de lenguaje natural).
