Ejecutar el motor de noticias: fijarse que estes en carpeta correcta
python appnoticias.py
Ver las noticias en el navegador (opcional):
streamlit run app.py


# 🗞️ Noticiero Automático con Inteligencia Artificial

Este proyecto es un sistema de automatización de noticias desarrollado en **Python**. Se encarga de monitorear feeds RSS de los principales diarios argentinos, extraer el contenido de las notas, resumirlas utilizando modelos avanzados de **Google Gemini** y almacenar todo en una base de datos de **Google Sheets** para su posterior visualización.

## 🚀 Funcionalidades
- **Scraping en Tiempo Real:** Monitorea fuentes como Olé, Clarín e iProfesional cada 30 segundos.
- **Resúmenes Inteligentes:** Utiliza IA para generar resúmenes de 3 oraciones, eliminando el "ruido" de las notas originales.
- **Lógica de Fallback (Respaldo):** Si un modelo de IA falla o no está disponible, el sistema intenta automáticamente con el siguiente en la lista para asegurar la continuidad.
- **Evita Duplicados:** Chequea los links existentes en Google Sheets antes de procesar una noticia para no gastar tokens de IA innecesariamente.
- **Ajuste de Horario:** Corrige las fechas de publicación al huso horario de Argentina (UTC-3).

## 🛠️ Stack Tecnológico
- **Lenguaje:** Python 3.x
- **IA:** Google Generative AI (Gemini)
- **Base de Datos:** Google Sheets API (`gspread`)
- **Web Scraping:** `BeautifulSoup`, `feedparser` y `requests`
- **Interfaz (Opcional):** Streamlit (para ver las noticias)

## 📁 Estructura del Proyecto
- `appnoticias.py`: El "motor" que busca, procesa y guarda las noticias.
- `app.py`: Dashboard visual para leer las noticias procesadas.
- `creds.json`: Credenciales de la cuenta de servicio de Google Cloud.
- `.env`: (Recomendado) Para guardar las API Keys de Gemini.

## 🤖 Modelos de IA Utilizados (en orden de prioridad)
1. `gemini-3.1-flash-lite-preview`
2. `gemini-3-flash-preview`
3. `gemini-2.5-flash-lite`
4. `gemini-2.5-flash`

## ⚙️ Configuración e Instalación

1. **Instalar dependencias:**
   ```bash
   pip install feedparser google-generativeai pandas requests gspread beautifulsoup4 oauth2client streamlit
