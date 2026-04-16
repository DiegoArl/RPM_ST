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
    df_ambulatorio = pivot_fechas(df_cod_ambulatorio)
    df_horizontal["Canal"] = "HORIZONTAL"
    df_ambulatorio["Canal"] = "AMBULATORIO"
    df_so = pd.concat([df_horizontal, df_ambulatorio])
    return df_so

def separar_cluster_material(df_material):
    df = df_material.copy()

    codigos_exp = (
        df
        .assign(cluster=df["cluster"].str.split(","))
        .explode("cluster")
    )
    return codigos_exp, df

def agregar_periodo_y_cok(df_so, df_material_fecha, df_material_cok):
    df = df_so.copy()
    df_per = df_material_fecha.copy()
    df_cok = df_material_cok.copy()

    for _df in [df, df_per, df_cok]:
        _df['Código Material'] = _df['Código Material'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

    df_per = df_per[['Canal', 'Código Material', 'Periodo', 'Fecha Inicio', 'Fecha Fin']]

    df = df.merge(df_per, on=['Canal', 'Código Material'], how='left')

    mask_rango = (
        df['Fecha Inicio'].isna() |
        (
            (df['Fecha'] >= df['Fecha Inicio']) &
            (df['Fecha'] <= df['Fecha Fin'])
        )
    )

    df = df[mask_rango].drop(columns=['Fecha Inicio', 'Fecha Fin'])

    df_cok_keys = df_cok[['Código Material', 'cluster', 'Periodo']].drop_duplicates()
    df_cok_keys['COK'] = 1

    df = df.merge(df_cok_keys, on=['Código Material', 'cluster', 'Periodo'], how='left').fillna(0)
    df['COK'] = df['COK'].astype(int)

    return df

def cuota_materiales(df_cuota_amb, df_cuota_hor, df_region, df_material):
    encabezado = [
        'DT_',
        'Periodo',
        'Codigo',
        'Entregado'
        ]
    df_amb = df_cuota_amb[encabezado].copy()
    df_hor = df_cuota_hor[encabezado].copy()
    df_region = df_region.copy()

    df_amb["Canal"] = "AMBULATORIO"
    df_hor["Canal"] = "HORIZONTAL"

    df_cuota = pd.concat([df_amb, df_hor]).fillna(0)

    df_cuota_fecha = df_cuota.merge(
        df_material[['Código Material', 'Periodo', 'Fecha Inicio', 'Fecha Fin']].drop_duplicates(),
        left_on=['Codigo', 'Periodo'],
        right_on=['Código Material', 'Periodo'],
        how='left'
    ).drop(columns=['Código Material'])

    df_entregado = df_cuota_fecha.merge(
        df_region,
        on="DT_",
        how="left"
    ).groupby(
        ["DT", "Region","Canal", "Periodo", "Codigo", "Fecha Inicio", "Fecha Fin"],
        as_index=False
    )["Entregado"].sum()

    return df_entregado

def agregar_dummies_faltantes(df_final, df_entregado):
    # ---------------------------------------------------------------
    # 1. Expandir df_entregado: una fila por mes (día 1) del rango
    # ---------------------------------------------------------------
    filas_expandidas = []
    for _, row in df_entregado.iterrows():
        meses = pd.date_range(
            start=pd.to_datetime(row['Fecha Inicio']).replace(day=1),
            end=pd.to_datetime(row['Fecha Fin']).replace(day=1),
            freq='MS'
        )
        for fecha in meses:
            filas_expandidas.append({
                'DT':        row['DT'],
                'Canal':     row['Canal'],
                'Codigo':    row['Codigo'],
                'Periodo':   row['Periodo'],
                'Region':    row['Region'],
                'Entregado': row['Entregado'],
                'Fecha':     fecha,   # día 1 del mes, solo para cruce
            })

    esperadas = pd.DataFrame(filas_expandidas)

    if esperadas.empty:
        return df_final

    # ---------------------------------------------------------------
    # 2. Crear columna de cruce en df_final (día 1) sin tocar original
    # ---------------------------------------------------------------
    existentes = df_final[['DT', 'Canal', 'Codigo', 'Periodo', 'Fecha']].copy()
    existentes['Fecha_cruce'] = pd.to_datetime(existentes['Fecha']).dt.to_period('M').dt.to_timestamp()
    existentes = existentes.drop_duplicates(subset=['DT', 'Canal', 'Codigo', 'Periodo', 'Fecha_cruce'])

    # Renombrar para hacer el merge por Fecha_cruce
    esperadas['Fecha_cruce'] = esperadas['Fecha']

    # ---------------------------------------------------------------
    # 3. Detectar combinaciones faltantes
    # ---------------------------------------------------------------
    faltantes = esperadas.merge(
        existentes[['DT', 'Canal', 'Codigo', 'Periodo', 'Fecha_cruce']],
        on=['DT', 'Canal', 'Codigo', 'Periodo', 'Fecha_cruce'],
        how='left',
        indicator=True
    )
    faltantes = faltantes[faltantes['_merge'] == 'left_only'].drop(columns=['_merge', 'Fecha_cruce'])
    # 'Fecha' aquí sigue siendo día 1 — es el valor que va en el dummy
    # (no hay fecha real que preservar porque el registro no existe)

    if faltantes.empty:
        return df_final

    # ---------------------------------------------------------------
    # 4. Construir dummies
    # ---------------------------------------------------------------
    n = len(faltantes)
    dummies = pd.DataFrame(index=range(n))

    dummies['llave_cliente']      = pd.NA
    dummies['Nombre Region']      = faltantes['Region'].values
    dummies['Nombre Cliente HML'] = faltantes['DT'].values
    dummies['Código Material']    = faltantes['Codigo'].values
    dummies['Nombre Material']    = pd.NA
    dummies['nom_vendedor']       = pd.NA
    dummies['cluster']            = pd.NA
    dummies['Fecha']              = faltantes['Fecha'].values
    dummies['Codificado']         = 0
    dummies['Canal']              = faltantes['Canal'].values
    dummies['Periodo']            = faltantes['Periodo'].values
    dummies['COK']                = 0
    dummies['DT']                 = faltantes['DT'].values
    dummies['Region']             = faltantes['Region'].values
    dummies['Codigo']             = faltantes['Codigo'].values
    dummies['Entregado']          = faltantes['Entregado'].values

    return pd.concat([df_final, dummies], ignore_index=True)

def procesar_flujo_materiales_datanest(archivo_dnm, archivo_mat):
    dfs = archivo_dnm.copy()
    dfm = archivo_mat.copy()
    df_so = concat_codificacion(dfs['df_so_hor'], dfs['df_so_amb'])

    df_material_cok, df_material_fecha = separar_cluster_material(dfm['df_materiales'])
    df_periodo = agregar_periodo_y_cok(df_so, df_material_fecha, df_material_cok)

    df_entregado = cuota_materiales(dfm['df_cuota_amb'], dfm['df_cuota_hor'], dfm['df_region'], dfm['df_materiales'])

    df_entregado["Codigo"] = df_entregado["Codigo"].astype(str)
    df_final = df_periodo.merge(
        df_entregado[["DT","Periodo","Codigo", "Canal", "Entregado"]],
        left_on=["Nombre Cliente HML", "Periodo", "Código Material", "Canal"],
        right_on=["DT","Periodo","Codigo", "Canal"],
        how="inner"
    )

    df_final2 = agregar_dummies_faltantes(df_final, df_entregado)
    return df_final2