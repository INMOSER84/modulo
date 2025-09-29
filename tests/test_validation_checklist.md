# Lista de Verificación de Pruebas - Módulo de Gestión de Servicios

Este documento proporciona una lista de verificación exhaustiva para validar la funcionalidad del módulo de Órdenes de Servicio en Odoo 17.

## 1. Pruebas de Orden de Servicio

### 1.1. Creación de Orden de Servicio
- [ ] Crear una orden de servicio con campos obligatorios únicamente
  - [ ] Verificar que se genera automáticamente el nombre/sequencia
  - [ ] Verificar estado inicial (borrador)
  - [ ] Verificar que se guarden correctamente los datos

- [ ] Crear una orden de servicio con todos los campos
  - [ ] Incluir descripción detallada
  - [ ] Incluir fechas programadas
  - [ ] Incluir ubicación
  - [ ] Incluir prioridad

- [ ] Crear una orden de servicio con líneas de refacción
  - [ ] Agregar múltiples líneas de refacción
  - [ ] Verificar cálculo de subtotal por línea
  - [ ] Verificar cálculo de total general
  - [ ] Modificar cantidades y precios
  - [ ] Eliminar líneas de refacción

- [ ] Crear una orden de servicio con equipo
  - [ ] Seleccionar equipo existente
  - [ ] Crear nuevo equipo desde la orden
  - [ ] Verificar que se muestre la información del equipo

- [ ] Crear una orden de servicio sin equipo (si no es requerido)
  - [ ] Verificar que el sistema permite guardar sin equipo

- [ ] Crear una orden de servicio con técnico asignado
  - [ ] Seleccionar técnico existente
  - [ ] Verificar disponibilidad del técnico
  - [ ] Verificar que se muestre la información del técnico

- [ ] Crear una orden de servicio sin técnico (si no es requerido)
  - [ ] Verificar que el sistema permite guardar sin técnico

### 1.2. Flujo de Trabajo de Orden de Servicio
- [ ] Transición de Borrador a Programada
  - [ ] Verificar cambio de estado
  - [ ] Verificar fecha de programación
  - [ ] Verificar notificaciones generadas

- [ ] Transición de Programada a En Progreso
  - [ ] Verificar cambio de estado
  - [ ] Verificar fecha de inicio
  - [ ] Verificar notificaciones generadas

- [ ] Transición de En Progreso a Completada
  - [ ] Verificar cambio de estado
  - [ ] Verificar fecha de completado
  - [ ] Verificar notas de completado
  - [ ] Verificar notificaciones generadas

- [ ] Cancelar orden en cualquier estado
  - [ ] Cancelar desde borrador
  - [ ] Cancelar desde programada
  - [ ] Cancelar desde en progreso
  - [ ] Verificar que no se puede cancelar desde completada

### 1.3. Acciones de Orden de Servicio
- [ ] Programar orden de servicio
  - [ ] Verificar disponibilidad de técnico
  - [ ] Verificar conflictos de programación
  - [ ] Enviar notificación al cliente

- [ ] Iniciar orden de servicio
  - [ ] Verificar que solo se pueda iniciar si está programada
  - [ ] Registrar fecha y hora de inicio
  - [ ] Enviar notificación al cliente

- [ ] Completar orden de servicio (con asistente)
  - [ ] Completar con notas
  - [ ] Completar sin notas
  - [ ] Adjuntar evidencias (fotos, documentos)
  - [ ] Registrar firma digital del cliente
  - [ ] Generar certificado de servicio

- [ ] Cancelar orden de servicio
  - [ ] Cancelar con motivo
  - [ ] Cancelar sin motivo
  - [ ] Enviar notificación al cliente

- [ ] Reprogramar orden de servicio (con asistente)
  - [ ] Cambiar fecha y hora
  - [ ] Cambiar técnico
  - [ ] Registrar motivo de reprogramación
  - [ ] Enviar notificación al cliente

- [ ] Crear factura desde orden de servicio
  - [ ] Facturar servicio principal
  - [ ] Facturar líneas de refacción
  - [ ] Facturar todo junto
  - [ ] Verificar que la orden se marque como facturada

