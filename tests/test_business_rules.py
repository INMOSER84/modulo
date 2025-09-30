# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestBusinessRules(TransactionCase):

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
        })
        
        # Crear un tipo de servicio
        self.service_type = self.env['service.type'].create({
            'name': 'Test Service Type',
            'duration': 2.0,
            'equipment_required': True,
            'technician_required': True,
            'description': 'Test service type description',
        })
        
        # Crear un equipo
        self.equipment = self.env['service.equipment'].create({
            'name': 'Test Equipment',
            'serial_number': 'TEST001',
            'partner_id': self.partner.id,
            'model': 'Model X',
            'brand': 'Brand Y',
        })
        
        # Crear un técnico
        self.technician = self.env['hr.employee'].create({
            'name': 'Test Technician',
            'work_email': 'technician@example.com',
            'is_technician': True,
        })
        
        # Crear un producto para refacciones
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'lst_price': 100.0,
            'type': 'product',
            'default_code': 'TP001',
        })
        
        # Crear una orden de servicio
        self.service_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'description': 'Test Service Order',
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
        })

    def test_validate_service_order(self):
        """Probar validación de orden de servicio"""
        business_logic = self.env['service.order.business.logic']
        
        # Orden de servicio válida
        errors = business_logic.validate_service_order(self.service_order)
        self.assertEqual(len(errors), 0, "Orden válida no debería tener errores")
        
        # Falta partner
        self.service_order.partner_id = False
        errors = business_logic.validate_service_order(self.service_order)
        self.assertGreater(len(errors), 0, "Debería haber error cuando falta el cliente")
        self.assertTrue(any('Customer is required' in error for error in errors), 
                       "Error de cliente requerido no encontrado")
        
        # Restaurar partner
        self.service_order.partner_id = self.partner.id
        
        # Falta equipo (requerido para este tipo de servicio)
        self.service_order.equipment_id = False
        errors = business_logic.validate_service_order(self.service_order)
        self.assertGreater(len(errors), 0, "Debería haber error cuando falta el equipo")
        self.assertTrue(any('Equipment is required' in error for error in errors), 
                       "Error de equipo requerido no encontrado")
        
        # Restaurar equipo
        self.service_order.equipment_id = self.equipment.id
        
        # Falta técnico (requerido para este tipo de servicio)
        self.service_order.technician_id = False
        errors = business_logic.validate_service_order(self.service_order)
        self.assertGreater(len(errors), 0, "Debería haber error cuando falta el técnico")
        self.assertTrue(any('Technician is required' in error for error in errors), 
                       "Error de técnico requerido no encontrado")
        
        # Restaurar técnico
        self.service_order.technician_id = self.technician.id
        
        # Fechas inconsistentes
        self.service_order.scheduled_date_end = self.TEST_DATE - timedelta(hours=1)
        errors = business_logic.validate_service_order(self.service_order)
        self.assertGreater(len(errors), 0, "Debería haber error con fechas inconsistentes")
        self.assertTrue(any('End date must be after start date' in error for error in errors), 
                       "Error de fechas inconsistentes no encontrado")

    def test_calculate_service_duration(self):
        """Probar cálculo de duración de servicio"""
        business_logic = self.env['service.order.business.logic']
        
        # Duración base
        duration = business_logic.calculate_service_duration(self.service_order)
        self.assertEqual(duration, 2.0, "Duración base incorrecta")
        
        # Agregar líneas de refacción
        self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.product.id,
            'quantity': 2.0,
            'unit_price': 100.0,
        })
        
        duration = business_logic.calculate_service_duration(self.service_order)
        self.assertEqual(duration, 3.0, "Duración con refacciones incorrecta")
        
        # Cambiar prioridad a urgente
        self.service_order.priority = 'urgent'
        duration = business_logic.calculate_service_duration(self.service_order)
        self.assertEqual(duration, 4.5, "Duración con prioridad urgente incorrecta")
        
        # Cambiar prioridad a baja
        self.service_order.priority = 'low'
        duration = business_logic.calculate_service_duration(self.service_order)
        self.assertEqual(duration, 2.5, "Duración con prioridad baja incorrecta")
        
        # Probar con tipo de servicio sin duración definida
        service_type_no_duration = self.env['service.type'].create({
            'name': 'Service Type No Duration',
            'duration': 0.0,
        })
        self.service_order.service_type_id = service_type_no_duration.id
        duration = business_logic.calculate_service_duration(self.service_order)
        self.assertEqual(duration, 1.0, "Duración por defecto incorrecta")

    def test_check_service_order_conflicts(self):
        """Probar detección de conflictos de orden de servicio"""
        business_logic = self.env['service.order.business.logic']
        
        # Programar la orden de servicio
        self.service_order.write({
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
            'state': 'scheduled',
        })
        
        # Crear otra orden de servicio para el mismo técnico al mismo tiempo
        conflicting_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'scheduled_date': self.TEST_DATE + timedelta(hours=1),
            'scheduled_date_end': self.TEST_DATE_END + timedelta(hours=1),
            'state': 'scheduled',
            'description': 'Conflicting Service Order',
        })
        
        # Verificar conflictos
        conflicts = business_logic.check_service_order_conflicts(conflicting_order)
        self.assertGreater(len(conflicts), 0, "Debería detectar conflictos")
        self.assertTrue(any('Overlapping' in conflict['reason'] for conflict in conflicts), 
                       "Conflicto de superposición no detectado")
        
        # Probar sin conflictos
        non_conflicting_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'scheduled_date': self.TEST_DATE + timedelta(days=1),
            'scheduled_date_end': self.TEST_DATE_END + timedelta(days=1),
            'state': 'scheduled',
            'description': 'Non-Conflicting Service Order',
        })
        
        conflicts = business_logic.check_service_order_conflicts(non_conflicting_order)
        self.assertEqual(len(conflicts), 0, "No debería haber conflictos")
        
        # Probar conflicto de equipo
        another_technician = self.env['hr.employee'].create({
            'name': 'Another Technician',
            'is_technician': True,
        })
        
        equipment_conflict_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': another_technician.id,
            'scheduled_date': self.TEST_DATE + timedelta(hours=1),
            'scheduled_date_end': self.TEST_DATE_END + timedelta(hours=1),
            'state': 'scheduled',
            'description': 'Equipment Conflict Service Order',
        })
        
        conflicts = business_logic.check_service_order_conflicts(equipment_conflict_order)
        self.assertGreater(len(conflicts), 0, "Debería detectar conflicto de equipo")
        self.assertTrue(any('Equipment' in conflict['reason'] for conflict in conflicts), 
                       "Conflicto de equipo no detectado")

    def test_auto_assign_technician(self):
        """Probar asignación automática de técnicos"""
        business_logic = self.env['service.order.business.logic']
        
        # Crear orden sin técnico asignado
        order_no_technician = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
            'description': 'Order without technician',
        })
        
        # Asignar técnico automáticamente
        assigned_technician = business_logic.auto_assign_technician(order_no_technician)
        self.assertIsNotNone(assigned_technician, "Debería asignar un técnico")
        self.assertEqual(order_no_technician.technician_id, assigned_technician, 
                        "Técnico no asignado correctamente")
        
        # Probar cuando no hay técnicos disponibles
        order_no_technician2 = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
            'description': 'Order without technician 2',
        })
        
        # Marcar técnico como no disponible
        self.technician.is_available = False
        
        # Intentar asignar técnico
        with self.assertRaises(UserError):
            business_logic.auto_assign_technician(order_no_technician2)

    def test_generate_service_report(self):
        """Probar generación de reportes de servicio"""
        business_logic = self.env['service.order.business.logic']
        
        # Completar la orden de servicio
        self.service_order.action_complete()
        
        # Generar reporte
        report_data = business_logic.generate_service_report(self.service_order)
        
        self.assertIn('order_data', report_data, "Reporte debe incluir datos de la orden")
        self.assertIn('partner_data', report_data, "Reporte debe incluir datos del cliente")
        self.assertIn('equipment_data', report_data, "Reporte debe incluir datos del equipo")
        self.assertIn('technician_data', report_data, "Reporte debe incluir datos del técnico")
        
        # Verificar datos del reporte
        self.assertEqual(report_data['order_data']['name'], self.service_order.name, 
                        "Nombre de orden incorrecto en reporte")
        self.assertEqual(report_data['partner_data']['name'], self.partner.name, 
                        "Nombre de cliente incorrecto en reporte")

    def test_notify_customer(self):
        """Probar notificación a clientes"""
        business_logic = self.env['service.order.business.logic']
        
        # Completar la orden de servicio
        self.service_order.action_complete()
        
        # Notificar al cliente
        result = business_logic.notify_customer(self.service_order)
        
        self.assertTrue(result, "Notificación debería ser exitosa")
        
        # Verificar que se creó un mensaje en el chatter
        messages = self.env['mail.message'].search([
            ('model', '=', 'service.order'),
            ('res_id', '=', self.service_order.id),
            ('message_type', '=', 'notification'),
        ])
        self.assertGreater(len(messages), 0, "Debería haber mensajes de notificación")
        
        # Probar notificación sin email del cliente
        self.partner.email = False
        result = business_logic.notify_customer(self.service_order)
        self.assertFalse(result, "Notificación debería fallar sin email")
