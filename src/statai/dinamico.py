"""Gramática composicional conservadora: consume la pregunta completa."""
import re
import numpy as np

SEXO = {'hombre':'Hombre','hombres':'Hombre','masculina':'Hombre','masculino':'Hombre',
        'mujer':'Mujer','mujeres':'Mujer','femenina':'Mujer','femenino':'Mujer'}
ZONAS = {'rural':('area','Rural'), 'urbana':('area','Urbana'), 'urbano':('area','Urbana'),
         'rural nacional':('dominio','Rural Nacional'), 'resto urbano':('dominio','Resto Urbano'),
         'urbano metropolitano':('dominio','Urbano Metropolitano')}
ZONA = '|'.join(sorted(ZONAS,key=len,reverse=True))
GRUPO = r'(?:(?:de |para )?(?:los |las |el |la )?)?(?P<sexo>hombres|hombre|mujeres|mujer|masculina|masculino|femenina|femenino)'


def resolver_dinamica(q):
    # Primero, extraer un sufijo geográfico reconocido. No descartar texto sobrante.
    filtros = {}
    m = re.search(r' (?:en (?:el |la )?|del |de la |de el )(?:(area|dominio|zona) )?('+ZONA+r')$',q)
    if m:
        dim,val = ZONAS[m[2]]
        if m[1] in ('area','dominio') and m[1] != dim:
            return None
        filtros[dim]=[val]; q=q[:m.start()]
        if q.endswith(' nacional'):
            return None
    elif q.endswith(' en guatemala'):
        q=q[:-len(' en guatemala')]
    elif q.endswith(' a nivel nacional'):
        q=q[:-len(' a nivel nacional')]
    def consulta(indicador, by, sexo=None, direccion=None):
        f={k:list(v) for k,v in filtros.items()}
        if sexo: f['sexo']=[sexo]
        nombre={'participacion':'Participación laboral (tasa sobre PET)','ingreso':'Ingreso laboral medio mensual','brecha':'Brecha relativa de ingresos'}[indicador]
        if direccion:
            sujeto,base,op=direccion
            nombre=f'Diferencia porcentual: {sujeto} respecto a {base} ({op}; signo negativo = sentido contrario)'
        detalle=', '.join(f'{k}: {v[0]}' for k,v in f.items()) or 'Nacional'
        return dict(id='dinamica_'+indicador,descripcion=f'{nombre} · {detalle}',indicador=indicador,by=by,filtros=f,alias=[],direccion=direccion)
    m=re.fullmatch(r'que porcentaje (mas|menos) ganan (?:los |las )?(hombres|mujeres) que (?:los |las )?(hombres|mujeres)',q)
    if m and m[2]!=m[3]:
        return consulta('brecha',[],direccion=(SEXO[m[2]],SEXO[m[3]],m[1]))
    for patron in [r'(?:cual es )?(?:la )?(?:tasa de )?participacion laboral '+GRUPO,
                   r'que porcentaje de (?:los |las )?(?P<sexo>hombres|mujeres) participa(?:n)? en el mercado laboral',
                   r'cuantos? de cada 100 (?P<sexo>hombres|mujeres) participan en el mercado laboral',
                   r'cuantas de cada 100 (?P<sexo>mujeres) participan en el mercado laboral']:
        m=re.fullmatch(patron,q)
        if m: return consulta('participacion',['sexo'],SEXO[m['sexo']])
    for patron in [r'(?:cual es )?(?:el )?ingreso laboral (?:medio|promedio)(?: mensual)? '+GRUPO,
                   r'cuanto gana(?:n)?(?: en promedio)? (?:los |las |el |la )?(?P<sexo>hombres|mujeres|hombre|mujer)']:
        m=re.fullmatch(patron,q)
        if m: return consulta('ingreso',['sexo'],SEXO[m['sexo']])
    if re.fullmatch(r'(?:cual es )?(?:la )?(?:tasa de )?participacion laboral(?: nacional)?',q):
        return consulta('participacion',[])
    if re.fullmatch(r'(?:cual es )?(?:el )?ingreso laboral (?:medio|promedio)(?: mensual| nacional)?',q):
        return consulta('ingreso',[])
    if re.fullmatch(r'(?:cual es )?(?:la )?(?:tasa de )?participacion laboral por (?:sexo|genero)',q):
        return consulta('participacion',['sexo'])
    if re.fullmatch(r'(?:cual es )?(?:el )?ingreso laboral (?:medio|promedio) por (?:sexo|genero)',q):
        return consulta('ingreso',['sexo'])
    if re.fullmatch(r'(?:cual es )?(?:la )?brecha (?:de ingresos|de ingresos laborales)(?: entre hombres y mujeres)?',q):
        return consulta('brecha',[])
    return None


def aplicar_direccion(r, direccion):
    """Nunca recuperar una brecha suprimida. Denominador = grupo de referencia."""
    sujeto,base,op=direccion
    r=r.copy()
    cols={'Hombre':'media_hombres','Mujer':'media_mujeres'}
    a,b=r[cols[sujeto]],r[cols[base]]
    valido=r['valor'].notna() & np.isfinite(a) & np.isfinite(b) & (b>0)
    r['valor']=np.nan
    r.loc[valido,'valor']=100*(a[valido]-b[valido])/b[valido]*(1 if op=='mas' else -1)
    return r