- [ ] Imprimir orden de servicio
  - [ ] Imprimir en formato PDF
  - [ ] Verificar contenido del reporte
  - [ ] Enviar por correo electrónico

- [ ] Imprimir certificado de servicio
  - [ ] Imprimir en formato PDF
  - [ ] Verificar contenido del reporte
  - [ ] Enviar por correo electrónico

## 2. Pruebas de Equipo

### 2.1. Creación de Equipo
- [ ] Crear equipo con campos obligatorios únicamente
  - [ ] Verificar que se genera automáticamente el nombre/sequencia
  - [ ] Verificar que se guarde correctamente

- [ ] Crear equipo con todos los campos
  - [ ] Incluir información detallada
  - [ ] Incluir información de garantía
  - [ ] Incluir intervalo de servicio
  - [ ] Incluir fotos del equipo

- [ ] Crear equipo con información de garantía
  - [ ] Establecer fecha de inicio de garantía
  - [ ] Establecer fecha de fin de garantía
  - [ ] Verificar cálculo de estado de garantía

- [ ] Crear equipo con intervalo de servicio
  - [ ] Establecer intervalo en días
  - [ ] Verificar cálculo de próxima fecha de servicio

### 2.2. Acciones de Equipo
- [ ] Programar servicio para equipo
  - [ ] Crear orden de servicio desde equipo
  - [ ] Verificar que se preseleccione el equipo
  - [ ] Verificar que se muestre el historial de servicios

- [ ] Ver historial de servicio de equipo
  - [ ] Verificar que se muestren todas las órdenes de servicio
  - [ ] Verificar que se muestren las fechas de servicio
  - [ ] Verificar que se muestren los técnicos asignados

- [ ] Imprimir historial de equipo
  - [ ] Imprimir en formato PDF
  - [ ] Verificar contenido del reporte
  - [ ] Enviar por correo electrónico

### 2.3. Código QR de Equipo
- [ ] Generar código QR
  - [ ] Verificar que se genere automáticamente al crear
  - [ ] Regenerar código QR manualmente
  - [ ] Verificar que el código QR contenga la información correcta

- [ ] Escanear código QR
  - [ ] Verificar que redirija a la página del equipo
  - [ ] Verificar que muestre la información correcta
  - [ ] Verificar que funcione desde dispositivos móviles

## 3. Pruebas de Tipo de Servicio

### 3.1. Creación de Tipo de Servicio
- [ ] Crear tipo de servicio con campos obligatorios únicamente
  - [ ] Verificar que se guarde correctamente

- [ ] Crear tipo de servicio con todos los campos
  - [ ] Incluir descripción detallada
  - [ ] Establecer duración predeterminada
  - [ ] Configurar si requiere equipo
  - [ ] Configurar si requiere técnico
  - [ ] Asociar producto relacionado

### 3.2. Acciones de Tipo de Servicio
- [ ] Ver órdenes de servicio por tipo
  - [ ] Filtrar órdenes por tipo de servicio
  - [ ] Verificar que se muestren las órdenes correctas
  - [ ] Verificar que se muestren las estadísticas

## 4. Pruebas de Integración

### 4.1. Integración Contable
- [ ] Crear factura desde orden de servicio
  - [ ] Facturar servicio principal
  - [ ] Facturar líneas de refacción
  - [ ] Facturar todo junto
  - [ ] Verificar que se generen las líneas de factura correctas
  - [ ] Verificar que se calculen los importes correctos
  - [ ] Verificar que la orden se marque como facturada

- [ ] Crear factura de proveedor para línea de refacción
  - [ ] Seleccionar proveedor
  - [ ] Verificar que se generen las líneas de factura correctas
  - [ ] Verificar que se calculen los importes correctos

### 4.2. Integración de RRHH
- [ ] Asignar técnico a orden de servicio
  - [ ] Seleccionar técnico existente
  - [ ] Verificar disponibilidad del técnico
  - [ ] Verificar que se actualice la agenda del técnico

