"""StatShield: bloqueo de cruces no permitidos, advertencias de tamaño muestral,
registro de definiciones usadas en cada resultado.

Lee los umbrales y desagregaciones permitidas/bloqueadas de config/reglas_calidad.yaml.
"""

from __future__ import annotations

import pandas as pd

MOTIVO_BLOQUEO = (
    "La consulta está fuera de las reglas configuradas para ENEIC. Revise el dominio de estudio "
    "y las dimensiones autorizadas (sexo, dominio y área). Su autorización no garantiza precisión muestral."
)


class DesagregacionNoAutorizada(Exception):
    """Se intentó una desagregación fuera del dominio de estudio permitido."""


def verificar_desagregacion(by: list[str], permitidas: list[str], bloqueadas: list[str]) -> None:
    """Lanza DesagregacionNoAutorizada si `by` incluye alguna dimensión bloqueada
    o no listada como permitida. El mensaje explica el motivo para mostrarlo al usuario."""
    for dim in by or []:
        if dim in bloqueadas:
            raise DesagregacionNoAutorizada(f"Desagregación por '{dim}' bloqueada. {MOTIVO_BLOQUEO}")
        if dim not in permitidas:
            raise DesagregacionNoAutorizada(
                f"Desagregación por '{dim}' no autorizada (permitidas: {', '.join(permitidas)}). {MOTIVO_BLOQUEO}"
            )


def advertencia_tamano_muestral(n_no_ponderado: int, minimo: int) -> str | None:
    """Devuelve un mensaje de advertencia si n_no_ponderado < minimo, o None si está OK."""
    if n_no_ponderado == 0:
        return "No hay casos elegibles; no existe una estimación calculable."
    if n_no_ponderado < minimo:
        return (
            f"Solo {n_no_ponderado} casos no ponderados (mínimo {minimo}): "
            "tamaño muestral reducido; interpretar con cautela. Precisión estadística no evaluada."
        )
    return None


def aplicar_statshield(
    resultado: pd.DataFrame, by: list[str] | None, reglas: dict, suprimir_bajo_minimo: bool = False
) -> pd.DataFrame:
    """Valida `by` y agrega la columna `advertencia` a la salida de StatEngine.

    Con `suprimir_bajo_minimo=True` (brecha de ingreso, ver docs/indicadores.md) el `valor`
    de las filas bajo el umbral se reemplaza por NaN en vez de solo advertir.
    """
    cruces = reglas["cruces"]
    verificar_desagregacion(by or [], cruces["desagregaciones_permitidas"], cruces["desagregaciones_bloqueadas"])
    minimo = cruces["minimo_casos_no_ponderados"]

    salida = resultado.copy()
    salida["advertencia"] = [advertencia_tamano_muestral(int(n), minimo) for n in salida["n_no_ponderado"]]
    if {"n_hombres", "n_mujeres"}.issubset(salida.columns):
        falta_grupo = (salida["n_hombres"] == 0) | (salida["n_mujeres"] == 0)
        salida.loc[falta_grupo, "advertencia"] = (
            "No es posible calcular la brecha porque falta uno de los grupos de comparación con ingresos elegibles."
        )
        invalida = ~falta_grupo & salida["valor"].isna() & salida["advertencia"].isna()
        salida.loc[invalida, "advertencia"] = "Brecha no calculable: revise las medias y el denominador."
    if suprimir_bajo_minimo:
        bajo = salida["n_no_ponderado"] < minimo
        salida.loc[bajo, "valor"] = float("nan")
        salida.loc[bajo, "advertencia"] += " Valor no publicado."
    return salida
