import time
import feedparser
from google import genai
import pandas as pd
import os
import re
import requests
# import gspread
from bs4 import BeautifulSoup
# from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==========================================
# CONFIGURACIÓN (CORREGIDA)
# ==========================================
API_KEYS = {
    "Olé": os.getenv("OLE_API_KEY"),
    "Clarín": os.getenv("CLARIN_API_KEY"),
    "iProfesional": os.getenv("IPROFESIONAL_API_KEY"),
    "Caras": os.getenv("CARAS_API_KEY"),
    "Ambito": os.getenv("AMBITO_API_KEY")
}

FUENTES = {
    "Olé": "https://www.ole.com.ar/rss/ultimas-noticias/",
    "Clarín": "https://www.clarin.com/rss/lo-ultimo/",
    "iProfesional": "https://www.iprofesional.com/rss/home",
    "Caras": "https://caras.perfil.com/feed",
    "Ambito": "https://www.ambito.com/rss/pages/home.xml",
}


FIREBASE_CREDS = "firebase-creds.json"

# ==========================================
# FUNCIONES
# ==========================================
def conectar_firestore():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDS)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"❌ Error al conectar con Firestore: {e}")
        return None

def guardar_en_firestore(nueva_fila, db):
    try:
        db.collection('articulos').add(nueva_fila)
        return True
    except Exception as e:
        print(f"⚠️ Error al insertar documento en Firestore: {e}")
        return False

def limpiar_html(texto):
    if not texto: return ""
    return re.sub(r'<[^>]*>', '', texto)

def extraer_cuerpo_noticia(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.encoding = 'utf-8'
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        parrafos = soup.find_all('p')
        texto_sucio = " ".join([p.get_text() for p in parrafos if len(p.get_text()) > 60])
        return " ".join(texto_sucio.split())[:4000]
    except:
        return ""

# ==========================================
# BUCLE PRINCIPAL
# ==========================================
ultimos_links = {nombre: "" for nombre in FUENTES}
db = conectar_firestore()

if not db:
    print("No se pudo establecer la conexión inicial. Cerrando script.")
    exit()

print("🚀 Script iniciado. Monitoreando noticias...")

while True:
    ahora = datetime.now()
    
    # OPTIMIZACIÓN: Leemos los links existentes en Firestore UNA VEZ por ciclo de 30 segundos
    try:
        docs = db.collection('articulos').select(['Link']).stream()
        links_en_db = [doc.to_dict().get('Link') for doc in docs if 'Link' in doc.to_dict()]
    except Exception as e:
        print(f"⚠️ Error al leer Firestore: {e}")
        links_en_db = []

    for diario, url in FUENTES.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entrada = feed.entries[0]
                link_actual = entrada.link

                if link_actual != ultimos_links[diario]:
                    
                    # Chequeo preventivo contra la lista que bajamos de Firestore
                    if link_actual in links_en_db:
                        print(f"✅ {diario}: La noticia ya está en Firestore. Saltando...")
                        ultimos_links[diario] = link_actual
                        continue 

                    # Si llegó acá, es porque REALMENTE es nueva
                    print(f"🔍 Procesando nueva noticia en {diario}...")
                    
                    # FECHAS CORREGIDAS
                    fecha_rss_raw = entrada.get('published', '')
                    if fecha_rss_raw:
                        try:
                            fecha_dt = datetime(*(entrada.published_parsed[:6]))
                            fecha_dt = fecha_dt - timedelta(hours=3) # AJUSTE ARGENTINA
                            fecha_publicacion = fecha_dt.strftime("%d/%m/%Y %H:%M:%S")
                        except:
                            fecha_publicacion = fecha_rss_raw 
                    else:
                        fecha_publicacion = ahora.strftime("%d/%m/%Y %H:%M:%S")

                    fecha_carga = ahora.strftime("%d/%m/%Y %H:%M:%S")
                    
                    cuerpo_nota = extraer_cuerpo_noticia(link_actual)
                    resumen_rss = limpiar_html(entrada.get('summary', ''))
                    texto_para_ia = cuerpo_nota if len(cuerpo_nota) > 150 else resumen_rss

                    # GEMINI (Actualizado a nueva API)
                    resumen_ia = "Error en IA"
                    modelos_a_probar = [
                        'gemini-3.1-flash-lite-preview', 
                        'gemini-3-flash-preview', 
                        'gemini-2.5-flash-lite', 
                        'gemini-2.5-flash'
                    ]
                    
                    prompt = f"Sos un periodista. Resumí en maximo 4 oraciones directamente y sin comentarios.:\n\n{texto_para_ia}"
                    
                    for nombre_modelo in modelos_a_probar:
                        try:
                            client = genai.Client(api_key=API_KEYS.get(diario))
                            response = client.models.generate_content(
                                model=nombre_modelo,
                                contents=prompt
                            )
                            resumen_ia = response.text.strip()
                            
                            print(f"🤖 [{diario}] Resumen OK con: {nombre_modelo}")
                            break 
                        except Exception as e:
                            print(f"❌ Error real detectado: {e}")
                            continue

                    # Preparación de datos para guardado
                    datos = {
                        "Diario": diario, 
                        "Fecha Carga": fecha_carga,
                        "Fecha Publicacion": fecha_publicacion, 
                        "Titulo": entrada.title,
                        "Resumen IA": resumen_ia, 
                        "Resumen Web": resumen_rss, 
                        "Link": link_actual
                    }

                    if guardar_en_firestore(datos, db):
                        print(f"💾 [{diario}] Guardado exitosamente en Firestore.")
                        # Actualizamos memoria local para evitar re-procesar en este mismo ciclo
                        ultimos_links[diario] = link_actual
                        links_en_db.append(link_actual)

        except Exception as e:
            print(f"❗ Error en el bucle de {diario}: {e}")

    # Espera de 30 segundos antes de la siguiente vuelta
    time.sleep(30)