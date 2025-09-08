# 🐾 Petzy - Tienda de Mascotas

## 📋 Descripción del Proyecto
**Petzy** es una plataforma de e-commerce especializada en productos para mascotas.  
Desarrollada con **Django 4.2** y **SQLite3**, utiliza una arquitectura **MVT (Modelo-Vista-Template)** e incluye todas las funcionalidades de una tienda online completa.

---

## 🚀 Cómo ejecutar el proyecto

### Prerrequisitos
- **Python:** 3.8 o superior  
- **pip:** Gestor de paquetes de Python  
- **Git:** Para clonar el repositorio  

### 📦 Instalación paso a paso
1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd Petzy
```
2. Crear entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
```
3. Instalar dependencias:
```bash
pip install -r requirements.txt     
``` 
4. Aplicar migraciones:
```bash
python manage.py migrate
```
5. Cargar datos iniciales (opcional):
```bash
python manage.py loaddata data/sample_data.json
```
6. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

## 🌐 Acceso a la aplicación

Sitio principal: http://127.0.0.1:8000/

Panel de administración: http://127.0.0.1:8000/admin/

### 👥 Credenciales de prueba
```bash
Administrador

Usuario: admin

Contraseña: admin123

Email: admin@petzy.com

Clientes

Usuario: cliente1 / Contraseña: password123

Usuario: cliente2 / Contraseña: password123

Usuario: cliente3 / Contraseña: password123
```

## 🏗️ Arquitectura del Proyecto
### 📊 Modelo de Datos

Users: Sistema de autenticación personalizado

Products: Catálogo de productos y reseñas

Cart: Carrito de compras

Orders: Sistema de pedidos y pagos

### 🎨 Tecnologías Utilizadas

Backend: Django 4.2, Python

Base de datos: SQLite3

Frontend: HTML5, CSS3, JavaScript

Templates: Django Template Language

## 🎯 Funcionalidades Principales
### ✅ Implementadas

🔐 Autenticación personalizada con modelo de usuario extendido

🛍️ Catálogo de productos con imágenes y descripciones

⭐ Sistema de reseñas y calificaciones

🛒 Carrito de compras persistente

📦 Sistema de pedidos con estados de orden

💳 Módulo de pagos integrado

⚙️ Panel de administración Django personalizado

### 🚀 Funcionalidades Especiales

🔍 Búsqueda de productos por nombre

📄 Generación de facturas PDF para órdenes

⭐ Top productos más vendidos

💬 Top productos más comentados

## 📝 Notas

Se recomienda usar un entorno virtual para evitar conflictos de dependencias.

La base de datos utilizada por defecto es SQLite3, ideal para desarrollo y pruebas.

Las rutas de acceso pueden modificarse según la configuración del proyecto.