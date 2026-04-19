import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Configuración visual de la web
st.set_page_config(page_title="Noticias de Diarios con IA", layout="wide", page_icon="🗞️")

st.title("🗞️ Noticias de Diarios con IA")
st.markdown("---")

# 2. Función para leer los datos de Google Sheets
def cargar_datos():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Asegurate que este archivo esté en la carpeta
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Base_Noticias").sheet1 
    data = sheet.get_all_records()
    return pd.DataFrame(data)

try:
    df = cargar_datos()

    # 3. Filtros en la barra lateral
    st.sidebar.header("Filtros")
    diarios = st.sidebar.multiselect(
        "Seleccioná los diarios:", 
        options=df['Diario'].unique(), 
        default=df['Diario'].unique()
    )
    
    df_filtrado = df[df['Diario'].isin(diarios)]

    # 4. Mostrar las noticias como tarjetas
    if df_filtrado.empty:
        st.warning("No hay noticias para mostrar con esos filtros.")
    else:
        for index, row in df_filtrado.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(f"**{row['Diario']}**")
                    st.caption(f"🕒 {row['Fecha Publicacion']}")
                with col2:
                    st.subheader(row['Titulo'])
                    st.markdown(f"**Resumen IA:** {row['Resumen IA']}")
                    st.link_button("Leer nota completa", row['Link'])
                st.markdown("---")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
