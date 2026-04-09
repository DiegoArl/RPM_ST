import pandas as pd
 
 
def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["cod_ok"] = df.apply(lambda r: r["Codificado"] if r["COK"] == 1 else 0, axis=1)
 
    entregado_unico = (
        df[["Region", "DT", "Canal", "Periodo", "Codigo", "Entregado"]]
        .drop_duplicates()
    )
    entregado_por_grupo = (
        entregado_unico.groupby(["Region", "DT", "Canal", "Periodo"])["Entregado"]
        .sum()
        .reset_index()
        .rename(columns={"Entregado": "Entregado_Sum"})
    )
 
    cluster_pivot = (
        df.groupby(["Region", "DT", "Canal", "Periodo", "cluster"])
        .agg(clientes=("llave_cliente", "nunique"))
        .reset_index()
        .pivot_table(
            index=["Region", "DT", "Canal", "Periodo"],
            columns="cluster",
            values="clientes",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    cluster_pivot.columns.name = None
    for col in ["A", "B+", "B-", "C"]:
        if col not in cluster_pivot.columns:
            cluster_pivot[col] = 0
    cluster_pivot["TOP"] = cluster_pivot[["A", "B+", "B-", "C"]].sum(axis=1)
 
    cod_metricas = (
        df.groupby(["Region", "DT", "Canal", "Periodo"])
        .agg(
            Codificado_Real=("Codificado", "sum"),
            Codificado_OK=("cod_ok", "sum"),
        )
        .reset_index()
    )
 
    resultado = (
        cluster_pivot
        .merge(cod_metricas, on=["Region", "DT", "Canal", "Periodo"], how="left")
        .merge(entregado_por_grupo, on=["Region", "DT", "Canal", "Periodo"], how="left")
    )
    resultado.rename(columns={"Entregado_Sum": "Entregado"}, inplace=True)
    resultado["%Avance Real"] = resultado.apply(
        lambda r: r["Codificado_Real"] / r["Entregado"] if r["Entregado"] > 0 else 0, axis=1
    )
    resultado["%Avance Teorico"] = resultado.apply(
        lambda r: r["Codificado_OK"] / r["Entregado"] if r["Entregado"] > 0 else 0, axis=1
    )
 
    col_order = [
        "Region", "DT", "Canal", "Periodo",
        "TOP", "A", "B+", "B-", "C",
        "Entregado", "Codificado_Real", "%Avance Real",
        "Codificado_OK", "%Avance Teorico",
    ]
    return resultado[col_order]
 
 
def calcular_totales_cluster(df: pd.DataFrame) -> dict:
    return (
        df.drop_duplicates(subset=["llave_cliente", "cluster"])
        .groupby("cluster")["llave_cliente"]
        .count()
        .to_dict()
    )
 
 
def calcular_kpis_globales(df_metricas: pd.DataFrame) -> dict:
    total_entregado = df_metricas["Entregado"].sum()
    total_cod_real = df_metricas["Codificado_Real"].sum()
    total_cod_ok = df_metricas["Codificado_OK"].sum()
    return {
        "Entregado": total_entregado,
        "Codificado_Real": total_cod_real,
        "Codificado_OK": total_cod_ok,
        "%Avance Real": total_cod_real / total_entregado if total_entregado > 0 else 0,
        "%Avance Teorico": total_cod_ok / total_entregado if total_entregado > 0 else 0,
    }
 
 
def agregar_totales(df: pd.DataFrame) -> pd.DataFrame:
    num_cols = ["TOP", "A", "B+", "B-", "C", "Entregado", "Codificado_Real", "Codificado_OK"]
    filas = []
 
    for region, grupo in df.groupby("Region", sort=False):
        grupo = grupo.copy()
        grupo["_subtotal"] = False
        filas.append(grupo)
 
        sub = grupo[num_cols].sum()
        sub_row = {c: None for c in df.columns}
        sub_row.update(sub.to_dict())
        sub_row["Region"] = region
        sub_row["DT"] = "Total"
        sub_row["%Avance Real"] = sub["Codificado_Real"] / sub["Entregado"] if sub["Entregado"] > 0 else 0
        sub_row["%Avance Teorico"] = sub["Codificado_OK"] / sub["Entregado"] if sub["Entregado"] > 0 else 0
        sub_row["_subtotal"] = True
        filas.append(pd.DataFrame([sub_row]))
 
    resultado = pd.concat(filas, ignore_index=True)
 
    grand = df[num_cols].sum()
    grand_row = {c: None for c in resultado.columns}
    grand_row.update(grand.to_dict())
    grand_row["Region"] = "Total general"
    grand_row["DT"] = ""
    grand_row["%Avance Real"] = grand["Codificado_Real"] / grand["Entregado"] if grand["Entregado"] > 0 else 0
    grand_row["%Avance Teorico"] = grand["Codificado_OK"] / grand["Entregado"] if grand["Entregado"] > 0 else 0
    grand_row["_subtotal"] = True
    resultado = pd.concat([resultado, pd.DataFrame([grand_row])], ignore_index=True)
 
    return resultado
