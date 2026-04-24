import feedparser
from google import genai
import pandas as pd
import os
import re
import requests
import time  # Para el retraso (RPM)
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==========================================
# CONFIGURACIÓN
# ==========================================
API_KEYS = {
    "Olé": os.getenv("OLE_API_KEY"),
    "Perfil": os.getenv("PERFIL_API_KEY"),
    "Caras": os.getenv("CARAS_API_KEY"),
    "Ambito": os.getenv("AMBITO_API_KEY")
}

FUENTES = {
    "Olé": "https://www.ole.com.ar/rss/ultimas-noticias/",
    "Perfil": "https://www.perfil.com/feed",
    "Caras": "https://caras.perfil.com/feed",
    "Ambito": "https://www.ambito.com/rss/pages/home.xml",
}

FIREBASE_CREDS = "firebase-creds.json"

# ==========================================
# FUNCIONES
# ==========================================
def conectar_firestore(request=None):
    try:
        if not firebase_admin._apps:
            if os.path.exists(FIREBASE_CREDS):
                cred = credentials.Certificate(FIREBASE_CREDS)
                initialize_app(cred)
            else:
                initialize_app()
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

def ejecutar_recoleccion(request=None):
    db = conectar_firestore()
    if not db:
        return "Error de conexión a Firestore", 500

    print("🚀 Iniciando recolección de noticias...")
    
    argentina_tz = timezone(timedelta(hours=-3))
    fecha_carga = datetime.now(argentina_tz)

    for diario, url in FUENTES.items():
        try:
            print(f"📰 Revisando {diario}...")
            feed = feedparser.parse(url)
            
            # Instanciar el cliente una sola vez por diario
            api_key = API_KEYS.get(diario)
            if not api_key:
                print(f"⚠️ Sin API Key para {diario}, saltando...")
                continue
            client = genai.Client(api_key=api_key)
            
            # RECORREMOS TODAS LAS NOTICIAS DEL RSS
            for entrada in feed.entries:
                link_actual = entrada.link

                # Consulta eficiente: ¿Existe este link específico?
                doc_existe = db.collection('articulos').where('Link', '==', link_actual).limit(1).get()
                if len(doc_existe) > 0:
                    print(f"⏭️ Noticia ya procesada: {entrada.title[:40]}...")
                    continue  # Cambiado a continue para no saltar noticias si hubo una interrupción

                print(f"🔍 Nueva noticia detectada: {entrada.title[:60]}...")
                
                # Procesamiento de fecha
                try:
                    fecha_dt = datetime(*(entrada.published_parsed[:6]), tzinfo=timezone.utc)
                    fecha_publicacion = fecha_dt.astimezone(argentina_tz)
                except:
                    fecha_publicacion = fecha_carga

                cuerpo_nota = extraer_cuerpo_noticia(link_actual)
                resumen_rss = limpiar_html(entrada.get('summary', ''))
                texto_para_ia = cuerpo_nota if len(cuerpo_nota) > 150 else resumen_rss

                # GEMINI (Modelos TAL CUAL pediste)
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
                        response = client.models.generate_content(
                            model=nombre_modelo,
                            contents=prompt
                        )
                        resumen_ia = response.text.strip()
                        print(f"🤖 [{diario}] OK con: {nombre_modelo}")
                        break 
                    except Exception as e:
                        continue

                # Preparar y guardar
                datos = {
                    "Diario": diario, 
                    "Fecha_Carga": fecha_carga,
                    "Fecha_Publicacion": fecha_publicacion,
                    "Titulo": entrada.title,
                    "Resumen_IA": resumen_ia,
                    "Resumen_Web": resumen_rss,
                    "Link": link_actual
                }

                if guardar_en_firestore(datos, db):
                    print(f"💾 Guardado en Firestore.")
                
                # --- CONTROL DE RPM ---
                # Esperamos 12 segundos antes de ir a la siguiente noticia
                # para no superar los 5 pedidos por minuto a la IA.
                print("⏳ Esperando 12s para cuidar el RPM...")
                time.sleep(12)

        except Exception as e:
            print(f"❗ Error en el bucle de {diario}: {e}")
    
    return "OK", 200

if __name__ == "__main__":
    ejecutar_recoleccion()
    print("✅ Ciclo finalizado.")