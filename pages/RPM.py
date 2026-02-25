import streamlit as st
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo, leer_archivo_rpm
from Scripts.activos import procesar_activos, procesar_ventas, procesar_flujo_RPM

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


archivo_ventas = st.file_uploader(
    "Subir Ventas y Coberturas",
    type=["csv", "xlsx"]
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
    type=["csv", "xlsx"]
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
    df_activos = procesar_activos(df_AF, df_Cartera)
except Exception as e:
    st.exception(e)
    st.stop()

if df_activos.empty:
    st.warning("No se generaron activos")
    st.stop()

try:
    df_RPM = procesar_flujo_RPM(df_activos, df_out)
except Exception as e:
    st.exception(e)
    st.stop()

st.subheader("BASE RPM (Sin Fórmulas)")
st.write(f"Filas: {df_RPM.shape[0]} | Columnas: {df_RPM.shape[1]}")
st.dataframe(df_RPM)

st.download_button(
    label="Descargar Excel",
    data=exportar_excel(df_RPM),
    file_name="RPM_final.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)