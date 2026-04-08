import pandas as pd
import numpy as np
import re

def pivot_fechas(df):
    df_p = df.copy()

    columnas_fijas = []
    for c in ['llave_cliente', 'Nombre Region', 'Nombre Cliente HML', 'Código Material', 'Nombre Material', 'nom_vendedor', 'cluster']:
        if c in df_p.columns:
            columnas_fijas.append(c)

    columnas_periodos = [
        c for c in df_p.columns
        if c not in columnas_fijas
        and re.fullmatch(r'\d{4}-\d{2}', str(c))
    ]

    for c in columnas_periodos:
        df_p[c] = pd.to_numeric(df_p[c], errors='coerce')

    df_long = df_p.melt(
        id_vars=columnas_fijas,
        value_vars=columnas_periodos,
        var_name='Fecha',
        value_name='Codificado'
    )

    cluster_lista = ['TOP', 'A', 'B+', 'B-', 'C']

    df_long['Fecha'] = pd.to_datetime(df_long['Fecha'], format='%Y-%m', errors='coerce')
    df_long['Fecha'] = df_long['Fecha'].dt.to_period('M').dt.to_timestamp()

    if 'cluster' in df_long.columns:
        df_long['cluster'] = df_long['cluster'].apply(lambda x: x if x in cluster_lista else 'C')

    cols_grp = columnas_fijas + ['Fecha']
    df_long = (
        df_long
        .groupby(cols_grp, as_index=False, dropna=False)
        .agg(Codificado=('Codificado', 'sum'))
    )
    return df_long

def concat_codificacion(df_cod_horizontal, df_cod_ambulatorio):
    df_horizontal = pivot_fechas(df_cod_horizontal)
    df_horizontal["Canal"] = "HORIZONTAL"
    df_ambulatorio = pivot_fechas(df_cod_ambulatorio)
    df_ambulatorio["Canal"] = "AMBULATORIO"
    df_so = pd.concat([df_horizontal, df_ambulatorio])
    return df_so

def procesar_flujo_materiales_datanest(archivo):
    dfs = archivo.copy()
    horizontal = dfs['df_so_hor']
    ambulatorio = dfs['df_so_amb']

    return horizontal, ambulatorio