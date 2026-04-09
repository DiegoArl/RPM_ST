import streamlit as st
import pandas as pd
import io
import requests
import plotly.graph_objects as go
 
from utils.dashboard_utils import (
    calcular_metricas,
    calcular_totales_cluster,
    calcular_kpis_globales,
    agregar_totales,
)
 
st.set_page_config(page_title="Dashboard Materiales", layout="wide")

FILE = st.secrets["FILE_ID"]
DATA_URL = f"https://docs.google.com/spreadsheets/d/{FILE}/export?format=xlsx"


@st.cache_data(show_spinner="Cargando datos…", ttl=None)
def cargar_datos(url: str) -> pd.DataFrame:
    response = requests.get(url)
    response.raise_for_status()
    contenido = io.BytesIO(response.content)
    if url.split("?")[0].endswith(".csv"):
        return pd.read_csv(contenido)
    return pd.read_excel(contenido, engine="openpyxl")
 
if st.button("Refresh datos"):
    st.cache_data.clear()
    st.rerun()
 
try:
    df_raw = cargar_datos(DATA_URL)
except Exception as e:
    st.error(f"No se pudo cargar el archivo: {e}")
    st.stop()
 
periodos = sorted(df_raw["Periodo"].dropna().unique(), reverse=True)
canales = sorted(df_raw["Canal"].dropna().unique())
clusters = ["All"] + sorted(df_raw["cluster"].dropna().unique())
regiones = ["All"] + sorted(df_raw["Region"].dropna().unique())
 
