import streamlit as st
import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import os
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Configuración visual de la web
st.set_page_config(page_title="Noticias de Diarios con IA", layout="wide", page_icon="🗞️")

st.title("🗞️ Noticias de Diarios con IA")
st.markdown("---")

# 2. Función para leer los datos de Firestore
def cargar_datos():
    # Verificamos si la app ya fue inicializada para evitar errores en Streamlit
    if not firebase_admin._apps:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(base_dir, 'firebase-creds.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    docs = db.collection('articulos').stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

try:
    df = cargar_datos()

    if not df.empty:
        # --- LÓGICA DE ORDENAMIENTO ---
        # Convertimos a fecha real para ordenar
        df['Fecha Publicacion'] = pd.to_datetime(df['Fecha Publicacion'], dayfirst=True)
        # Ordenamos (True = de más vieja a más nueva, False = de más nueva a más vieja)
        df = df.sort_values(by='Fecha Publicacion', ascending=False)
        # ------------------------------

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
                        st.write(f"### {row['Diario']}")
                        
                        # TIP PRO: Formateamos la fecha para que se vea linda en la web
                        fecha_linda = row['Fecha Publicacion'].strftime("%d/%m/%Y %H:%M")
                        
                        st.caption(f"🗓️ **Pub:** {fecha_linda}")
                        st.caption(f"📥 **Carga:** {row['Fecha Carga']}")
                    
                    with col2:
                        st.subheader(row['Titulo'])
                        st.write(f"*{row['Resumen Web']}*")
                        st.markdown(f"**🤖 Resumen IA:** {row['Resumen IA']}")
                        st.link_button("🔗 Leer nota completa", row['Link'])
                    
                    st.markdown("---")
    else:
        st.info("Todavía no hay noticias cargadas.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")