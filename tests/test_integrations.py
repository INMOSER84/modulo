# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestIntegrations(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Constantes para pruebas
        self.TEST_DATE = datetime(2023, 1, 1, 10, 0, 0)
        self.TEST_DATE_END = datetime(2023, 1, 1, 12, 0, 0)
        
        # Crear un partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
            'phone': '123456789',
            'street': 'Test Street',
            'city': 'Test City',
            'country_id': self.env.ref('base.us').id,
        })
        
        # Crear un tipo de servicio con un producto
        self.product = self.env['product.product'].create({
            'name': 'Test Service Product',
            'lst_price': 100.0,
            'type': 'service',
            'default_code': 'TS001',
            'description': 'Test service product description',
        })
        
        self.service_type = self.env['service.type'].create({
            'name': 'Test Service Type',
            'duration': 2.0,
            'equipment_required': False,
            'technician_required': True,
            'product_id': self.product.id,
            'description': 'Test service type description',
        })
        
        # Crear un técnico
        self.technician = self.env['hr.employee'].create({
            'name': 'Test Technician',
            'work_email': 'technician@example.com',
            'is_technician': True,
            'job_id': self.env.ref('hr.job_technician').id if self.env.ref('hr.job_technician', False) else False,
        })
        
        # Crear un producto para refacciones
        self.refaction_product = self.env['product.product'].create({
            'name': 'Test Refaction Product',
            'lst_price': 50.0,
            'type': 'product',
            'default_code': 'TR001',
            'description': 'Test refaction product',
        })
        
        # Crear una orden de servicio
        self.service_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
            'description': 'Test Service Order',
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
        })
        
        # Crear ubicación de inventario para pruebas
        self.stock_location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        if not self.stock_location:
            self.stock_location = self.env['stock.location'].create({
                'name': 'Test Stock Location',
                'usage': 'internal',
                'location_id': self.env.ref('stock.stock_location_locations').id,
            })

    def test_account_integration(self):
        """Probar integración contable"""
        # Agregar una línea de refacción
        self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.refaction_product.id,
            'quantity': 2.0,
            'unit_price': 50.0,
        })
        
        # Crear factura
        account_integration = self.env['account.integration']
        invoice = account_integration.create_invoice_from_service_order(self.service_order)
        
        self.assertTrue(invoice, "Factura no creada")
        self.assertEqual(invoice.partner_id, self.partner, "Cliente incorrecto en factura")
        self.assertEqual(invoice.move_type, 'out_invoice', "Tipo de factura incorrecto")
        self.assertEqual(len(invoice.invoice_line_ids), 2, "Número de líneas de factura incorrecto")
        self.assertTrue(self.service_order.is_invoiced, "Orden no marcada como facturada")
        
        # Verificar líneas de factura
        service_line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertTrue(service_line, "Línea de servicio no encontrada")
        self.assertEqual(service_line.price_unit, 100.0, "Precio de servicio incorrecto")
        
        refaction_line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.refaction_product)
        self.assertTrue(refaction_line, "Línea de refacción no encontrada")
        self.assertEqual(refaction_line.price_unit, 50.0, "Precio de refacción incorrecto")
        self.assertEqual(refaction_line.quantity, 2.0, "Cantidad de refacción incorrecta")
        
        # Probar crear factura duplicada
        with self.assertRaises(UserError):
            account_integration.create_invoice_from_service_order(self.service_order)
        
        # Probar crear factura sin líneas
        service_order_empty = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        
        invoice_empty = account_integration.create_invoice_from_service_order(service_order_empty)
        self.assertTrue(invoice_empty, "Factura vacía no creada")
        self.assertEqual(len(invoice_empty.invoice_line_ids), 1, "Número de líneas incorrecto en factura vacía")

    def test_hr_integration(self):
        """Probar integración de RRHH"""
        hr_integration = self.env['hr.integration']
        
        # Programar orden de servicio
        success = hr_integration.schedule_service_order(self.service_order)
        self.assertTrue(success, "Programación fallida")
        self.assertEqual(self.service_order.state, 'scheduled', "Estado incorrecto después de programar")
        self.assertTrue(self.service_order.scheduled_date, "Fecha de programación no establecida")
        
        # Verificar disponibilidad del técnico
        available = hr_integration.check_technician_availability(
            self.technician,
            self.service_order.scheduled_date,
            self.service_order.scheduled_date_end
        )
        self.assertFalse(available, "Técnico debería estar ocupado")
        
        # Encontrar siguiente espacio disponible
        next_slot = hr_integration.find_next_available_slot(self.technician, 2.0)
        self.assertTrue(next_slot, "No se encontró siguiente espacio disponible")
        self.assertGreater(next_slot[0], self.service_order.scheduled_date_end, 
                          "Siguiente espacio disponible incorrecto")
        
        # Probar programar en horario no laboral
        non_working_date = self.TEST_DATE.replace(hour=20, minute=0)  # 8 PM
        self.service_order.scheduled_date = non_working_date
        self.service_order.scheduled_date_end = non_working_date + timedelta(hours=2)
        
        with self.assertRaises(ValidationError):
            hr_integration.schedule_service_order(self.service_order)
        
        # Probar con técnico no disponible
        self.technician.is_available = False
        self.service_order.scheduled_date = self.TEST_DATE
        self.service_order.scheduled_date_end = self.TEST_DATE_END
        
        with self.assertRaises(ValidationError):
            hr_integration.schedule_service_order(self.service_order)
        
        # Restaurar técnico
        self.technician.is_available = True
        
        # Probar creación de asistencia
        attendance = hr_integration.create_technician_attendance(self.technician, self.service_order)
        self.assertTrue(attendance, "Asistencia no creada")
        self.assertEqual(attendance.employee_id, self.technician, "Empleado incorrecto en asistencia")
        self.assertEqual(attendance.check_in, self.service_order.scheduled_date, 
                         "Hora de entrada incorrecta en asistencia")

    def test_stock_integration(self):
        """Probar integración de inventario"""
        stock_integration = self.env['stock.integration']
        
        # Crear un producto almacenable
        stock_product = self.env['product.product'].create({
            'name': 'Test Stock Product',
            'type': 'product',
            'lst_price': 50.0,
            'default_code': 'TSP001',
        })
        
        # Crear un quant para el producto
        self.env['stock.quant'].create({
            'product_id': stock_product.id,
            'location_id': self.stock_location.id,
            'quantity': 10.0,
        })
        
        # Verificar disponibilidad del producto
        available = stock_integration.check_product_availability(stock_product, 5.0)
        self.assertTrue(available, "Producto debería estar disponible")
        
        # Reservar producto
        move = stock_integration.reserve_product_for_service(stock_product, 5.0)
        self.assertTrue(move, "Reserva no creada")
        self.assertEqual(move.product_qty, 5.0, "Cantidad reservada incorrecta")
        self.assertEqual(move.state, 'assigned', "Estado de movimiento incorrecto")
        
        # Verificar disponibilidad después de reserva
        available_after_reserve = stock_integration.check_product_availability(stock_product, 6.0)
        self.assertFalse(available_after_reserve, "Producto no debería estar disponible para 6 unidades")
        
        # Consumir producto
        consume_move = stock_integration.consume_product_for_service(stock_product, 2.0, self.service_order)
        self.assertTrue(consume_move, "Movimiento de consumo no creado")
        self.assertEqual(consume_move.product_qty, 2.0, "Cantidad consumida incorrecta")
        self.assertEqual(consume_move.state, 'done', "Estado de movimiento incorrecto")
        
        # Verificar stock después de consumo
        quant = self.env['stock.quant'].search([
            ('product_id', '=', stock_product.id),
            ('location_id', '=', self.stock_location.id),
        ])
        self.assertEqual(quant.quantity, 8.0, "Cantidad en stock incorrecta después de consumo")
        
        # Devolver producto
        return_move = stock_integration.return_product_from_service(stock_product, 1.0, self.service_order)
        self.assertTrue(return_move, "Movimiento de devolución no creado")
        self.assertEqual(return_move.product_qty, 1.0, "Cantidad devuelta incorrecta")
        self.assertEqual(return_move.state, 'done', "Estado de movimiento incorrecto")
        
        # Verificar stock después de devolución
        quant_after_return = self.env['stock.quant'].search([
            ('product_id', '=', stock_product.id),
            ('location_id', '=', self.stock_location.id),
        ])
        self.assertEqual(quant_after_return.quantity, 9.0, "Cantidad en stock incorrecta después de devolución")
        
        # Probar reserva sin stock suficiente
        with self.assertRaises(ValidationError):
            stock_integration.reserve_product_for_service(stock_product, 15.0)
        
        # Probar consumo sin reserva previa
        with self.assertRaises(ValidationError):
            stock_integration.consume_product_for_service(stock_product, 5.0, self.service_order)

    def test_project_integration(self):
        """Probar integración con proyectos"""
        project_integration = self.env['project.integration']
        
        # Crear proyecto de servicio
        project = project_integration.create_project_from_service_order(self.service_order)
        self.assertTrue(project, "Proyecto no creado")
        self.assertEqual(project.name, self.service_order.name, "Nombre de proyecto incorrecto")
        self.assertEqual(project.partner_id, self.partner, "Cliente de proyecto incorrecto")
        self.assertEqual(project.user_id, self.technician.user_id, "Responsable de proyecto incorrecto")
        
        # Crear tarea de servicio
        task = project_integration.create_task_from_service_order(self.service_order)
        self.assertTrue(task, "Tarea no creada")
        self.assertEqual(task.name, self.service_order.name, "Nombre de tarea incorrecto")
        self.assertEqual(task.project_id, project, "Proyecto de tarea incorrecto")
        self.assertEqual(task.user_id, self.technician.user_id, "Asignado de tarea incorrecto")
        
        # Actualizar progreso de tarea
        progress = project_integration.update_task_progress(task, 50.0)
        self.assertTrue(progress, "Progreso no actualizado")
        self.assertEqual(task.progress, 50.0, "Porcentaje de progreso incorrecto")
        
        # Completar tarea
        completed = project_integration.complete_task(task)
        self.assertTrue(completed, "Tarea no completada")
        self.assertEqual(task.stage_id.name, 'Done', "Etapa de tarea incorrecta")
        
        # Probar crear proyecto duplicado
        with self.assertRaises(UserError):
            project_integration.create_project_from_service_order(self.service_order)

    def test_messaging_integration(self):
        """Probar integración de mensajería"""
        messaging_integration = self.env['messaging.integration']
        
        # Enviar notificación de programación
        result = messaging_integration.send_scheduling_notification(self.service_order)
        self.assertTrue(result, "Notificación de programación no enviada")
        
        # Verificar mensaje en el chatter
        messages = self.env['mail.message'].search([
            ('model', '=', 'service.order'),
            ('res_id', '=', self.service_order.id),
            ('message_type', '=', 'notification'),
        ])
        scheduling_msg = messages.filtered(lambda m: 'scheduled' in m.body.lower())
        self.assertTrue(scheduling_msg, "Mensaje de programación no encontrado")
        
        # Enviar recordatorio
        result = messaging_integration.send_reminder(self.service_order)
        self.assertTrue(result, "Recordatorio no enviado")
        
        # Verificar mensaje de recordatorio
        reminder_msg = messages.filtered(lambda m: 'reminder' in m.body.lower())
        self.assertTrue(reminder_msg, "Mensaje de recordatorio no encontrado")
        
        # Enviar notificación de completado
        self.service_order.action_complete()
        result = messaging_integration.send_completion_notification(self.service_order)
        self.assertTrue(result, "Notificación de completado no enviada")
        
        # Verificar mensaje de completado
        completion_msg = messages.filtered(lambda m: 'completed' in m.body.lower())
        self.assertTrue(completion_msg, "Mensaje de completado no encontrado")
        
        # Probar enviar notificación sin email
        self.partner.email = False
        result = messaging_integration.send_scheduling_notification(self.service_order)
        self.assertFalse(result, "Notificación no debería enviarse sin email")
