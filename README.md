# 📰 Portal de Noticias con IA (Scraper + Gemini)

Este proyecto es un pipeline automatizado de noticias que recolecta artículos de los principales medios de Argentina (Olé, Clarín, Caras, Ámbito), procesa su contenido y genera resúmenes inteligentes utilizando los últimos modelos de **Google Gemini**.

## 🌐 Demo en Vivo
Puedes ver el portal funcionando aquí: [🔗 https://portal-noticias-ia-9c7c9.web.app/](https://portal-noticias-ia-9c7c9.web.app/)

> **Nota:** El backend procesa las noticias cada X tiempo y el frontend consume los datos en tiempo real desde Firestore.

## 🚀 Funcionalidades

*   **Scraping Multifuente:** Monitorea feeds RSS de diversos diarios en tiempo real.
*   **Extracción de Contenido:** Utiliza `BeautifulSoup` para extraer el cuerpo de la noticia de forma limpia, omitiendo publicidad y elementos innecesarios.
*   **Resúmenes con IA:** Procesa el texto mediante la API de Google GenAI para generar resúmenes concisos de máximo 4 oraciones.
*   **Control de Rate Limiting:** Implementa un sistema de espera para respetar los límites de RPM (Requests Per Minute) de la API gratuita.
*   **Persistencia en la Nube:** Almacena los resultados en **Firebase Firestore**, evitando duplicados mediante la verificación de enlaces.

## 🛠️ Tecnologías utilizadas

*   **Lenguaje:** Python 3.x
*   **IA:** Google Gemini API (GenAI)
*   **Base de Datos:** Firebase Firestore (NoSQL)
*   **Librerías Key:** `feedparser`, `BeautifulSoup4`, `google-genai`, `requests`.
*   **Frontend:** HTML5, CSS3 (Tailwind/Bootstrap), JavaScript (Vanilla/Firebase SDK).

## 📂 Estructura del Proyecto

*   `/`: Contiene el `backend.py` y archivos de configuración.
*   `/frontend`: (Opcional) Si separaste los archivos web en una carpeta, menciónalo aquí.
    *   `index.html`: Estructura principal del portal.
    *   `app.js`: Lógica para leer datos de Firebase y mostrarlos.
    *   `styles.css`: Diseño y estilos responsivos.

## 📋 Configuración

Para replicar este proyecto, necesitarás:

1.  **API Keys de Gemini:** Obtén tus llaves en Google AI Studio.
2.  **Firebase:** Crea un proyecto en la consola de Firebase, activa Firestore y descarga el archivo `firebase-creds.json`.
3.  **Variables de Entorno:** Crea un archivo `.env` con el siguiente formato:
    ```env
    OLE_API_KEY=tu_key_aqui
    CLARIN_API_KEY=tu_key_aqui
    CARAS_API_KEY=tu_key_aqui
    AMBITO_API_KEY=tu_key_aqui
    ```

## 💻 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/portal-noticias-ia.git

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el script
python backend.py
```

---
*Proyecto desarrollado como muestra de integración de IA Generativa y Web Scraping.*
