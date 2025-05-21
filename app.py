import streamlit as st
import pandas as pd
import os

# Archivos
CARPETA_DATOS = "C:\\Users\\Daniela\\Desktop\\Streamlit\\BACI"
ARCHIVO_PAISES = os.path.join(CARPETA_DATOS, "country_codes_V202501.csv")

@st.cache_data
def cargar_paises():
    paises = pd.read_csv(ARCHIVO_PAISES)
    paises["code"] = pd.to_numeric(paises["code"], errors="coerce").astype("Int64")

    paises_exp = paises.rename(columns={"code": "i", "country_name": "pais_exportador"})
    paises_imp = paises.rename(columns={"code": "j", "country_name": "pais_importador"})

    return paises_exp, paises_imp

@st.cache_data
def cargar_datos(anio, paises_exp, paises_imp):
    archivo = os.path.join(CARPETA_DATOS, f"BACI_HS02_Y{anio}_V202501.csv")
    if not os.path.exists(archivo):
        return pd.DataFrame()

    df = pd.read_csv(archivo)

    # Merge con país exportador
    df = df.merge(paises_exp[["i", "pais_exportador"]], on="i", how="left")
    # Merge con país importador
    df = df.merge(paises_imp[["j", "pais_importador"]], on="j", how="left")

    # Renombrar y limpiar
    df = df.drop(columns=["i", "j"])
    df = df.rename(columns={
        "pais_exportador": "exportador",
        "pais_importador": "importador"
    })

    return df

# ---------- INTERFAZ STREAMLIT ----------
st.title("📦 Dashboard de Exportaciones BACI")

# Selección de año
anio = st.selectbox("Selecciona un año", list(range(2002, 2024)))

# Cargar datos
paises_exp, paises_imp = cargar_paises()
df = cargar_datos(anio, paises_exp, paises_imp)

if df.empty:
    st.warning("⚠️ No se encontró el archivo para el año seleccionado.")
else:
    productos = sorted(df["k"].unique())
    producto = st.selectbox("Selecciona un producto (código HS)", productos)

    paises = sorted(set(df["exportador"].dropna().unique()) | set(df["importador"].dropna().unique()))
    pais = st.selectbox("Selecciona un país", paises)

    modo = st.radio("¿Visualizar como país exportador o importador?", ["Exportador", "Importador"])

    if modo == "Exportador":
        df_filtrado = df[(df["exportador"] == pais) & (df["k"] == producto)]
        df_agrupado = df_filtrado.groupby("importador")["v"].sum().reset_index()
        df_agrupado = df_agrupado.sort_values(by="v", ascending=False)
        st.bar_chart(df_agrupado.set_index("importador"))
    else:
        df_filtrado = df[(df["importador"] == pais) & (df["k"] == producto)]
        df_agrupado = df_filtrado.groupby("exportador")["v"].sum().reset_index()
        df_agrupado = df_agrupado.sort_values(by="v", ascending=False)
        st.bar_chart(df_agrupado.set_index("exportador"))

    st.success(f"{len(df_filtrado)} registros mostrados para {pais} en {anio}")