# URL Shortener — Justificación técnica y solución propuesta

## Tecnologías utilizadas

- **Framework web:** Django + Django REST Framework (DRF).  
  - Django ofrece un sistema maduro y seguro para desarrollo web, con gestión de usuarios, seguridad integrada (CSRF, XSS), ORM potente y escalable, panel de admin automático, entre otras cosas.  
  - DRF permite construir APIs RESTful limpias y fáciles de documentar.  
  - Django posee muchas cosas ya desarrolladas, lo que permite enfocarse en la lógica de negocio.
- **Cache:** Redis para cachear URLs acortadas, mejorando rendimiento y reduciendo carga en la base de datos.  
- **Autenticación:** JWT (SimpleJWT), para manejo seguro y escalable de autenticación en API.  
- **Documentación:** Swagger (drf_yasg), para facilitar el consumo y testeo de la API.  
- **Rate limiting:** django-ratelimit para proteger endpoints de ataques de fuerza bruta o abuso.

Esta combinación garantiza seguridad, rendimiento y escalabilidad.

## Framework elegido y ventajas

Django es un framework muy robusto que acelera el desarrollo sin sacrificar control ni seguridad. 
Incluye un ORM robusto que permite interactuar con la base de datos usando Python en lugar de SQL crudo, lo que reduce significativamente el riesgo de ataques por inyección SQL.  
DRF simplifica la exposición de APIs limpias y permite fácil integración con clientes web o móviles.
También, en caso de ser necesario, es posible utilizar plantillas para desarrollar Frontend.

Además, la comunidad y documentación son una gran ventaja para resolver problemas.

## Consideraciones de seguridad

- Validación rigurosa en serializers para inputs (email, password, URLs).  
- Protección CSRF y XSS activadas por defecto en Django.  
- Hashing seguro de contraseñas con el sistema nativo de Django (PBKDF2 por defecto).  
- Uso de JWT con expiración y blacklist para controlar tokens activos y revocados.  
- Rate limiting por IP para endpoints para evitar abuso o ataques de fuerza bruta.  
- Headers de seguridad y uso HTTPS en producción.  
- Validación estricta para URLs acortadas para evitar inyección o caracteres inválidos.  

## Manejo de colisiones en SHORT IDs

- Generación de IDs aleatorios de longitud configurable. Por defecto 8 caracteres alfanuméricos, máximo 10.  
- Validación al generar para evitar colisiones: si el SHORT ID generado existe, se genera uno nuevo hasta que sea único.  
- Algoritmo simple pero eficiente, dado el tamaño del espacio de IDs, reduce la probabilidad de colisiones a valores muy pequeños. Por ejemplo, tomando 8 caracteres alfanuméricos (o base 62), se tienen 2.18×10^14 combinaciones posibles.
- Opcionalmente, se podría extender para usar algoritmos más sofisticados como por ejemplo, base62 + timestamp + hash parcial, timestamp + primary key (PK) con operaciones de bit shifting.

## Robustez y escalabilidad

- Cache con Redis para acelerar redirecciones, evitar consultas repetidas a la DB.  
- Rate limiting para mitigar abusos y ataques DDoS básicos.  
- Uso de base de datos relacional con migraciones y posibilidad de escalar a DB dedicadas.  
- Código modular, probado y documentado para facilitar mantenimiento y escalabilidad.  
- Preparado para deploy en entornos cloud con configuración por variables de entorno y contenedores Docker.   








# Justificación Técnica del Proyecto - Acortador de URLs

## Lenguaje y Framework

**Python + Django**

Elegí Django como framework principal por las siguientes razones:

- Tiene una arquitectura robusta que permite un desarrollo rápido y seguro.
- Incluye muchas herramientas integradas (ORM, autenticación, middleware, gestión de usuarios).
- Su ecosistema es maduro, mantenido y ampliamente documentado.
- Django REST Framework facilita la creación de APIs modernas, seguras y bien documentadas.

---

## Base de Datos

**SQLite para desarrollo / PostgreSQL para producción**

- En desarrollo se utiliza SQLite por simplicidad.
- En producción se puede habilitar PostgreSQL fácilmente vía variables de entorno.
- PostgreSQL es confiable, escalable y ampliamente soportado en entornos cloud y Docker.

---

## Cache y Rendimiento

**Redis (opcional, altamente recomendado)**

- Utilizado para cachear resultados de redirecciones.
- Minimiza consultas a base de datos y mejora tiempos de respuesta.
- También se usa como backend para aplicar límites de tasa (rate limiting).

---

## Seguridad

- Autenticación basada en JWT con **SimpleJWT**.
- Protección contra ataques:
  - CSRF y CORS configurables por entorno.
  - Rate limiting por IP para endpoints sensibles.
  - Validación robusta de URLs (evita entradas maliciosas).
  - XSS y Clickjacking mitigados con configuración de seguridad en middleware.

---

## Prevención de Colisiones en IDs

- Los IDs cortos generados tienen una longitud configurable (por defecto 8 caracteres alfanuméricos, 62 posibles por carácter).
- Eso brinda un espacio de búsqueda de `62^8 ≈ 218 billones de combinaciones únicas`.
- En caso de colisión, se vuelve a intentar la generación (retry loop controlado).
- Se podría migrar a esquemas más sofisticados (hashes, algoritmos distribuidos) si se alcanzaran límites.

---

## Documentación

- La API se documenta automáticamente con **Swagger** y **ReDoc**, disponibles en:
  - `/swagger/`
  - `/redoc/`
- También se incluye una colección de Postman exportada en la carpeta `docs/`.

---

## Despliegue y Contenedores

- Proyecto preparado para ser ejecutado con Docker y Docker Compose.
- Separación de servicios (Django, Redis, PostgreSQL).
- Variables de entorno controlan el comportamiento del entorno (`.env.example` incluido).

---

## Logging

- Se implementó logging a archivos separados (`auth.log`, `shortener.log`).
- Permite trazabilidad de acciones importantes: creación de usuarios, login, redirecciones, fallas.
- Pensado para ser compatible con sistemas de monitoreo/logging centralizado (ej: ELK Stack).

---

## Escalabilidad y Volumen de Tráfico

Se consideró como “gran volumen de tráfico” un escenario donde el servicio debe manejar:

- **Decenas de miles de redirecciones por minuto**
- **Miles de URLs nuevas por hora**
- **Hasta millones de requests diarios**

Por eso, la solución incluye:

- Cache con Redis para acelerar las redirecciones
- Rate limiting configurable para evitar abuso
- Persistencia en PostgreSQL (que puede escalarse horizontalmente)
- Contenedores separados, permitiendo escalar servicios de forma independiente (por ejemplo: varios workers de redirección)
- Configuraciones de seguridad para exposición pública

---

## Conclusión

Esta arquitectura está pensada para ser **segura, performante y escalable**, con herramientas estándar de la industria y capacidad de adaptarse a escenarios reales de carga. El uso de variables de entorno, contenedores y logs controlados asegura que puede mantenerse fácilmente en producción.
