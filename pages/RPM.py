import streamlit as st
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo, leer_archivo_rpm
from Scripts.activos import procesar_activos, procesar_ventas, procesar_flujo_RPM

st.header("RPM")

def archivos_rpm_cargados():
    requeridos = [
        "ventas_df",
        "AF",
        "Cartera"
    ]
    return all(k in st.session_state for k in requeridos)

archivo_ventas = st.file_uploader(
    "Subir Ventas y Coberturas",
    type=["csv", "xlsx"],
    key="ventas_file"
)

if archivo_ventas and "ventas_df" not in st.session_state:
    try:
        datos = leer_archivo_rpm(archivo_ventas)
        df_out = procesar_ventas(datos)

        if df_out.empty:
            st.error("El procesamiento de ventas no generó resultados")
            st.stop()

        st.session_state["ventas_df"] = df_out
        st.success("Ventas procesadas correctamente")

    except Exception as e:
        st.exception(e)
        st.stop()

archivo_AF = st.file_uploader(
    "Subir activos",
    type=["csv", "xlsx"]
)

if archivo_AF and "AF" not in st.session_state:
    try:
        st.session_state["AF"] = leer_archivo(archivo_AF)
        st.success("Activos cargados")
    except Exception as e:
        st.exception(e)

archivo_Cartera = st.file_uploader(
    "Subir cartera de clientes",
    type=["csv", "xlsx"],
    key="cartera_file"
)

if archivo_Cartera and "Cartera" not in st.session_state:
    try:
        st.session_state["Cartera"] = leer_archivo(archivo_Cartera)
        st.success("Cartera cargada")
    except Exception as e:
        st.exception(e)

if not archivos_rpm_cargados():
    st.warning("Faltan archivos por cargar")
    st.stop()

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
    df_RPM = procesar_flujo_RPM(
        df_activos,
        st.session_state["ventas_df"]
    )
except Exception as e:
    st.exception(e)
    st.stop()

st.subheader("BASE RPM (Sin Fórmulas)")
st.write(f"Filas: {df_RPM.shape[0]} | Columnas: {df_RPM.shape[1]}")

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


st.download_button(
    label="Descargar Excel",
    data=df_a_excel(df_RPM),
    file_name="RPM_final.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)