for key, default in [
    ("periodo_sel", periodos[1]),
    ("canal_sel", canales[1]),
    ("cluster_sel", []),
    ("region_sel", []),
    ("codigo_sel", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("Avance Materiales")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    st.session_state["periodo_sel"] = st.radio(
        "Periodo", periodos,
        index=periodos.index(st.session_state["periodo_sel"]),
    )
with col_f2:
    st.session_state["canal_sel"] = st.radio(
        "Canal", canales,
        index=canales.index(st.session_state["canal_sel"]),
    )
with col_f3:
    st.session_state["cluster_sel"] = st.multiselect(
        "Cluster", sorted(df_raw["cluster"].dropna().unique()),
        default=st.session_state["cluster_sel"] if isinstance(st.session_state["cluster_sel"], list) else [],
    )
with col_f4:
    st.session_state["region_sel"] = st.multiselect(
        "Región", sorted(df_raw["Region"].dropna().unique()),
        default=st.session_state["region_sel"] if isinstance(st.session_state["region_sel"], list) else [],
    )

periodo_sel = st.session_state["periodo_sel"]
canal_sel = st.session_state["canal_sel"]
cluster_sel = st.session_state["cluster_sel"]
region_sel = st.session_state["region_sel"]

df_pre = df_raw[
    (df_raw["Periodo"] == periodo_sel) &
    (df_raw["Canal"] == canal_sel)
].copy()
if cluster_sel:
    df_pre = df_pre[df_pre["cluster"].isin(cluster_sel)]
if region_sel:
    df_pre = df_pre[df_pre["Region"].isin(region_sel)]

mapa_materiales = (
    df_pre[df_pre["Nombre Material"].notna() & (df_pre["Nombre Material"].str.strip() != "")]
    [["Código Material", "Nombre Material"]]
    .drop_duplicates()
    .sort_values("Nombre Material")
)
opciones_materiales = ["All"] + mapa_materiales["Nombre Material"].tolist()

if isinstance(st.session_state["codigo_sel"], list):
    st.session_state["codigo_sel"] = [m for m in st.session_state["codigo_sel"] if m in mapa_materiales["Nombre Material"].tolist()]

st.session_state["codigo_sel"] = st.multiselect(
    "Nombre Material",
    mapa_materiales["Nombre Material"].tolist(),
    default=st.session_state["codigo_sel"] if isinstance(st.session_state["codigo_sel"], list) else [],
)

df = df_pre.copy()
if st.session_state["codigo_sel"]:
    codigos = mapa_materiales[mapa_materiales["Nombre Material"].isin(st.session_state["codigo_sel"])]["Código Material"].tolist()
    df = df[df["Código Material"].isin(codigos)]
 
df = df_pre.copy()
if st.session_state["codigo_sel"] and st.session_state["codigo_sel"] != "All":
    codigos = mapa_materiales[mapa_materiales["Nombre Material"].isin(
        st.session_state["codigo_sel"] if isinstance(st.session_state["codigo_sel"], list)
        else [st.session_state["codigo_sel"]]
    )]["Código Material"].tolist()
    df = df[df["Código Material"].isin(codigos)]
 
if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()
 
df_metricas = calcular_metricas(df)
kpis = calcular_kpis_globales(df_metricas)
cluster_counts = calcular_totales_cluster(df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total entregado", f"{int(kpis['Entregado']):,}")
k2.metric("Codificado real", f"{int(kpis['Codificado_Real']):,}")
k3.metric("% Avance real", f"{kpis['%Avance Real']*100:.2f}%")
k4.metric("% Avance teórico", f"{kpis['%Avance Teorico']*100:.2f}%")
 
st.divider()
 
col_donut, col_barras = st.columns(2)
 
COLORES_CLUSTER = {
    "C": "#378ADD",
    "A": "#85B7EB",
    "B+": "#7F77DD",
    "B-": "#AFA9EC",
}
 
with col_donut:
    st.subheader("Materiales codificados por cluster")
    total_clientes = sum(cluster_counts.values())
    labels = list(cluster_counts.keys())
    values = list(cluster_counts.values())
    colors = [COLORES_CLUSTER.get(l, "#888780") for l in labels]
    text_labels = [f"{v:,}\n({v/total_clientes*100:.1f}%)" if total_clientes > 0 else "0" for v in values]
 
    fig_donut = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        text=text_labels,
        textinfo="text",
        textposition="outside",
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        marker=dict(colors=colors, line=dict(width=0)),
        showlegend=True,
    ))
    fig_donut.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8A8A8A"),
        legend=dict(
            orientation="v",
            x=1.02, y=0.5,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig_donut, width="stretch")
 
with col_barras:
    st.subheader("Total entregado vs codificado")
 
    avance_real = kpis["%Avance Real"]
    avance_teo = kpis["%Avance Teorico"]
 
    tramo_real = avance_real * 100
    tramo_teo = max((avance_teo - avance_real) * 100, 0)
    tramo_resto = max(100 - avance_teo * 100, 0)
 
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Avance real",
        x=[tramo_real], y=[""],
        orientation="h",
        marker_color="#378ADD",
        hovertemplate=f"Avance real: {avance_real*100:.2f}%<extra></extra>",
        text=f"{avance_real*100:.2f}%",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
    ))
    fig_bar.add_trace(go.Bar(
        name="Brecha teórica",
        x=[tramo_teo], y=[""],
        orientation="h",
        marker_color="#7F77DD",
        hovertemplate=f"Avance teórico: {avance_teo*100:.2f}%<extra></extra>",
        text=f"{avance_teo*100:.2f}%" if tramo_teo > 2 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=13),
    ))
    fig_bar.add_trace(go.Bar(
        name="Pendiente",
        x=[tramo_resto], y=[""],
        orientation="h",
        marker_color="#D3D1C7",
        hovertemplate=f"Pendiente: {tramo_resto:.2f}%<extra></extra>",
        showlegend=True,
    ))
    fig_bar.update_layout(
        barmode="stack",
        height=120,
        margin=dict(t=10, b=40, l=0, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8A8A8A"),
        xaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            showgrid=False,
            zeroline=False,
            color="#8A8A8A",
        ),
        yaxis=dict(showticklabels=False, showgrid=False),
        legend=dict(
            orientation="h",
            x=0, y=-0.6,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
    )
    st.plotly_chart(fig_bar, width="stretch")
 
st.divider()
 
st.subheader("Detalle por región y DT")
 
df_metricas_canal = df_metricas[df_metricas["Canal"] == canal_sel].copy()
df_tabla = agregar_totales(df_metricas_canal)
 
subtotal_mask = df_tabla["_subtotal"].fillna(False).astype(bool)
df_display = df_tabla.drop(columns=["Canal", "Periodo", "_subtotal"]).copy()
 
for col in ["%Avance Real", "%Avance Teorico"]:
    df_display[col] = df_display[col].apply(
        lambda x: f"{float(x)*100:.2f}%" if pd.notna(x) and x != "" else ""
    )
 
for col in ["TOP", "A", "B+", "B-", "C", "Entregado", "Codificado_Real", "Codificado_OK"]:
    df_display[col] = df_display[col].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) and x != "" and x is not None else ""
    )
 
def estilo_filas(row):
    idx = row.name
    if subtotal_mask.iloc[idx]:
        return ["font-weight: 500"] * len(row)
    return [""] * len(row)
 
st.dataframe(
    df_display.style.apply(estilo_filas, axis=1),
    width="stretch",
    hide_index=True,
)