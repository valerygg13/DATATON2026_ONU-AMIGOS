# Checklist de cumplimiento — Issue #20

Verificado el 2026-11-25 contra los lineamientos de la Nota Conceptual Datatón INE 2026
(Categoría 2).

| Requisito | Estado | Evidencia |
|---|---|---|
| Fuente principal: base pública de ine.gob.gt | ✅ | ENEIC I 2026, `data/README.md` |
| Fuente y fecha de descarga documentadas | ✅ | `config/variables.yaml` → `fuente`, y en cada ficha metodológica exportada |
| Repositorio Git desde el día 1 | ✅ | `Initial commit` del 2026-11-23 |
| Prototipo funcional demostrable | ✅ | `streamlit run app/app.py`, instrucciones en README |
| Reproducible (instalación + dependencias) | ✅ | `requirements.txt` + sección Setup del README |
| README con problema/usuarios, arquitectura, instalación, datasets, limitaciones | ✅ | README.md (issue #18) |
| Secreto estadístico (no identificar personas/hogares/empresas) | ✅ | Solo se trabaja con agregados ponderados; sin guardado permanente de archivos subidos (`src/fuentes.py`, directorio temporal) |
| Sin credenciales/llaves en el código | ✅ | Verificado con búsqueda de patrones (api_key, secret, password, token, claves privadas) — sin coincidencias |
| IA generativa: declarada si se usó | ✅ | README → "Cumplimiento": declarado uso de asistente de código con IA generativa durante el desarrollo |
| Servicios de pago/nube: declarados si se usaron | ✅ | README → "Cumplimiento": no se usan: StatAI es un emparejador local sin LLM ni llamadas externas |
| Uso correcto de la información (fiel a definiciones del INE) | ✅ | Fórmulas documentadas en `docs/indicadores.md`, validadas contra resultados oficiales en `docs/validacion_eneic.md` |
| Componentes de terceros y sus licencias listados | ✅ | Ver tabla abajo |
| Citar al INE como fuente de los datos | ✅ | README, `data/README.md`, ficha metodológica de cada exportación |

## Licencias de dependencias (`requirements.txt`)

| Paquete | Licencia |
|---|---|
| pandas | BSD-3-Clause |
| numpy | BSD-3-Clause |
| pyreadstat | Apache-2.0 |
| openpyxl | MIT |
| PyYAML | MIT |
| streamlit | Apache-2.0 |
| plotly | MIT |
| pytest | MIT |

Todas de código abierto, sin costo de licenciamiento. Se removió `duckdb` de
`requirements.txt`: estaba declarada pero no se usa en ningún módulo (el cálculo se hace
íntegramente con pandas/NumPy).

## Pendiente antes de la entrega (no bloqueante para este checklist)

- Issue #19: grabar el video demostrativo de 2-3 minutos (ver `docs/guion_video.md`).
