# Portal de Noticias IA - Resumen y Categorización 🚀

Este proyecto es una plataforma profesional de noticias automatizada que utiliza Inteligencia Artificial para recolectar, resumir y clasificar noticias de los principales medios de Argentina en tiempo real.

## ✨ Características

- **Recolección Multi-fuente**: Extrae noticias automáticamente vía RSS de fuentes como Olé, Perfil, Ámbito y Caras.
- **Resúmenes con Gemini AI**: Genera resúmenes ejecutivos de máximo 4 oraciones utilizando los últimos modelos de Google Gemini.
- **Categorización Inteligente**: Clasifica automáticamente cada artículo en categorías como Política, Economía, Deportes, Tecnología, etc.
- **Diseño Premium**: Interfaz moderna con estética "Glassmorphism", modo oscuro nativo, y diseño responsivo optimizado para móviles.
- **Filtros Dinámicos**: Sistema de filtrado combinado por medio de comunicación y categoría temática.
- **Gestión de Datos Eficiente**: Limpieza automática de noticias antiguas y almacenamiento persistente en Firestore.

## 🛠️ Stack Tecnológico

### Backend (Python)
- **Google GenAI SDK**: Integración con Gemini 2.x y 3.x Flash.
- **Feedparser**: Procesamiento de feeds RSS.
- **BeautifulSoup4**: Scraping para extracción de texto completo de noticias.
- **Firebase Admin SDK**: Comunicación con Firestore.
- **Google Cloud Run**: Hosting del backend escalable.

### Frontend (Web)
- **HTML5 / CSS3**: Diseño a medida con variables CSS y animaciones fluidas.
- **JavaScript (Vanilla)**: Lógica de filtrado y consumo de datos en tiempo real.
- **Firebase SDK**: Conexión directa con la base de datos desde el cliente.
- **Firebase Hosting**: Despliegue de la aplicación web.

## ⚙️ Configuración del Entorno

### Requisitos Previos
1. Una cuenta en [Google Cloud Console](https://console.cloud.google.com/).
2. Un proyecto de Firebase con Firestore habilitado.
3. API Keys de Google Gemini.

### Variables de Entorno
El backend requiere las siguientes claves para funcionar:
- `OLE_API_KEY`
- `PERFIL_API_KEY`
- `CARAS_API_KEY`
- `AMBITO_API_KEY`

## 🚀 Despliegue

### 1. Backend (Google Cloud Run)
Para desplegar o actualizar el servicio de procesamiento:

```bash
gcloud run deploy noticias-backend \
  --project=portal-noticias-ia \
  --source . \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --timeout 540 \
  --memory 512Mi \
  --set-env-vars OLE_API_KEY="TU_KEY",PERFIL_API_KEY="TU_KEY",...
```

### 2. Frontend (Firebase Hosting)
Para subir los cambios visuales y la lógica del cliente:

```bash
firebase deploy
```

## 📂 Estructura del Proyecto

- `backend.py`: Script principal que realiza el scraping, llama a la IA y guarda en Firestore.
- `public/index.html`: SPA (Single Page Application) con el diseño y lógica de visualización.
- `firebase-creds.json`: (No incluido por seguridad) Credenciales de cuenta de servicio para acceso a DB.
- `requirements.txt`: Dependencias de Python necesarias.

---
*Desarrollado con ❤️ integrando Python y Google Gemini AI.*