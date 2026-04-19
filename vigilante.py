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
# CONFIGURACIÓN DE LLAVES Y FUENTES
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

# CONFIGURACIÓN GOOGLE SHEETS
NOMBRE_PLANILLA = "Base_Noticias"
# Ajusté el nombre según tu mensaje: creds.json
ARCHIVO_JSON = "creds.json" 

# ==========================================
# FUNCIONES DE CONEXIÓN Y GUARDADO (GOOGLE SHEETS)
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
        # Verificamos duplicados en la columna G (índice 7: Link)
        links_existentes = hoja.col_values(7)
        if nueva_fila['Link'] in links_existentes:
            return False
            
        # Convertimos el diccionario a una lista plana para la fila
        fila_datos = [
            nueva_fila["Diario"],
            nueva_fila["Fecha Carga"],
            nueva_fila["Fecha Publicacion"],
            nueva_fila["Titulo"],
            nueva_fila["Resumen IA"],
            nueva_fila["Resumen Web"],
            nueva_fila["Link"]
        ]
        
        # Insertamos en la fila 2 (debajo del encabezado)
        hoja.insert_row(fila_datos, 2)
        return True
    except Exception as e:
        print(f"⚠️ Error al insertar fila: {e}")
        return False

# ==========================================
# FUNCIONES DE EXTRACCIÓN Y LIMPIEZA
# ==========================================
def limpiar_html(texto):
    if not texto: return ""
    return re.sub(r'<[^>]*>', '', texto)

def extraer_cuerpo_noticia(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.encoding = 'utf-8'
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        parrafos = soup.find_all('p')
        texto_sucio = " ".join([p.get_text() for p in parrafos if len(p.get_text()) > 60])
        return " ".join(texto_sucio.split())[:4000]
    except:
        return ""

# ==========================================
# BUCLE PRINCIPAL (MODO NUBE)
# ==========================================
ultimos_links = {nombre: "" for nombre in FUENTES}

print(f"🚀 Vigilante Nube activado. Conectando a Google Sheets...")
hoja_nube = conectar_google_sheets()

if hoja_nube:
    print(f"✅ Conexión exitosa a la planilla: {NOMBRE_PLANILLA}")
else:
    print("❌ No se pudo iniciar el vigilante sin conexión a la planilla.")
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
                    
                    cuerpo_nota = extraer_cuerpo_noticia(link_actual)
                    resumen_rss = limpiar_html(entrada.get('summary', ''))
                    texto_para_ia = cuerpo_nota if len(cuerpo_nota) > 150 else resumen_rss

                    # Gemini IA
                    try:
                        genai.configure(api_key=API_KEYS.get(diario))
                        model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
                        
                        prompt = (f"Actuá como un periodista. Respondé directamente con el resumen en 3 oraciones, sin introducciones.\n\n"
                                  f"TÍTULO: {entrada.title}\n"
                                  f"RESUMEN PREVIO: {resumen_rss}\n"
                                  f"CUERPO COMPLETO: {texto_para_ia}")
                        
                        resumen_ia = model.generate_content(prompt).text.strip()
                        time.sleep(2) 
                    except Exception as e:
                        resumen_ia = "Error en IA"
                        print(f"❌ Error Gemini {diario}: {e}")

                    # Preparar datos
                    fecha_str = ahora.strftime("%d/%m/%Y %H:%M:%S")
                    datos = {
                        "Diario": diario, 
                        "Fecha Carga": fecha_str,
                        "Fecha Publicacion": fecha_str, 
                        "Titulo": entrada.title, 
                        "Resumen IA": resumen_ia, 
                        "Resumen Web": resumen_rss, 
                        "Link": link_actual
                    }

                    if guardar_en_google_sheets(datos, hoja_nube):
                        print(f"✅ [{diario}] Guardado en Google Sheets.")

        except Exception as e:
            print(f"❗ Error procesando {diario}: {e}")

    print(f"☕ Ronda terminada. Esperando 30 segundos...")
    time.sleep(30)