- [ ] Verificar disponibilidad de técnico
  - [ ] Verificar disponibilidad en fecha específica
  - [ ] Verificar disponibilidad en rango de fechas
  - [ ] Verificar que se muestren los horarios ocupados

- [ ] Programar orden de servicio
  - [ ] Verificar que se actualice la agenda del técnico
  - [ ] Verificar que se envíe notificación al técnico
  - [ ] Verificar que se genere un evento en el calendario

- [ ] Encontrar siguiente espacio disponible
  - [ ] Buscar espacio para servicio de duración específica
  - [ ] Verificar que se muestren los espacios disponibles
  - [ ] Seleccionar espacio y asignar a orden de servicio

### 4.3. Integración de Inventario
- [ ] Verificar disponibilidad de producto
  - [ ] Verificar stock actual
  - [ ] Verificar stock comprometido
  - [ ] Verificar stock disponible

- [ ] Reservar producto para servicio
  - [ ] Reservar cantidad específica
  - [ ] Verificar que se actualice el stock comprometido
  - [ ] Verificar que se genere un movimiento de stock

- [ ] Consumir producto para servicio
  - [ ] Consumir cantidad específica
  - [ ] Verificar que se actualice el stock actual
  - [ ] Verificar que se genere un movimiento de stock
  - [ ] Verificar que se registre el consumo en la orden de servicio

- [ ] Devolver producto desde servicio
  - [ ] Devolver cantidad específica
  - [ ] Verificar que se actualice el stock actual
  - [ ] Verificar que se genere un movimiento de stock
  - [ ] Verificar que se registre la devolución en la orden de servicio

## 5. Pruebas de Lógica de Negocio

### 5.1. Validar Orden de Servicio
- [ ] Validar orden de servicio completa
  - [ ] Verificar que no haya errores de validación
  - [ ] Verificar que se cumplan todas las reglas de negocio

- [ ] Validar orden de servicio con campos obligatorios faltantes
  - [ ] Verificar que se muestren los errores correctos
  - [ ] Verificar que no se permita guardar

- [ ] Validar orden de servicio con desajuste de propietario de equipo
  - [ ] Verificar que se muestre el error correcto
  - [ ] Verificar que no se permita guardar

### 5.2. Calcular Duración de Servicio
- [ ] Calcular duración base
  - [ ] Verificar que se use la duración del tipo de servicio
  - [ ] Verificar que se calcule correctamente

- [ ] Calcular duración con líneas de refacción
  - [ ] Verificar que se sume el tiempo adicional por línea
  - [ ] Verificar que se calcule correctamente

- [ ] Calcular duración con factor de prioridad
  - [ ] Verificar que se aplique el factor correcto según prioridad
  - [ ] Verificar que se calcule correctamente

### 5.3. Verificar Conflictos de Orden de Servicio
- [ ] Verificar conflicto de técnico
  - [ ] Programar dos servicios para el mismo técnico al mismo tiempo
  - [ ] Verificar que se detecte el conflicto
  - [ ] Verificar que se muestre una advertencia

- [ ] Verificar conflicto de equipo
  - [ ] Programar dos servicios para el mismo equipo al mismo tiempo
  - [ ] Verificar que se detecte el conflicto
  - [ ] Verificar que se muestre una advertencia

## 6. Pruebas de Portal

### 6.1. Portal de Cliente
- [ ] Ver órdenes de servicio
  - [ ] Verificar que se muestren las órdenes del cliente
  - [ ] Verificar que se pueda filtrar por estado
  - [ ] Verificar que se pueda ordenar por fecha

- [ ] Ver detalles de orden de servicio
  - [ ] Verificar que se muestren todos los detalles
  - [ ] Verificar que se muestren las líneas de refacción
  - [ ] Verificar que se muestre la información del técnico
  - [ ] Verificar que se muestre la información del equipo

- [ ] Aceptar orden de servicio
  - [ ] Aceptar orden pendiente
  - [ ] Verificar que cambie el estado
  - [ ] Verificar que se envíe una notificación

- [ ] Cancelar orden de servicio
  - [ ] Cancelar orden pendiente
  - [ ] Verificar que cambie el estado
  - [ ] Verificar que se envíe una notificación

