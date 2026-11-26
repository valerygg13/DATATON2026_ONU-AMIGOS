# Validación estadística de StatCore GT

## Prueba de aceptación — Issue #14

**Fecha:** 25 de noviembre de 2026  
**Fuente:** Instituto Nacional de Estadística de Guatemala  
**Operación estadística:** ENEIC, primer trimestre de 2026  
**Base:** Base de datos Personas ENEIC I 2026.sav  
**Ponderador:** FACTOR  
**Indicador:** Tasa Global de Participación (PEA/PET)

## Objetivo

Verificar que StatCore GT reproduce los resultados publicados por el INE mediante el procesamiento automatizado de microdatos oficiales.

## Resultados

| Dominio | INE (%) | StatCore GT (%) | Diferencia (pp) |
|---|---:|---:|---:|
| Nacional | 64.2195 | 64.22 | 0.0005 |
| Urbano Metropolitano | 66.9505 | 66.95 | 0.0005 |
| Resto Urbano | 65.4826 | 65.48 | 0.0026 |
| Rural Nacional | 61.8645 | 61.86 | 0.0045 |

## Criterio de aceptación

Coincidencia de los resultados al redondear a dos decimales.

## Evidencia

- Procesamiento de la base oficial en formato SAV.
- 35,040 observaciones no ponderadas correspondientes al universo PET reportado por el sistema.
- Cero incidencias detectadas por las reglas implementadas en DataGuard.
- Cuatro de cuatro estimaciones coincidentes.
- Verificación manual mediante la interfaz de StatCore GT.

## Conclusión

La prueba de aceptación se considera superada para la tasa global de participación laboral, a nivel nacional y para los tres dominios de estudio.

## Limitaciones

La coincidencia de las estimaciones puntuales no constituye una validación completa de todos los indicadores ni de sus errores estándar, intervalos de confianza o coeficientes de variación.

## Referencia

Instituto Nacional de Estadística de Guatemala (2026). Informe de resultados de la Encuesta Nacional de Empleo e Ingresos Continua — ENEIC 2026. Secciones 4.6 y 5.21–5.24, páginas 91, 105 y 106.