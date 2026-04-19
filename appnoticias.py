import time
import feedparser
import google.generativeai as genai
import pandas as pd
import os
import re
import requests
import gspread
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN
# ==========================================
API_KEYS = {
    "Olé": "AIzaSyDCvBWEP_i-EQ8ESF83avnBMtz7DwArKzM",
    "Clarín": "AIzaSyDZU-bJrXUr1h78Mv-mJTEERHEOt7EIH28",
    "iProfesional": "AIzaSyBlP6Cz0ePoVnTkOWXrciAWNtuGzXfX5Wc"
}

FUENTES = {
    "Olé": "https://www.ole.com.ar/rss/ultimas-noticias/",
    "Clarín": "https://www.clarin.com/rss/lo-ultimo/",
    "iProfesional": "https://www.iprofesional.com/rss/home"
}

NOMBRE_PLANILLA = "Base_Noticias"
ARCHIVO_JSON = "creds.json" 

# ==========================================
# FUNCIONES
# ==========================================
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(ARCHIVO_JSON, scope)
        client = gspread.authorize(creds)
        return client.open(NOMBRE_PLANILLA).sheet1
    except Exception as e:
        print(f"❌ Error al conectar con Google Sheets: {e}")
        return None

def guardar_en_google_sheets(nueva_fila, hoja):
    try:
        links_existentes = hoja.col_values(7)
        if nueva_fila['Link'] in links_existentes:
            return False
        fila_datos = [
            nueva_fila["Diario"], nueva_fila["Fecha Carga"],
            nueva_fila["Fecha Publicacion"], nueva_fila["Titulo"],
            nueva_fila["Resumen IA"], nueva_fila["Resumen Web"],
            nueva_fila["Link"]
        ]
        hoja.insert_row(fila_datos, 2)
        return True
    except Exception as e:
        print(f"⚠️ Error al insertar fila: {e}")
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
hoja_nube = conectar_google_sheets()

if not hoja_nube:
    exit()

while True:
    ahora = datetime.now()
    for diario, url in FUENTES.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entrada = feed.entries[0]
                link_actual = entrada.link

                if link_actual != ultimos_links[diario]:
                    ultimos_links[diario] = link_actual
                    print(f"🔍 Nueva noticia en {diario}: {entrada.title[:50]}...")
                    
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

                    # GEMINI
                    try:
                        genai.configure(api_key=API_KEYS.get(diario))
                        model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
                        prompt = (f"Sos un periodista. Resumí en 3 oraciones directamente y sin comentarios como aquí esta el resumen.\n\nTÍTULO: {entrada.title}\nCUERPO: {texto_para_ia}")
                        resumen_ia = model.generate_content(prompt).text.strip()
                    except:
                        resumen_ia = "Error en IA"

                    datos = {
                        "Diario": diario, "Fecha Carga": fecha_carga,
                        "Fecha Publicacion": fecha_publicacion, "Titulo": entrada.title,
                        "Resumen IA": resumen_ia, "Resumen Web": resumen_rss, "Link": link_actual
                    }

                    if guardar_en_google_sheets(datos, hoja_nube):
                        print(f"✅ [{diario}] Guardado con hora Argentina.")

        except Exception as e:
            print(f"❗ Error: {e}")

    time.sleep(30)