## 7. Pruebas de Seguridad

### 7.1. Permisos de Usuario
- [ ] Verificar permisos de usuario básico
  - [ ] Verificar que pueda ver sus propias órdenes
  - [ ] Verificar que no pueda ver órdenes de otros usuarios
  - [ ] Verificar que pueda crear órdenes
  - [ ] Verificar que pueda editar sus propias órdenes
  - [ ] Verificar que no pueda editar órdenes de otros usuarios

- [ ] Verificar permisos de técnico
  - [ ] Verificar que pueda ver las órdenes asignadas
  - [ ] Verificar que pueda editar las órdenes asignadas
  - [ ] Verificar que no pueda ver órdenes no asignadas
  - [ ] Verificar que no pueda editar órdenes no asignadas

- [ ] Verificar permisos de supervisor
  - [ ] Verificar que pueda ver todas las órdenes
  - [ ] Verificar que pueda editar todas las órdenes
  - [ ] Verificar que pueda asignar técnicos
  - [ ] Verificar que pueda programar servicios

- [ ] Verificar permisos de administrador
  - [ ] Verificar que pueda ver todas las órdenes
  - [ ] Verificar que pueda editar todas las órdenes
  - [ ] Verificar que pueda configurar el módulo
  - [ ] Verificar que pueda eliminar órdenes

### 7.2. Reglas de Registro
- [ ] Verificar reglas de usuario básico
  - [ ] Verificar que solo vea sus propias órdenes
  - [ ] Verificar que solo vea equipos de sus clientes

- [ ] Verificar reglas de técnico
  - [ ] Verificar que solo vea órdenes asignadas
  - [ ] Verificar que solo vea equipos de sus órdenes asignadas

- [ ] Verificar reglas de supervisor
  - [ ] Verificar que vea todas las órdenes
  - [ ] Verificar que vea todos los equipos

## 8. Pruebas de Interfaz de Usuario

### 8.1. Vistas de Orden de Servicio
- [ ] Vista de lista
  - [ ] Verificar que se muestren los campos correctos
  - [ ] Verificar que funcionen los filtros
  - [ ] Verificar que funcionen los agrupadores
  - [ ] Verificar que funcionen los botones de acción

- [ ] Vista de formulario
  - [ ] Verificar que se muestren todos los campos
  - [ ] Verificar que funcionen los botones de estado
  - [ ] Verificar que funcionen los botones de acción
  - [ ] Verificar que funcionen las pestañas

- [ ] Vista Kanban
  - [ ] Verificar que se muestren las tarjetas correctamente
  - [ ] Verificar que funcionen los botones de estado
  - [ ] Verificar que funcionen los botones de acción

- [ ] Vista de calendario
  - [ ] Verificar que se muestren los eventos correctamente
  - [ ] Verificar que funcionen los filtros
  - [ ] Verificar que funcionen los botones de navegación
  - [ ] Verificar que se pueda arrastrar y soltar eventos

### 8.2. Vistas de Equipo
- [ ] Vista de lista
  - [ ] Verificar que se muestren los campos correctos
  - [ ] Verificar que funcionen los filtros
  - [ ] Verificar que funcionen los agrupadores
  - [ ] Verificar que funcionen los botones de acción

- [ ] Vista de formulario
  - [ ] Verificar que se muestren todos los campos
  - [ ] Verificar que funcionen los botones de acción
  - [ ] Verificar que funcionen las pestañas
  - [ ] Verificar que se muestre el código QR

## 9. Pruebas de Reportes

### 9.1. Reportes de Orden de Servicio
- [ ] Reporte de orden de servicio
  - [ ] Verificar que se muestren todos los datos
  - [ ] Verificar que se muestre el logo de la empresa
  - [ ] Verificar que se muestren las líneas de refacción
  - [ ] Verificar que se muestre la información del técnico
  - [ ] Verificar que se muestre la información del equipo

