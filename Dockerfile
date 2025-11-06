# Imagen base oficial de Python
FROM python:3.12-slim

# Variables de entorno recomendadas para Django
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=Petzy.settings \
    PORT=8000

# Instala utilidades del sistema necesarias (por ejemplo, gettext para traducciones)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    gettext \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copia primero las dependencias (para aprovechar la caché de Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . /app/

# Recopila archivos estáticos y compila los catálogos de traducción
RUN python manage.py collectstatic --noinput \
 && django-admin compilemessages || true

# Expone el puerto donde correrá la app
EXPOSE 8000

# Comando que ejecuta Django con Gunicorn (para producción)
CMD ["bash", "-lc", "python manage.py migrate --noinput && gunicorn Petzy.wsgi:application --bind 0.0.0.0:8000"]

