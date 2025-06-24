# URL Shortener — Guía de Instalación y Uso
Este proyecto es un acortador de URLs expuesto como una API REST.<br>
A continuación se presenta una guía paso a paso para su instalación y uso.

*Para más detalles técnicos sobre las decisiones de diseño, tecnologías utilizadas y justificación de la arquitectura, consulte [Detalles Técnicos](docs/README.md)*

## 1. Requisitos Previos

- Python 3.12+  
- Git  
- PostgreSQL: recomendado para producción (opcional)  
- Redis: para cacheo y rate limiting (opcional)  
- Docker y Docker Compose: para correr contenedores (opcional)  


## 2. Clonar el Proyecto

```bash
git clone https://github.com/deimos-et-fobos/url-shortener
cd url-shortener
```

## 3. Crear y Activar Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate   
```

## 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 5. Configurar Variables de Entorno

Copiar el archivo de ejemplo y editar:

```bash
cp .env.example .env
```

Configurar en `.env`:

* `ENVIRONMENT`: `production` o `development`. Para pruebas locales utilizar `development`
* `ALLOWED_HOSTS`: lista de dominios permitidos separados por `,`, por ejemplo `localhost,127.0.0.1,mi-dominio.com`
* `DEBUG`: `True` o `False`
* `SECRET_KEY`: clave secreta Django
* `USE_POSTGRES`: `True` para usar PostgreSQL, `False` para SQLite. En `production` siempre se utilizará PostgreSQL.
* `USE_CACHE`: `True` habilitar Redis para cache y rate limiting. Por defecto `False`.
* `REDIS_URL`: URL de Redis, ejemplo: `redis://localhost:6379/0`
* `RATE_LIMIT`: Rate Limit. Por defecto '10/m'
* `CORS_ALLOWED_ORIGINS`: Lista de orígenes permitidos CORS para producción separados por `,`
* `CSRF_TRUSTED_ORIGINS`: Lista de orígenes permitidos CSRF para producción separados por `,`
* `SHORT_URL_LENGTH`: longitud de las short URL. Por defecto 8, máximo 10

***ATENCIÓN: Si desea habilitar el uso de cache con Redis, asegurese de que Redis esté instalado y que el servicio este en funcionamiento. Caso contrario, deshabilite el uso de cache.***
***ATENCIÓN: Para rate limiting es necesario que el uso cache este habilitado.***

## 6. Aplicar migraciones a la DB y realizar collectstatic

```bash
python manage.py migrate
python manage.py collectstatic
```

## 7. Crear Superuser 
Para utilizar el panel de administración de Django y gestionar usuarios u otros modelos, debe crear primero un superusuario.

```bash
python manage.py createsuperuser
```

El Admin Site estará disponible en: `http://127.0.0.1:8000/admin/`

## 8. Ejecutar Tests
Puede ejecutar los tests y generar un reporte del coverage del mismo utilizando:

```bash
pytest --cov --cov-report=html
```

## 9. Levantar el Servidor Local

```bash
python manage.py runserver
```

La API quedará disponible en:
`http://127.0.0.1:8000/`

***ATENCIÓN: Para pruebas locales, solo se podrán realizar solicitudes mediante el protocolo HTTP. Si se requiere HTTPS, deberá configurarse manualmente o utilizar un entorno de producción con certificados válidos.***


## 10. Uso con Docker (opcional)

En caso de desear utilizar Docker, asegurarse de tener Docker y Docker Compose instalados.

Desde la raíz del proyecto ejecutar:

```bash
cp .env.example .env
docker compose up --build
```

Esto levantará todos los servicios configurados: Django, Postgres, Redis.

La API quedará disponible en:
`http://127.0.0.1:8000/`

### Crear superuser
Con los contenedores ya iniciados ejecutar en otra terminal:

```bash
docker exec -ti django_app python manage.py createsuperuser
```

### Ejecutar Tests
Al igual que para crear un superuser, con los contenedores ya iniciados ejecutar en otra terminal:

```bash
docker exec  django_app pytest --cov --cov-report=html
```


## 11. Documentación de la API

La documentación de la API estará disponible en:

* Swagger UI: `http://127.0.0.1:8000/swagger/`
* Redoc: `http://127.0.0.1:8000/redoc/`


## 12. Uso de la API
Para comenzar a utilizar la API, el usuario primero deberá registrarse y seguidamente realizar el login.<br>
Luego podrá crear short URLs con IDs aleatorios o personalizados.<br>
En caso de que el token de acceso expire, podrá obtener un token de acceso nuevo.<br>
Finalmente, cualquier usuario que acceda a la short URL será redireccionado a la URL original.

### Registro de Usuario

POST `/api/auth/register/`

```json
{
  "email": "usuario@example.com",
  "password1": "pass1234!",
  "password2": "pass1234!"
}
```

### Login y obtención de tokens JWT

POST `/api/auth/login/`

```json
{
  "email": "usuario@example.com",
  "password": "pass1234!"
}
```

Respuesta:

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### Obtener un nuevo token de acceso

POST `/api/auth/token-refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

Respuesta:

```json
{
  "access": "<access_token>"
}
```

### Crear short URL 

Para crear una short URL se usa el endpoint `/api/shortener/`. El body debe contener:
- `url` (obligatorio): debe ser una URL válida.
- `short_url` (opcional): string de máximo 10 caracteres.

Comportamiento:
- Si `short_url` no está presente, es un string vacío o `null`, se genera una short URL aleatoria.
- Si `short_url` está presente y es válido, se intentará crear la short URL con ese valor.

POST `/api/shortener/`
Headers:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

Body:

```json
{
  "url": "https://www.ejemplo.com/enlace-largo",
  "short_url": ""
}
```

Respuesta:

```json
{
  "url": "https://www.ejemplo.com/enlace-largo",
  "short_url": "http://127.0.0.1:8000/as2dD37F"
}
```

### Redirigir a URL original

GET `http://127.0.0.1:8000/<short_id>/`

Ejemplo:

`http://127.0.0.1:8000/as2dD37F/`

Esto redirige automáticamente al enlace original.



## 13. Logs
Los logs se generan en la carpeta `log/`:

* `shortener.log`: eventos relacionados con el acortador de URLs
* `auth.log`: eventos de autenticación

## 14. Postman
En el directorio `docs/postman/` puede encontrar colleciones de Postman disponibles para probar la API:
- Auth.postman_collection.json
- Shortener.postman_collection.json
- workspace.postman_globals.json

## 15. Archivos útiles

* `.env.example`: ejemplo de variables de entorno
* `docs/README.md`: documentación correspondiente a las tecnologías utilizadas
* `docs/postman`: collecciones de Postman para probar la API
* `docker-compose.yaml`: para levantar con Docker

## 16. Despliegue en Producción (opcional)

Este proyecto puede desplegarse en producción utilizando servicios como:
- Railway, Render, Heroku, Fly.io
- VPS con Nginx y Gunicorn/Daphne
- Docker + Docker Compose + PostgreSQL + Redis

Se recomienda usar HTTPS, configurar correctamente `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`,
`CSRF_TRUSTED_ORIGINS`, `DEBUG=False`, `ENVIRONMENT=production` y proteger el archivo `.env`.