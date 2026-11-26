"""Carga temporal de archivos compatibles con ENEIC, sin caché compartida."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
import numpy as np
from src.dataguard.validators import cargar_base
from src.pipeline import preparar_base, BaseNoValida

MAX_BYTES = 50 * 1024**2

def preparar_archivo(nombre, contenido, variables, reglas, *, multiperiodo=False):
    ext = Path(nombre).suffix.lower()
    if ext not in {'.sav', '.csv', '.xlsx'}:
        raise BaseNoValida('Formato no permitido.')
    if not contenido or len(contenido) > MAX_BYTES:
        raise BaseNoValida('Archivo vacío o superior a 50 MB.')
    if ext == '.xlsx':
        with ZipFile(BytesIO(contenido)) as z:
            if sum(i.file_size for i in z.infolist()) > 200 * 1024**2:
                raise BaseNoValida('Excel demasiado grande al descomprimir.')
    with TemporaryDirectory(prefix='statcore_') as carpeta:
        ruta = Path(carpeta) / ('base' + ext)
        ruta.write_bytes(contenido)
        df = cargar_base(ruta)
    if df.empty:
        raise BaseNoValida('La base no contiene registros.')
    # Exigir esquema completo para no omitir controles por columnas ausentes.
    faltantes = set(variables['base_personas'].values()) - set(df.columns)
    if faltantes:
        raise BaseNoValida('Variables ausentes: ' + ', '.join(sorted(faltantes)))
    for columna in variables['base_personas'].values():
        serie = df[columna]
        numerica = pd.to_numeric(serie, errors='coerce')
        if (serie.notna() & numerica.isna()).any():
            raise BaseNoValida(f'La variable {columna} contiene valores no numéricos.')
        df[columna] = numerica
    if multiperiodo:
        from src.perfiles import detectar_perfil
        variables, perfil = detectar_perfil(df, variables)
    else:
        for columna, esperado in variables['fuente']['periodo'].items():
            if columna in df.columns and not pd.to_numeric(df[columna], errors='coerce').eq(esperado).all():
                raise BaseNoValida(f'{columna} no coincide con el perfil configurado.')
    preparado, incidencias = preparar_base(df, variables, reglas)
    if multiperiodo:
        if perfil['estado'] == 'experimental_automatico':
            m = variables['base_personas']
            # En ediciones desconocidas exigimos códigos exactos, no solo rangos.
            for clave, permitidos in [('sexo', [1, 2]), ('dominio', [1, 2, 3]), ('area', [1, 2])]:
                if not df[m[clave]].isin(permitidos).all():
                    raise BaseNoValida(f'Edición nueva: códigos incompatibles o ausentes en {m[clave]}.')
            for columna in m.values():
                if np.isinf(df[columna].to_numpy(dtype=float)).any():
                    raise BaseNoValida(f'Edición nueva: valores infinitos en {columna}.')
            if incidencias:
                raise BaseNoValida('Edición nueva: requiere revisión de DataGuard. ' + '; '.join(incidencias))
            pet = df[m['pet']].eq(1)
            pea = df[m['pea']].eq(1)
            inactivos = df[m['inactivos']].eq(1)
            ocupados = df[m['ocupados']].eq(1)
            desocupados = df[m['desocupados']].eq(1)
            if not pet.any() or not pet.eq(pea | inactivos).all() or not pea.eq(ocupados | desocupados).all():
                raise BaseNoValida('Edición nueva: clasificación laboral incompleta o incompatible.')
        return preparado, incidencias, variables, perfil
    return preparado, incidencias


def huella(contenido):
    return sha256(contenido).hexdigest()
