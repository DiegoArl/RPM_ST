import streamlit as st
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo, leer_archivo_rpm
from Scripts.activos import procesar_activos, procesar_ventas, procesar_flujo_RPM

st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.header("RPM")

@st.cache_data
def cargar_archivo(archivo):
    return leer_archivo(archivo)

@st.cache_data
def cargar_archivo_rpm_cached(archivo):
    return leer_archivo_rpm(archivo)

@st.cache_data
def exportar_excel(df):
    return df_a_excel(df)

@st.cache_data
def procesar_rpm_cache(df_activos, df_out):
    return procesar_flujo_RPM(df_activos, df_out)

def limpiar_app():
    st.cache_data.clear()
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

archivo_ventas = st.file_uploader(
    "Subir Ventas y Coberturas",
    type=["csv", "xlsx"],
    key="ventas_file"
)

if archivo_ventas:
    try:
        datos = cargar_archivo_rpm_cached(archivo_ventas)
        df_out = procesar_ventas(datos)

        if df_out.empty:
            st.error("El procesamiento de ventas no generó resultados")
            st.stop()

        st.session_state["ventas_df"] = df_out
        st.success("Ventas procesadas correctamente")

    except Exception as e:
        st.exception(e)
        st.stop()

if "ventas_df" not in st.session_state:
    st.warning("Cargar archivo de ventas")
    st.stop()

df_out = st.session_state["ventas_df"]


archivo_AF = st.file_uploader(
    "Subir activos",
    type=["csv", "xlsx"]
)

if archivo_AF:
    try:
        st.session_state["AF"] = cargar_archivo(archivo_AF)
        st.success("Activos cargados")
    except Exception as e:
        st.exception(e)

if "AF" not in st.session_state:
    st.warning("Cargar base de activos")
    st.stop()

archivo_Cartera = st.file_uploader(
    "Subir cartera de clientes",
    type=["csv", "xlsx"],
    key="cartera_file"
)

if archivo_Cartera:
    try:
        st.session_state["Cartera"] = cargar_archivo(archivo_Cartera)
        st.success("Cartera cargada")
    except Exception as e:
        st.exception(e)

if "Cartera" not in st.session_state:
    st.warning("Cargar cartera de clientes")
    st.stop()


df_AF = st.session_state["AF"]
df_Cartera = st.session_state["Cartera"]

try:
    df_activos = procesar_activos(
        st.session_state["AF"],
        st.session_state["Cartera"]
    )
except Exception as e:
    st.exception(e)
    st.stop()


if df_activos.empty:
    st.warning("No se generaron activos")
    st.stop()


try:
    df_RPM = procesar_rpm_cache(
        df_activos,
        st.session_state["ventas_df"]
    )
except Exception as e:
    st.exception(e)
    st.stop()

st.subheader("BASE RPM (Sin Fórmulas)")
st.write(f"Filas: {df_RPM.shape[0]} | Columnas: {df_RPM.shape[1]}")
st.dataframe(df_RPM)

st.markdown("""
<style>

/* Botón descargar (verde) */
div[data-testid="stDownloadButton"] button {
    background-color: #28a745;
    color: white;
    border: none;
}
div[data-testid="stDownloadButton"] button:hover {
    background-color: #218838;
}

/* Botón reiniciar (rojo) */
button[kind="secondary"] {
    background-color: #dc3545;
    color: white;
    border: none;
}
button[kind="secondary"]:hover {
    background-color: #c82333;
}

</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="Descargar Excel",
        data=exportar_excel(df_RPM),
        file_name="RPM_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    if st.button("Reiniciar carga de archivos"):
        limpiar_app()