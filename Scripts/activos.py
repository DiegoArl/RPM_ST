import pandas as pd
from datetime import datetime

headers_cartera = [
    "NomCia",
    "nombre_cliente",
    "Categoria",
    "canal",
    "direccion",
    "estado_cliente",
    "clave"
    ]
Regiones_Agregar = {
    "DISIM":"LIMA",
    "DISMAC":"LIMA",
    "DISUMP":"LIMA",
    "KALLPA":"LIMA",
    "MJF":"LIMA",
    "SAGADIS":"LIMA",
    "NORDIGESA 2":"NORTE",
    "NORDIGESA 3":"NORTE",
    "NORDIGESA 1":"NORTE",
    "CODIJISA":"NORTE",
    "OPEN JUNGLE":"CENTROS",
    "RICO FRIO":"CENTROS",
    "BYV":"CENTROS",
    "CESAR":"CENTROS",
    "OCO":"CENTROS",
    "GRANOR'S":"CENTROS",
    "DISSO":"CENTROS",
    "GUMI":"CENTROS",
    "DIFRIMAR":"SUR",
    "DISUR 1":"SUR",
    "DISUR 2":"SUR",
    "ROMA 1":"SUR",
    "ROMA 2":"SUR",
    "DFRIO 1":"SUR",
    "DFRIO 2":"SUR"
}
Regiones_null = [
  "LIMA MODERNO",
  "DESTRUIDA",
  "NESTLE",
  "LIMA AMBULATORIO",
  "SSTT",
  "BAJA CONCILIACION 2022",
  "ST-PATIO FH-TUMBES",
  "ST-PATIO FH-LIMA CARAPONGO",
  "ST-PATIO FH-HUACHO",
  "ST-PATIO FH-CUSCO",
  "ST-PATIO FH-LIMA",
  "ST-PATIO FH-TRUJILLO",
  "#N/D",
  "MODERNO"
]
Tamano_AF = [
    "CUBETERA",
    "EXTRA GRANDE",
    "PISCINA",
    "DIANA TOP",
    "GRANDE",
    "MEDIANA",
    "CHICA",
    "CHECK OUT",
    "DIANA TOP(ARRIBA)",
    "VERTICAL",
    "Vertical"
]
Columnas = [
  "PLACA SISTEMA",
  "PLACA FÍSICA",
  "TAMAÑO",
  "TD RAF",
  "FECHA DE UBICACIÓN",
  "# MÁQ X PDV",
  "AÑO",
  "Edad",
  "REGION",
  "NomCia",
  "CLIENTE",
  "nombre_cliente",
  "Categoria",
  "canal",
  "direccion",
  "estado_cliente"
]
new_col = [
  "PLACA SISTEMA",
  "PLACA FÍSICA",
  "TAMAÑO",
  "STATUS AF",
  "FECHA DE UBICACIÓN(CENSO)",
  "# MÁQ X PDV",
  "Año",
  "Edad",
  "REGION",
  "DT FIN",
  "COD CLIENTE",
  "RAZON SOCIAL",
  "CLUSTER",
  "TIPO CANAL",
  "DIRECCIÓN",
  "PDV ACTIVO"
]
columnas_str = {
    "CLIENTE":str,
    "clave":str,
    "codcia":str,
    "codclte":str,
    "domic":str,
    "numero_pedido":str,
    "codigoproducto":str,
    "vendedor":str,
    "Cod Cliente":str,
    "Clave del Cliente (15 dígitos)":str
}

def agregar_ceros(df):
  columnas_longitud = {'empresa': 3, 'domicilio': 3, 'codigo_cliente':6, 'oficina':3}
  for columna, longitud in columnas_longitud.items():
      df[columna] = df[columna].astype(str).str.zfill(longitud)
  return df

def codigo_cliente(df_cartera, df_AF):

  mask = (df_AF["DT FIN"] == "GUMI") & (df_AF["CLIENTE"].str.len() == 14)
  df_AF.loc[mask, "CLIENTE"] = df_AF.loc[mask, "CLIENTE"].str.zfill(15)
  return df_cartera, df_AF

