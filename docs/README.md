# URL Shortener — Detalles Técnicos
Este proyecto es un acortador de URLs expuesto como una API REST, diseñado con foco en seguridad, rendimiento, escalabilidad y facilidad de despliegue.<br>
A continuación se presentan detalles técnicos sobre las decisiones de diseño, tecnologías utilizadas y justificación de la arquitectura,

*Para más detalles sobre su Instalación y Uso consulte [Guía de Instalación y Uso](../README.md)*


## Tecnologías utilizadas
- **Lenguaje:** Python 3.12+
- **Framework web:** Django + Django REST Framework (DRF).  
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Cache:**  Redis (mejora de rendimiento y rate limiting)
- **Autenticación:** JWT (SimpleJWT)
- **Documentación:** Swagger (drf_yasg)
- **Rate limiting:** django-ratelimit para proteger endpoints de ataques de fuerza bruta o abuso.
- **Contenedores:** Docker + Docker Compose
- **Testing:** Pytest + Coverage
- **Logging:** Logs separados para autenticación y redirecciones

## Framework elegido y ventajas
Se escogió Django por ser un framework robusto, seguro y maduro para el desarrollo web. Cuenta con gestión de usuarios, seguridad integrada (CSRF, XSS), panel de administrador para gestión rápida y sencilla, entre otras cosas.
Incluye un ORM robusto que permite interactuar con la base de datos usando Python en lugar de SQL crudo, lo que reduce significativamente el riesgo de ataques por inyección SQL. 
DRF simplifica la exposición de APIs limpias y permite fácil integración con clientes web o móviles. 
También, en caso de ser necesario, Django permite utilizar plantillas para desarrollar Frontend.

## Base de Datos
**SQLite para desarrollo / PostgreSQL para producción**
Se decidió utilizar una base de datos relacional SQL debido a que el modelo de datos del sistema es altamente estructurado.
Durante el desarrollo se emplea SQLite, por su simplicidad y configuración inmediata. Opcionalmente se puede habilitar el uso de PostgreSQL en desarrollo facilmente vía variables de entorno.
Para producción, se utiliza PostgreSQL debido a que es mas robusta, ampliamente adoptada y que presenta claras ventajas sobre SQLite:
- Soporte completo de ACID, ideal para mantener la consistencia del sistema.
- Índices avanzados y validación de unicidad, necesarios para prevenir colisiones de short URLs.
- Excelente escalabilidad vertical y compatibilidad con soluciones de réplica y particionado.
- Soporte nativo en entornos Docker y cloud.

## Consideraciones de seguridad
- Validación rigurosa en serializers para inputs (email, password, URLs).  
- Protección CSRF y XSS activadas por defecto en Django.  
- Hashing seguro de contraseñas con el sistema nativo de Django (PBKDF2 por defecto).  
- Uso de JWT a trevés de SimpleJWT, con expiración, renovación y blacklist para controlar tokens activos y revocados.  
- Rate limiting por IP para endpoints para evitar abuso o ataques de fuerza bruta.  
- Headers de seguridad y uso HTTPS en producción.  
- Validación estricta para URLs acortadas para evitar inyección, caracteres inválidos o rutas protegidas.  

## Manejo de colisiones en SHORT IDs
- Generación de IDs aleatorios de longitud configurable. Por defecto 8 caracteres alfanuméricos, máximo 10.  
- Validación al generar para evitar colisiones: si el SHORT ID generado existe, se genera uno nuevo hasta que sea único.  
- Algoritmo simple pero eficiente, dado el tamaño del espacio de IDs, reduce la probabilidad de colisiones a valores muy pequeños. Por ejemplo, tomando 8 caracteres alfanuméricos (o base 62), se tienen 2.18×10^14 combinaciones posibles.
- Opcionalmente, se podría extender para usar algoritmos más sofisticados como por ejemplo, base62 + timestamp + hash parcial, timestamp + primary key (PK) con bit shifting.

## Robustez y escalabilidad
Pensando en exposición pública del servicio, el sistema se diseñó pensando en adaptarse a un escenario con un alto volumen de tráfico:
- Cache con Redis para acelerar redirecciones y evitar consultas repetidas a la DB.  
- Rate limiting para mitigar abusos y ataques DDoS básicos.  
- Uso de PostgreSQL como base de datos escalable.  
- Docker para escalar horizontalmente los servicios
- Código modular, probado y documentado para facilitar mantenimiento y escalabilidad.  

## Despliegue y Contenedores
- Proyecto dockerizado: servicios separados para Django, PostgreSQL y Redis
- .env.example para configuración por entorno 
- Soporta deploy en Railway, Render, VPS con Gunicorn + Nginx, o Docker en servidores dedicados
- Preparado para HTTPS, CORS y variables de entorno seguras

## Tests y Coverage
El proyecto incluye tests automatizados con `pytest`. Cubre:
- Registro y login de usuarios.
- Creación de URLs acortadas, con y sin colisiones, aleatorias o personalizadas.
- Redirección a URL original.
- Validaciones de serializers.

## Logging
- Se implementó logging a archivos separados:
  - `auth.log`: eventos de login, registro, errores
  - `shortener.log`: creación de short URLs, redirecciones, errores
- Permite trazabilidad de acciones importantes.

## Documentación de uso de la API
La aplicación cuenta con una documentación completa y accesible para facilitar su prueba e integración.
- En el archivo README.md del repositorio se encuentra una guía de instalación y uso paso a paso.
- La API está documentada automáticamente y expuesta mediante las siguientes rutas:
  - Swagger UI: /swagger/
  - ReDoc: /redoc/
- Además, se incluye una colección de Postman para facilitar las pruebas manuales. Está disponible en el directorio: `docs/postman/`

Esta documentación permite interactuar con la API de forma rápida, clara y consistente.

## Conclusión
Esta arquitectura está pensada para ser segura, performante y escalable, con herramientas estándar de la industria y capacidad de adaptarse a escenarios reales de carga. El uso de variables de entorno, contenedores y logs controlados asegura que puede mantenerse fácilmente en producción.