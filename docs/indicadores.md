# Definiciones y fórmulas — Issue #4

Confirmado contra datos reales de `ENEIC I 2026` (muestra de 3000 filas, base Personas,
descargada 2026-11-23). Fuente de variables: `config/variables.yaml`.

## Codificación de las variables derivadas (importante)

`PET`, `PEA`, `OCUPADOS`, `DESOCUPADOS`, `INACTIVOS` son **variables flag**, no binarias 0/1:

- Valor `1` → la persona pertenece a esa categoría.
- Valor vacío/`NaN` → la persona **no** pertenece (no es `0`).

Relación entre ellas (confirmado en muestra): `PEA` y `INACTIVOS` son subconjuntos disjuntos de
`PET`; `OCUPADOS` y `DESOCUPADOS` son subconjuntos disjuntos de `PEA`.

`YLAB_PUBLI` (ingreso laboral) es `NaN` para quien no tiene ingreso laboral que reportar
(población no ocupada, o sin dato) — no tratar `NaN` aquí como cero antes de decidir el
tratamiento (ver indicador 2).

## 1. Participación laboral

```
participación_laboral = Σ(FACTOR donde PEA == 1) / Σ(FACTOR donde PET == 1)
```

Agregable por `sexo` (`P02A02`) y/o `dominio` (`DOMINIO`). Siempre ponderado por `FACTOR`
(cuidado #1), nunca con conteo simple de filas.

## 2. Ingreso laboral medio

```
ingreso_laboral_medio = Σ(FACTOR * YLAB_PUBLI, donde OCUPADOS == 1 y YLAB_PUBLI no es NaN)
                         / Σ(FACTOR, donde OCUPADOS == 1 y YLAB_PUBLI no es NaN)
```

**Implementado (Fase 2, `ingreso_laboral_medio`)**: la población elegible es
`OCUPADOS == 1`, pero dentro de ocupados algunos no reportan ingreso laboral (`YLAB_PUBLI` NaN,
ej. trabajador familiar no remunerado). Se excluyen del denominador explícitamente — no se
imputan como cero, porque un cero falso infla artificialmente la brecha. Esto debe declararse
en la ficha metodológica (campo "tratamiento de faltantes y ceros").

Ceros reportados en `YLAB_PUBLI` (no NaN) **se incluyen** por defecto: son ingreso declarado.
El parámetro `excluir_ceros=True` permite excluirlos para análisis de sensibilidad; si se usa,
debe declararse en la ficha. Pendiente de validar con Estadística cuando se revise la base
completa (cuántos ocupados tienen `YLAB_PUBLI == 0` vs. NaN).

## 3. Brecha relativa de ingreso

```
brecha_relativa = (ingreso_medio_hombres - ingreso_medio_mujeres) / ingreso_medio_hombres * 100
```

Calculado sobre el resultado del indicador 2, agregado por `sexo`. Su `n_no_ponderado` es el
**menor** de los dos grupos (hombres/mujeres), porque es el que limita la precisión. Si
`ingreso_medio_hombres` es 0 o ese `n` es menor al umbral de `config/reglas_calidad.yaml`
(`cruces.minimo_casos_no_ponderados`), el indicador no se calcula y se devuelve la advertencia
de StatShield en su lugar.

**Medida descriptiva, no estimación causal de discriminación** — debe aclararse en la UI cada
vez que se muestra este indicador (lo exige la propuesta y es buena práctica metodológica).

## Desagregaciones válidas

Solo `sexo`, `dominio` y `area` (ver `config/reglas_calidad.yaml` →
`cruces.desagregaciones_permitidas`). `DOMINIO` tiene 3 categorías (Urbano Metropolitano, Resto
Urbano, Rural Nacional) — el diseño muestral de ENEIC **no** soporta desagregación por
municipio.
