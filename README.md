# Módulo Inmoser Service Management

## Descripción

Este módulo proporciona un sistema completo de gestión de órdenes de servicio para empresas de servicios técnicos. Está diseñado para optimizar y automatizar todo el proceso de gestión de servicios técnicos, desde la creación de la orden hasta la facturación y el seguimiento del historial de mantenimiento.

## Características Principales

### Gestión de Órdenes de Servicio
- Creación y seguimiento de órdenes de servicio
- Flujo de trabajo completo: Borrador → Programado → En Progreso → Completado → Cancelado
- Asignación automática y manual de técnicos
- Programación con calendario interactivo
- Gestión de prioridades y urgencias
- Control de tiempos y fechas

### Gestión de Equipos
- Registro completo de equipos por cliente
- Historial de mantenimiento y servicios realizados
- Generación automática de códigos QR
- Control de garantías y fechas de vencimiento
- Programación automática de mantenimiento preventivo
- Documentación adjunta (fotos, manuales, etc.)

### Portal del Cliente
- Acceso seguro para clientes
- Visualización de órdenes de servicio
- Aprobación o cancelación de servicios
- Descarga de certificados y reportes
- Seguimiento en tiempo real del estado del servicio

### Integraciones
- **Contabilidad**: Facturación automática desde órdenes de servicio
- **Inventario**: Control de refacciones y materiales utilizados
- **Recursos Humanos**: Gestión de técnicos y horarios
- **Calendario**: Vista mensual/semanal/diaria de servicios
- **Contactos**: Integración con clientes y proveedores

### Reportes y Análisis
- Reportes de órdenes de servicio por técnico
- Reportes de rendimiento y productividad
- Reportes de historial de equipos
- Certificados de servicio personalizados
- Análisis de tiempos y costos
- Dashboard con indicadores clave (KPIs)

## Requisitos

- Odoo 17 Community o Enterprise
- Módulos base: web, mail, account, stock, hr, portal, calendar, product, contacts
- Python: librería `qrcode` (se instala automáticamente)

## Instalación

1. Descargar el módulo y colocarlo en la carpeta `addons` de Odoo
2. Actualizar la lista de módulos en Odoo
3. Buscar "Inmoser Service Management" en la lista de aplicaciones
4. Hacer clic en "Instalar"

## Configuración Inicial

### 1. Crear Tipos de Servicio
1. Ir a `Servicios > Configuración > Tipos de Servicio`
2. Crear los tipos de servicio que ofrece su empresa
3. Configurar duración, requisitos de equipo/técnico, etc.

### 2. Configurar Técnicos
1. Ir a `Recursos Humanos > Empleados`
2. Seleccionar los empleados que serán técnicos
3. Marcar la opción "Es técnico" en la ficha del empleado
4. Configurar horarios y disponibilidad

### 3. Configurar Secuencias
1. Ir a `Configuración > Técnico > Secuencias`
2. Verificar que las secuencias para órdenes de servicio estén configuradas
3. Ajustar prefijos y formatos según necesidad

### 4. Configurar Plantillas de Correo
1. Ir a `Configuración > Técnico > Plantillas de Correo`
2. Revisar y personalizar las plantillas de notificación
3. Configurar remitentes y destinatarios por defecto

## Uso del Módulo

### Crear una Orden de Servicio

1. **Desde el menú principal**:
   - Ir a `Servicios > Órdenes de Servicio`
   - Hacer clic en `Crear`

2. **Desde un cliente**:
   - Ir a la ficha del cliente
   - En la pestaña `Servicios`, hacer clic en `Crear Orden de Servicio`

3. **Desde un equipo**:
   - Ir a la ficha del equipo
   - Hacer clic en `Programar Servicio`

4. **Completar los datos**:
   - Seleccionar el cliente
   - Seleccionar el tipo de servicio
   - Asignar técnico (opcional, puede asignarse automáticamente)
   - Seleccionar equipo (si aplica)
   - Agregar descripción y detalles adicionales
   - Programar fecha y hora

### Gestión del Flujo de Trabajo

1. **Programar**:
   - Una vez creada la orden, hacer clic en `Programar`
   - El sistema verificará disponibilidad del técnico
   - Se enviará notificación al cliente y técnico

2. **Iniciar Servicio**:
   - Cuando el técnico llega al lugar, hacer clic en `Iniciar`
   - Se registrará la hora de inicio
   - El técnico puede agregar notas y fotos desde móvil

