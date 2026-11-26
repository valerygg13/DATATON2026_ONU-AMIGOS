# Guion de exposición ante el jurado — 7 minutos + 3 de preguntas

Para la presentación de 12 diapositivas (`docs/presentacion/StatCoreGT_presentacion.pdf` /
Canva). Distinto del guion del video de respaldo (`docs/guion_video.md`, 2-3 min, solo
demo grabada). Este es para la exposición en vivo si el equipo clasifica como finalista.

Tiempo total objetivo: 6:30–7:00, dejando margen. Se puede repartir entre varios integrantes
(marcado entre corchetes como sugerencia, ajusten según quién domine cada parte).

---

## 1. Portada — 0:00–0:20 [cualquiera abre]

> "Buenos días/tardes. Somos el equipo ONU-AMIGOS y venimos a presentar **StatCore GT**, un
> motor modular de inteligencia estadística confiable, para la Categoría 2 del Datatón INE
> 2026. Nuestro caso de aplicación: brechas de género y autonomía económica en Guatemala."

## 2. El problema — 0:20–0:55 [rol Datos/Estadística]

> "El punto de partida es simple: tener acceso a una base de datos del INE no garantiza
> usarla bien. Identificar variables, interpretar códigos especiales, aplicar el factor de
> expansión y respetar el dominio de estudio exige conocimiento técnico — y un error en
> cualquiera de esos pasos produce estimaciones engañosas.
>
> Pensamos esto para los analistas del INE, sobre todo de Análisis Estadístico y Muestreo,
> pero también sirve a investigadores, estudiantes y otras instituciones."

## 3. Nuestra propuesta — 0:55–1:30

> "StatCore GT no es un tablero estático. Calcula los indicadores desde los microdatos
> originales, no desde cifras ya hechas. Valida cada consulta antes de calcularla — si el
> diseño muestral no la permite, la bloquea. Y documenta la procedencia de cada resultado:
> fuente, fórmula, fecha de descarga, filtros y advertencias.
>
> La inteligencia artificial es opcional ahí, y nunca sustituye el cálculo estadístico."

## 4. Arquitectura — 1:30–2:10 [rol Integración]

> "La herramienta tiene cuatro componentes en un solo flujo: los datos pasan por
> **DataGuard**, que valida estructura, códigos especiales, rangos y ponderadores; luego por
> **StatEngine**, que calcula los tres indicadores ponderados por sexo y dominio; después por
> **StatShield**, que bloquea cruces no permitidos y advierte cuando el tamaño muestral es
> bajo; y llegan a la interfaz en Streamlit. **StatAI** es opcional: un catálogo cerrado de
> preguntas, sin modelo de lenguaje ni conexión a la nube."

## 5. Fuente de datos — 2:10–2:40 [rol Datos]

> "Usamos la ENEIC, la Encuesta Nacional de Empleo e Ingresos Continua del INE, edición I
> 2026. Trabajamos con variables ya confirmadas en el diccionario oficial: el ponderador
> FACTOR, el dominio de estudio, el sexo, y las variables de PEA, PET, ocupados,
> desocupados e ingreso laboral. Registramos la fuente y la fecha de descarga en cada
> resultado que exportamos."

## 6. Indicadores — 2:40–3:20 [rol Estadística]

> "Calculamos tres indicadores. Uno: participación laboral, PEA sobre PET, ponderado. Dos:
> ingreso laboral medio, el promedio ponderado del ingreso de la población ocupada con
> ingreso válido. Tres: la brecha relativa de ingreso entre hombres y mujeres — y aquí somos
> explícitos: es una medida descriptiva, no una estimación causal de discriminación."

## 7. Demo — funcionalidad — 3:20–4:20 [rol Web, demo en vivo]

> "Vamos a mostrarles la herramienta funcionando. Esto es el Explorador: elijo
> participación laboral, la desagrego por sexo y dominio... y así se genera la tabla, el
> gráfico, y puedo exportar el resultado con su ficha metodológica completa en un clic."

*(Cambiar a la app real en este punto, o mostrar la captura si no hay conexión. Un minuto
completo porque es la parte más importante: Funcionalidad vale 25% de la nota.)*

## 8. Demo — DataGuard y StatShield — 4:20–5:20 [rol Datos/Integración, demo en vivo]

> "Antes de calcular nada, DataGuard revisó la base: estructura, ponderador, códigos
> especiales, rangos. Y si yo pido algo que el diseño muestral no permite — por ejemplo,
> desagregar por municipio — StatShield lo bloquea y explica por qué, en vez de darme un
> número que parece válido pero no lo es."

## 9. Rigor de datos — 5:20–6:00 [rol Estadística]

> "Esto no se quedó en la teoría: lo validamos contra el informe oficial del INE. La tasa de
> participación laboral que calcula StatCore GT coincide con la publicada por el INE en los
> cuatro dominios de estudio, redondeando a dos decimales — nacional, urbano metropolitano,
> resto urbano y rural nacional."

*(Señalar la tabla en pantalla mientras se dice esto.)*

## 10. Limitaciones — 6:00–6:30

> "Somos honestos sobre los límites: no calculamos intervalos de confianza todavía, la
> brecha de ingreso es descriptiva y no controla por horas trabajadas u ocupación, y solo
> tenemos un trimestre validado oficialmente. Ediciones nuevas de la encuesta se marcan como
> exploratorias hasta que las validemos."

## 11. Cumplimiento — 6:30–6:50

> "Todo corre localmente, sin servicios de pago ni de nube. Respetamos el secreto
> estadístico: no identificamos personas, hogares ni empresas. Y declaramos el uso de un
> asistente de código con IA generativa durante el desarrollo, como pide el lineamiento."

## 12. Cierre — 6:50–7:00

> "El repositorio es público, con 82 pruebas automatizadas y una instalación reproducible.
> Gracias — quedamos atentos a sus preguntas."

---

## Para los 3 minutos de preguntas

Preparar respuesta corta para:
- **¿Por qué la brecha de ingreso no es causal?** → no controla variables como horas,
  ocupación o escolaridad; es una comparación descriptiva de medias.
- **¿Qué pasa si suben una edición de ENEIC distinta?** → se detecta automáticamente el
  período; si no coincide con un perfil validado, se marca como "exploratorio" y se limitan
  los cálculos hasta validarla.
- **¿Por qué no calculan intervalos de confianza?** → requiere el diseño muestral completo
  (estratos, conglomerados); quedó declarado como limitación y mejora futura.
- **¿Usaron IA para programar?** → sí, un asistente de código con IA generativa, declarado en
  el README; el equipo puede explicar y defender todo el código.
