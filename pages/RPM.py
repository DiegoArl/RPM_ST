import streamlit as st
from datetime import datetime
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo, leer_archivo_rpm
from Scripts.activos import procesar_activos, procesar_ventas, procesar_flujo_RPM

st.header("RPM")

def archivos_rpm_cargados():
    requeridos = ["ventas_raw", "AF", "Cartera"]
    return all(k in st.session_state for k in requeridos)

archivo_ventas = st.file_uploader(
    "Subir Ventas y Coberturas",
    type=["csv", "xlsx"],
    key="ventas_file"
)

if archivo_ventas:
    try:
        st.session_state["ventas_raw"] = leer_archivo_rpm(archivo_ventas)
        st.success("Archivo de ventas subido correctamente")
    except Exception as e:
        st.error(str(e))

archivo_AF = st.file_uploader(
    "Subir activos",
    type=["csv", "xlsx"],
    key="af_file"
)

if archivo_AF:
    try:
        st.session_state["AF"] = leer_archivo(archivo_AF)
        st.success("Activos cargados correctamente")
    except Exception as e:
        st.error(str(e))

archivo_Cartera = st.file_uploader(
    "Subir cartera de clientes",
    type=["csv", "xlsx"],
    key="cartera_file"
)

if archivo_Cartera:
    try:
        st.session_state["Cartera"] = leer_archivo(archivo_Cartera)
        st.success("Cartera cargada correctamente")
    except Exception as e:
        st.error(str(e))


listo = archivos_rpm_cargados()

if not listo:
    st.warning("Faltan archivos por cargar")

if st.button("Procesar archivos", disabled=not listo):
    try:
        df_ventas = procesar_ventas(st.session_state["ventas_raw"])
        if df_ventas.empty:
            st.error("El procesamiento de ventas no generó resultados.")
            st.stop()
        st.session_state["ventas_df"] = df_ventas
    except Exception as e:
        st.error("Error procesando ventas. Verifique el formato o cambie de archivo.")
        st.session_state.pop("ventas_raw", None)
        st.stop()

    try:
        df_activos = procesar_activos(st.session_state["AF"], st.session_state["Cartera"])
        if df_activos.empty:
            st.warning("No se generaron activos.")
            st.stop()
    except Exception as e:
        st.error("Error procesando activos. Verifique el formato o cambie de archivo.")
        st.stop()

    try:
        df_RPM = procesar_flujo_RPM(df_activos, st.session_state["ventas_df"])
        st.session_state["rpm_df"] = df_RPM
        st.session_state["rpm_excel"] = df_a_excel(df_RPM)
    except Exception as e:
        st.error("Error generando RPM. Verifique el formato o cambie de archivo.")
        for key in ["ventas_raw", "ventas_df", "AF", "Cartera", "rpm_df", "rpm_excel"]:
            st.session_state.pop(key, None)
        st.stop()

if "rpm_df" not in st.session_state:
    st.stop()

df_RPM = st.session_state["rpm_df"]
excel_file = st.session_state["rpm_excel"]

st.subheader("BASE RPM (Sin Fórmulas)")
st.write(f"Filas: {df_RPM.shape[0]} | Columnas: {df_RPM.shape[1]}")
st.dataframe(df_RPM.head())

fecha_actual = datetime.now()
nombre_archivo = f"RPM_final_{fecha_actual.strftime('%d%m%Y')}.xlsx"

st.download_button(
    label="Descargar Excel",
    data=excel_file,
    file_name=nombre_archivo,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)