def cruzarAF_cartera(df, df_cartera):

  df = pd.merge(df, df_cartera[headers_cartera],
                left_on = "CLIENTE",
                right_on = "clave",
                how="left"
                )

  df_estado_not_null = df[
    (df['NomCia'].notna())&
    (df['TD RAF']!="PATIOS")
    ]

  df_estado_null = df[
    (df['TD RAF']=="PATIOS") &
    (df['CANAL']=="HORIZONTAL") &
    (~df['REGION'].isin(Regiones_null)) &
    (df['TAMAÑO'].str.upper().isin(Tamano_AF))
    ]

  df_estado_not_null = pd.concat([df_estado_not_null, df_estado_null])

  return df_estado_null, df_estado_not_null

def tamano_df(df):
  df = df[df["TAMAÑO"].str.upper().isin(Tamano_AF)]
  return df

def agregar_columnas_af(df):

    df = df.copy()
    df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
    año_actual = datetime.now().year

    df["Edad"] = año_actual - df["AÑO"]
    df["# MÁQ X PDV"] = (
        df.groupby("CLIENTE")["CLIENTE"].transform("count")
    )
    return df

def ordenar_columnas(df):
  df = df[Columnas]
  mapping = dict(zip(Columnas, new_col))
  df = df.rename(columns=mapping)
  return df

def bin_coberturas(df_Cobertura, columnas_fijas):
    df_Cobertura = df_Cobertura.copy().fillna(0)
    cols_to_transform = [col for col in df_Cobertura.columns if col not in columnas_fijas]

    for col in cols_to_transform:
        df_Cobertura[col] = df_Cobertura[col].apply(lambda x: 1 if x != 0 else 0)

    return df_Cobertura

def procesar_activos(df_AF, df_Cartera):
    df_Cartera, df_AF = codigo_cliente(df_Cartera.copy(), df_AF.copy())
    _, df_estado_not_null = cruzarAF_cartera(df_AF, df_Cartera)
    df_estado_not_null = ordenar_columnas(agregar_columnas_af(tamano_df(df_estado_not_null)))
    return df_estado_not_null    

def procesar_ventas(archivo):
    dfs = archivo.copy()
    columnas_fijas = ["Nombre Region", "Nombre Cliente HML", "llave_cliente"]
    drop_cols = ["Nombre Region", "Nombre Cliente HML"]
    df_Ventas = dfs['df_Ventas']
    df_Cobertura = bin_coberturas(dfs['df_Cobertura'], columnas_fijas)
    df_Cobertura = df_Cobertura.drop(columns=drop_cols, errors="ignore")

    columnas_periodos = [c for c in df_Ventas.columns if c not in columnas_fijas]

    df_long = df_Ventas.melt(
        id_vars=columnas_fijas,
        value_vars=columnas_periodos,
        var_name="Fecha",
        value_name="Valor"
    )
    df_long["Fecha"] = pd.to_datetime(df_long["Fecha"], errors="coerce")
    df_long = df_long[(df_long['llave_cliente'].notna()) & (df_long['Valor'].notna())]

    fecha_max = df_long["Fecha"].max()
    fecha_inicio = fecha_max - pd.DateOffset(months=13)
    df_12m = df_long[df_long["Fecha"].between(fecha_inicio, fecha_max)].copy()

    fecha_min_por_cliente = (
        df_12m.groupby("llave_cliente")['Fecha']
               .min()
               .reset_index(name='Fecha_minima')
    )
    df_12m = df_12m.merge(fecha_min_por_cliente, on='llave_cliente', how='left')

    df_wide = df_12m.pivot(
        index=["Nombre Region", "Nombre Cliente HML", "llave_cliente", "Fecha_minima"],
        columns="Fecha",
        values="Valor"
    )
    df_out = df_wide.reset_index().fillna(0)
   
    df_out["meses_diferencia"] = (
        (fecha_max.year - df_out["Fecha_minima"].dt.year) * 12 +
        (fecha_max.month - df_out["Fecha_minima"].dt.month)
    ) + 1

    return df_out.merge(
       df_Cobertura,
       on = "llave_cliente",
       how = 'left'
    ).drop(columns=drop_cols, errors='ignore')

def procesar_flujo_RPM(df_activos, df_out):
    df_RPM = df_activos.merge(
        df_out,
        left_on = "COD CLIENTE",
        right_on = "llave_cliente",
        how = "left"
    )   

    return df_RPM