- [ ] Certificado de servicio
  - [ ] Verificar que se muestren todos los datos
  - [ ] Verificar que se muestre el logo de la empresa
  - [ ] Verificar que se muestren las firmas
  - [ ] Verificar que se muestren las evidencias

### 9.2. Reportes de Equipo
- [ ] Reporte de historial de equipo
  - [ ] Verificar que se muestren todos los datos
  - [ ] Verificar que se muestre el logo de la empresa
  - [ ] Verificar que se muestren las órdenes de servicio
  - [ ] Verificar que se muestren las fechas de servicio

### 9.3. Reportes Estadísticos
- [ ] Reporte de servicios por técnico
  - [ ] Verificar que se muestren los datos correctos
  - [ ] Verificar que se puedan filtrar por fecha
  - [ ] Verificar que se puedan agrupar por técnico

- [ ] Reporte de servicios por tipo
  - [ ] Verificar que se muestren los datos correctos
  - [ ] Verificar que se puedan filtrar por fecha
  - [ ] Verificar que se puedan agrupar por tipo

- [ ] Reporte de servicios por cliente
  - [ ] Verificar que se muestren los datos correctos
  - [ ] Verificar que se puedan filtrar por fecha
  - [ ] Verificar que se puedan agrupar por cliente

## 10. Pruebas de API

### 10.1. API de Estado de Orden de Servicio
- [ ] Obtener estado de orden de servicio
  - [ ] Verificar que se devuelva el estado correcto
  - [ ] Verificar que se manejen errores correctamente

- [ ] Actualizar estado de orden de servicio
  - [ ] Verificar que se actualice el estado correctamente
  - [ ] Verificar que se manejen errores correctamente
  - [ ] Verificar que se generen las notificaciones correctas

### 10.2. API de Creación de Orden de Servicio
- [ ] Crear orden de servicio
  - [ ] Verificar que se cree correctamente
  - [ ] Verificar que se manejen errores correctamente
  - [ ] Verificar que se generen las notificaciones correctas

## 11. Pruebas de Rendimiento

### 11.1. Rendimiento de Operaciones Básicas
- [ ] Rendimiento de creación de orden de servicio
  - [ ] Medir tiempo de creación con datos mínimos
  - [ ] Medir tiempo de creación con todos los datos
  - [ ] Medir tiempo de creación con múltiples líneas de refacción

- [ ] Rendimiento de flujo de trabajo de orden de servicio
  - [ ] Medir tiempo de transición entre estados
  - [ ] Medir tiempo de completado con asistente
  - [ ] Medir tiempo de reprogramación con asistente

### 11.2. Rendimiento de Listados y Búsquedas
- [ ] Rendimiento de lista de órdenes de servicio
  - [ ] Medir tiempo de carga con 100 registros
  - [ ] Medir tiempo de carga con 1,000 registros
  - [ ] Medir tiempo de carga con 10,000 registros

- [ ] Rendimiento de búsqueda de órdenes de servicio
  - [ ] Medir tiempo de búsqueda por nombre
  - [ ] Medir tiempo de búsqueda por cliente
  - [ ] Medir tiempo de búsqueda por técnico

### 11.3. Rendimiento de Reportes
- [ ] Rendimiento de generación de reportes
  - [ ] Medir tiempo de generación de reporte de orden de servicio
  - [ ] Medir tiempo de generación de reporte de historial de equipo
  - [ ] Medir tiempo de generación de reportes estadísticos

## 12. Pruebas de Compatibilidad

### 12.1. Compatibilidad con Navegadores
- [ ] Verificar funcionamiento en Google Chrome
- [ ] Verificar funcionamiento en Mozilla Firefox
- [ ] Verificar funcionamiento en Microsoft Edge
- [ ] Verificar funcionamiento en Safari

### 12.2. Compatibilidad con Dispositivos
- [ ] Verificar funcionamiento en escritorio
- [ ] Verificar funcionamiento en tabletas
- [ ] Verificar funcionamiento en teléfonos móviles

### 12.3. Compatibilidad con Versiones de Odoo
- [ ] Verificar funcionamiento en Odoo 17 Community
- [ ] Verificar funcionamiento en Odoo 17 Enterprise
