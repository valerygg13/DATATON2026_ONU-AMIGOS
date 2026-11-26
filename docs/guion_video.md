# Guion del video demostrativo — Issue #19

Objetivo: 2:00–2:30 min, respaldo si falla la demo en vivo. Grabar con `streamlit run app/app.py`
corriendo sobre la base real (ENEIC I 2026 en `data/raw/`), no en modo demo.

Cada bloque apunta a un criterio del jurado (entre paréntesis) para no dejar ninguno fuera.

## 0:00–0:20 — Qué es y para quién (Aplicabilidad institucional)

> "StatCore GT transforma microdatos del INE en indicadores verificables. No es un tablero
> estático: calcula desde los datos originales, valida cada consulta y documenta su
> procedencia. Está pensado para analistas del INE, en particular Análisis Estadístico y
> Muestreo — pero cualquier institución que trabaje con la ENEIC puede usarlo."

Pantalla: página **Inicio**, mostrar el resumen de participación laboral por dominio.

## 0:20–0:50 — Consulta válida, de punta a punta (Funcionalidad)

> "Vamos al Explorador. Elijo participación laboral, desagrego por sexo y dominio..."

Pantalla: página **Explorador** → seleccionar indicador "Participación laboral" → `by = [sexo,
dominio]` → mostrar tabla + gráfico generados. Señalar el `n_no_ponderado` en la tabla.

> "...y exporto el resultado con su ficha metodológica: fuente, fórmula, fecha de descarga,
> filtros y advertencias — todo en un clic."

Pantalla: botón de exportar CSV / ficha metodológica (StatPassport).

## 0:50–1:15 — DataGuard en acción (Calidad técnica + Rigor de datos)

> "Antes de calcular nada, DataGuard valida la base: estructura, ponderador, códigos especiales
> y rangos."

Pantalla: página **DataGuard** → mostrar el número de registros e incidencias detectadas (o
"cero incidencias" si la base está limpia).

## 1:15–1:40 — StatShield bloqueando lo que no debe calcularse (Innovación)

> "Si pido una desagregación que el diseño muestral no permite, como por municipio, StatShield
> la bloquea y explica por qué — en vez de devolver un número engañoso."

Pantalla: página **StatShield** → ingresar una consulta no autorizada → mostrar el mensaje de
`DesagregacionNoAutorizada`. Luego mostrar una consulta válida para contrastar.

## 1:40–2:00 — Prueba contra cifras oficiales (Rigor de datos)

> "Validamos esto contra el informe oficial del INE: la tasa de participación laboral coincide
> en los cuatro dominios de estudio al redondear a dos decimales."

Pantalla: mostrar la tabla de `docs/validacion_eneic.md` (puede ser un recorte de pantalla
superpuesto, o leerla en voz alta sobre el Explorador con el mismo resultado en pantalla).

## 2:00–2:20 — Cierre: límites honestos + código abierto (Aplicabilidad + Presentación)

> "Es un prototipo: no calcula intervalos de confianza y la brecha de ingreso es descriptiva,
> no causal — lo decimos explícitamente en cada resultado. Todo el código es abierto, corre
> local, sin servicios de pago ni de nube."

Pantalla: volver a **Inicio** o mostrar el repo de GitHub un segundo.

## Checklist antes de grabar

- [ ] Base real de ENEIC I 2026 en `data/raw/` (no modo demo).
- [ ] `pytest` en verde (82 pruebas) — por si alguien pregunta en el Q&A.
- [ ] Practicar la secuencia de clics una vez antes de grabar, para no dudar en cámara.
- [ ] Verificar que el audio no se corte y que el texto en pantalla sea legible (zoom del
      navegador si hace falta).
