import streamlit as st

st.set_page_config(
    page_title= "Reportes",
    layout="wide"
)

st.title("Página principal")

st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

#st.switch_page("pages/Embajadores.py")

#pagina RPM (activos + cartera)
import streamlit as st
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo
from Scripts.activos import procesar_activos

st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.header("RPM - En construcción")


@st.cache_data
def cargar_archivo(archivo):
    return leer_archivo(archivo)


@st.cache_data
def procesar(df_AF, df_Cartera):
    return procesar_activos(df_AF, df_Cartera)


@st.cache_data
def exportar_excel(df):
    return df_a_excel(df)


archivo_AF = st.file_uploader(
    "Subir activos",
    type=["csv", "xlsx"]
)

if archivo_AF:
    try:
        st.session_state.AF = cargar_archivo(archivo_AF)
        st.success("Archivo subido correctamente")
    except Exception as e:
        st.error(str(e))

if "AF" not in st.session_state:
    st.warning("No se ha cargado la base de activos")
    st.stop()


archivo_Cartera = st.file_uploader(
    "Subir cartera de clientes",
    type=["csv", "xlsx"]
)

if archivo_Cartera:
    try:
        st.session_state.Cartera = cargar_archivo(archivo_Cartera)
        st.success("Cartera subida correctamente")
    except Exception as e:
        st.error(str(e))

if "Cartera" not in st.session_state:
    st.warning("No se ha cargado la cartera de clientes")
    st.stop()


df_AF = st.session_state["AF"]
df_Cartera = st.session_state["Cartera"]

try:
    df_out = procesar_activos(df_AF, df_Cartera)
except Exception as e:
    st.exception(e)
    st.stop()


if not df_out.empty:

    st.subheader("Base activos")
    st.write(f"Filas: {df_out.shape[0]} | Columnas: {df_out.shape[1]}")
    st.dataframe(df_out)

    st.download_button(
        label="Descargar Excel",
        data=exportar_excel(df_out),
        file_name="Archivo_prueba_RPM.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )