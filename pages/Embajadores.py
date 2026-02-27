import streamlit as st
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo_encuesta
from Scripts.encuesta import procesar_flujo_embajadores

st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.header("Encuesta Embajadores")

@st.cache_data
def cargar_archivo_encuesta_cached(archivo):
    return leer_archivo_encuesta(archivo)

@st.cache_data
def procesar_embajadores(df):
    return procesar_flujo_embajadores(df)

@st.cache_data
def generar_excel(df):
    return df_a_excel(df)

def limpiar_app():
    st.cache_data.clear()
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

archivo_embajadores = st.file_uploader(
    "Sube el excel con el archivo de embajadores (Ventas, Cuotas, Encuesta, Relacion, CambioRUC)",
    type=["xlsx"],
    key="embajadores_file"
)

if archivo_embajadores and "embajadores_df" not in st.session_state:

    try:

        datos = cargar_archivo_encuesta_cached(archivo_embajadores)
        st.session_state["embajadores_raw"] = datos

        df_final = procesar_embajadores(datos)

        if df_final is None or df_final.empty:
            st.error("El procesamiento no generó resultados")
            st.stop()

        st.session_state["embajadores_df"] = df_final
        st.session_state["embajadores_excel"] = generar_excel(df_final)

        st.success("Archivo procesado correctamente")

    except Exception as e:

        st.error("Error procesando el archivo")
        st.exception(e)
        st.stop()


if "embajadores_df" not in st.session_state:
    st.warning("No se ha cargado el archivo de embajadores")
    st.stop()


df_final = st.session_state["embajadores_df"]
excel_file = st.session_state["embajadores_excel"]


st.subheader("Archivo Embajadores")

st.write(
    f"Filas: {df_final.shape[0]} | Columnas: {df_final.shape[1]}"
)

st.dataframe(df_final.head())

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
        data=excel_file,
        file_name="Embajadores_Procesado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    if st.button("Reiniciar carga de archivos"):
        limpiar_app()