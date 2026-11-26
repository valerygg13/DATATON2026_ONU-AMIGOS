"""Carga temporal de archivos compatibles con ENEIC, sin caché compartida."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
from src.dataguard.validators import cargar_base
from src.pipeline import preparar_base, BaseNoValida

MAX_BYTES = 50 * 1024**2

def preparar_archivo(nombre, contenido, variables, reglas):
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
    periodo = variables['fuente']['periodo']
    for columna, esperado in periodo.items():
        if columna in df.columns:
            valores = pd.to_numeric(df[columna], errors='coerce')

            if not valores.eq(esperado).all():
                detectados = valores.dropna().unique().tolist()

                raise BaseNoValida(
                    f'{columna}: valores detectados {detectados}. '
                    f'Valor esperado: {esperado}. '
                    f'Perfil configurado: ENEIC '
                    f'{variables["fuente"]["edicion"]}.'
                )
    return preparar_base(df, variables, reglas)


def huella(contenido):
    return sha256(contenido).hexdigest()