3. **Completar Servicio**:
   - Al finalizar, hacer clic en `Completar`
   - Llenar el asistente con:
     - Fecha y hora de completado
     - Notas del servicio
     - Refacciones utilizadas
     - Evidencias (fotos antes/después)
     - Firma digital del cliente
   - Generar certificado de servicio

4. **Facturar**:
   - Desde la orden completada, hacer clic en `Crear Factura`
   - Se generará una factura con el servicio y refacciones
   - Revisar y confirmar la factura

### Gestión de Equipos

1. **Crear un Equipo**:
   - Ir a `Servicios > Equipos`
   - Hacer clic en `Crear`
   - Ingresar datos del equipo:
     - Nombre y número de serie
     - Marca y modelo
     - Cliente propietario
     - Fecha de instalación
     - Período de garantía
     - Intervalo de mantenimiento

2. **Generar Código QR**:
   - Desde la ficha del equipo, hacer clic en `Generar QR`
   - Se generará automáticamente un código QR
   - Imprimir y pegar en el equipo físico

3. **Ver Historial**:
   - Desde la ficha del equipo, ir a la pestaña `Historial de Servicios`
   - Ver todos los servicios realizados
   - Descargar reporte de historial

### Portal del Cliente

1. **Acceso del Cliente**:
   - Enviar invitación desde la ficha del cliente
   - El cliente recibirá un correo con enlace de acceso
   - Podrá crear su propia contraseña

2. **Funcionalidades del Portal**:
   - Ver todas sus órdenes de servicio
   - Aprobar o cancelar servicios pendientes
   - Descargar certificados y reportes
   - Ver información de sus equipos
   - Escanear códigos QR para ver detalles

## Personalización

### Campos Personalizados

El módulo permite agregar campos personalizados a:

- Órdenes de servicio
- Equipos
- Tipos de servicio
- Líneas de refacción

Para agregar campos personalizados:

1. Ir a `Configuración > Técnico > Campos Personalizados`
2. Crear nuevo campo
3. Seleccionar el modelo al que se aplicará
4. Configurar tipo y opciones

### Reportes Personalizados

Para personalizar reportes:

1. Ir a `Configuración > Técnico > Reportes`
2. Seleccionar el reporte a modificar
3. Usar el editor de plantillas QWeb
4. Agregar o modificar campos y diseño

### Flujos de Trabajo Personalizados

Para modificar flujos de trabajo:

1. Ir a `Configuración > Técnico > Flujos de Trabajo`
2. Seleccionar el flujo a modificar
3. Agregar o eliminar estados
4. Configurar transiciones y condiciones

## Solución de Problemas

### Problemas Comunes

**El técnico no aparece en la lista de asignación**:
- Verificar que el empleado esté marcado como "Es técnico"
- Comprobar que tenga un usuario asociado
- Verificar permisos de seguridad

**No se puede programar una orden de servicio**:
- Verificar que el técnico tenga disponibilidad
- Comprobar que no haya conflictos de horario
- Revisar que la orden tenga todos los campos requeridos

**El código QR no se genera**:
- Verificar que el equipo tenga número de serie
- Comprobar permisos de escritura
- Revisar la configuración de la librería qrcode

**Las notificaciones no se envían**:
- Verificar configuración del servidor de correo
- Comprobar plantillas de correo
- Revisar cola de correos pendientes

### Obtener Ayuda

- **Documentación**: [Wiki del proyecto](https://github.com/INMOSER84/inmoser_service_order/wiki)
- **Reportar Issues**: [GitHub Issues](https://github.com/INMOSER84/inmoser_service_order/issues)
- **Soporte Comercial**: [Contactar](mailto:soporte@inmoser.com)

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Hacer un Fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia Pública General Reducida de GNU v3.0. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Créditos

- **Desarrollador**: INMOSER84
- **Contribuyentes**: [Lista de contribuyentes](https://github.com/INMOSER84/inmoser_service_order/contributors)
- **Iconos**: [Font Awesome](https://fontawesome.com/)

## Changelog

### v17.0.1.0.0 (2023-12-01)
- Versión inicial para Odoo 17
- Implementación de todas las características principales
- Integración con módulos base de Odoo
- Documentación completa

---

**Nota**: Este módulo está en fase Beta. Se recomienda probarlo en un entorno de desarrollo antes de usarlo en producción.
