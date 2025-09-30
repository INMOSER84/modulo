# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestServiceEquipment(TransactionCase):

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
        
        # Crear un equipo
        self.equipment = self.env['service.equipment'].create({
            'name': 'Test Equipment',
            'serial_number': 'TEST001',
            'model': 'Test Model',
            'manufacturer': 'Test Manufacturer',
            'partner_id': self.partner.id,
            'location': 'Test Location',
            'service_interval': 365,
            'installation_date': '2022-01-01',
            'warranty_end_date': '2025-01-01',
            'notes': 'Test equipment notes',
        })
        
        # Crear un tipo de servicio
        self.service_type = self.env['service.type'].create({
            'name': 'Test Service Type',
            'duration': 2.0,
            'equipment_required': True,
            'technician_required': True,
            'description': 'Test service type description',
        })
        
        # Crear un técnico
        self.technician = self.env['hr.employee'].create({
            'name': 'Test Technician',
            'work_email': 'technician@example.com',
            'is_technician': True,
        })

    def test_equipment_creation(self):
        """Probar creación de equipo"""
        self.assertTrue(self.equipment.name, "El equipo debe tener un nombre")
        self.assertTrue(self.equipment.serial_number, "El equipo debe tener un número de serie")
        self.assertEqual(self.equipment.partner_id, self.partner, "El cliente del equipo es incorrecto")
        self.assertEqual(self.equipment.service_interval, 365, "El intervalo de servicio es incorrecto")
        self.assertTrue(self.equipment.next_service_date, "El equipo debe tener una fecha de próximo servicio")
        
        # Verificar cálculo de próxima fecha de servicio
        expected_next_date = datetime.strptime('2022-01-01', '%Y-%m-%d') + timedelta(days=365)
        self.assertEqual(self.equipment.next_service_date.date(), expected_next_date.date(), 
                        "La fecha de próximo servicio es incorrecta")

    def test_equipment_qr_code(self):
        """Probar generación de código QR del equipo"""
        self.assertTrue(self.equipment.qr_code, "El equipo debe tener un código QR")
        
        # Verificar que el código QR es una cadena base64 válida
        import base64
        try:
            base64.b64decode(self.equipment.qr_code)
            valid_base64 = True
        except Exception:
            valid_base64 = False
        self.assertTrue(valid_base64, "El código QR debe ser una cadena base64 válida")
        
        # Verificar que el código QR se regenera al cambiar el número de serie
        original_qr = self.equipment.qr_code
        self.equipment.serial_number = 'TEST002'
        self.assertNotEqual(self.equipment.qr_code, original_qr, 
                          "El código QR debe cambiar al modificar el número de serie")

    def test_equipment_service_history(self):
        """Probar historial de servicio del equipo"""
        # Crear una orden de servicio para el equipo
        service_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'description': 'Test Service Order',
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
        })
        
        # Verificar que la orden está asociada al equipo
        self.assertEqual(len(self.equipment.service_order_ids), 1, 
                        "El equipo debe tener una orden de servicio asociada")
        self.assertEqual(self.equipment.service_order_ids[0], service_order, 
                        "La orden de servicio asociada es incorrecta")
        
        # Crear otra orden de servicio para el mismo equipo
        service_order2 = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'description': 'Test Service Order 2',
            'scheduled_date': self.TEST_DATE + timedelta(days=7),
            'scheduled_date_end': self.TEST_DATE_END + timedelta(days=7),
        })
        
        # Verificar que ambas órdenes están asociadas al equipo
        self.assertEqual(len(self.equipment.service_order_ids), 2, 
                        "El equipo debe tener dos órdenes de servicio asociadas")
        self.assertIn(service_order2, self.equipment.service_order_ids, 
                     "La segunda orden de servicio no está asociada al equipo")

    def test_equipment_constraints(self):
        """Probar restricciones del modelo de equipo"""
        # Sin nombre
        with self.assertRaises(ValidationError):
            self.env['service.equipment'].create({
                'name': False,
                'serial_number': 'TEST002',
                'partner_id': self.partner.id,
            })
            
        # Sin número de serie
        with self.assertRaises(ValidationError):
            self.env['service.equipment'].create({
                'name': 'Test Equipment 2',
                'serial_number': False,
                'partner_id': self.partner.id,
            })
            
        # Sin cliente
        with self.assertRaises(ValidationError):
            self.env['service.equipment'].create({
                'name': 'Test Equipment 2',
                'serial_number': 'TEST002',
                'partner_id': False,
            })
            
        # Número de serie duplicado
        with self.assertRaises(ValidationError):
            self.env['service.equipment'].create({
                'name': 'Test Equipment 2',
                'serial_number': 'TEST001',  # Mismo número de serie que self.equipment
                'partner_id': self.partner.id,
            })
            
        # Intervalo de servicio negativo
        with self.assertRaises(ValidationError):
            self.env['service.equipment'].create({
                'name': 'Test Equipment 2',
                'serial_number': 'TEST002',
                'partner_id': self.partner.id,
                'service_interval': -1,
            })

    def test_equipment_onchange_methods(self):
        """Probar métodos onchange del modelo de equipo"""
        # Crear un equipo sin fecha de instalación
        equipment = self.env['service.equipment'].new({
            'name': 'Test Equipment 2',
            'serial_number': 'TEST002',
            'partner_id': self.partner.id,
            'service_interval': 180,
        })
        
        # Establecer fecha de instalación y verificar que se calcula la próxima fecha de servicio
        equipment.installation_date = '2023-01-01'
        equipment._onchange_installation_date()
        self.assertEqual(equipment.next_service_date, datetime(2023, 6, 30), 
                        "La próxima fecha de servicio no se calculó correctamente")
        
        # Cambiar intervalo de servicio y verificar que se actualiza la próxima fecha
        equipment.service_interval = 90
        equipment._onchange_service_interval()
        self.assertEqual(equipment.next_service_date, datetime(2023, 3, 31), 
                        "La próxima fecha de servicio no se actualizó correctamente")

    def test_equipment_compute_methods(self):
        """Probar métodos compute del modelo de equipo"""
        # Crear una orden de servicio completada para el equipo
        service_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'description': 'Test Service Order',
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
        })
        
        # Completar la orden de servicio
        service_order.action_complete()
        
        # Verificar campo calculado de última fecha de servicio
        self.assertEqual(self.equipment.last_service_date, self.TEST_DATE.date(), 
                        "La última fecha de servicio es incorrecta")
        
        # Verificar campo calculado de días hasta próximo servicio
        today = datetime.now().date()
        days_until_service = (self.equipment.next_service_date.date() - today).days
        self.assertEqual(self.equipment.days_until_next_service, days_until_service, 
                        "Los días hasta el próximo servicio son incorrectos")
        
        # Verificar campo calculado de estado de garantía
        self.assertTrue(self.equipment.under_warranty, "El equipo debería estar bajo garantía")
        
        # Cambiar fecha de fin de garantía a una fecha pasada
        self.equipment.warranty_end_date = '2020-01-01'
        self.assertFalse(self.equipment.under_warranty, "El equipo no debería estar bajo garantía")

    def test_equipment_action_methods(self):
        """Probar métodos de acción del modelo de equipo"""
        # Probar método para ver historial de servicio
        action = self.equipment.action_view_service_history()
        self.assertEqual(action['type'], 'ir.actions.act_window', 
                        "La acción para ver historial de servicio es incorrecta")
        self.assertEqual(action['res_model'], 'service.order', 
                        "El modelo para ver historial de servicio es incorrecto")
        self.assertIn(('equipment_id', '=', self.equipment.id), action['domain'], 
                     "El dominio para ver historial de servicio es incorrecto")
        
        # Probar método para generar código QR
        self.equipment.action_generate_qr_code()
        self.assertTrue(self.equipment.qr_code, "El código QR no se generó correctamente")
        
        # Probar método para programar servicio
        action = self.equipment.action_schedule_service()
        self.assertEqual(action['type'], 'ir.actions.act_window', 
                        "La acción para programar servicio es incorrecta")
        self.assertEqual(action['res_model'], 'service.order', 
                        "El modelo para programar servicio es incorrecto")
        self.assertEqual(action['context']['default_equipment_id'], self.equipment.id, 
                        "El contexto para programar servicio es incorrecto")

    def test_equipment_unlink(self):
        """Probar eliminación de equipos"""
        # Crear una orden de servicio para el equipo
        service_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'equipment_id': self.equipment.id,
            'technician_id': self.technician.id,
            'description': 'Test Service Order',
        })
        
        # Intentar eliminar el equipo con órdenes de servicio asociadas
        with self.assertRaises(UserError):
            self.equipment.unlink()
            
        # Eliminar la orden de servicio
        service_order.unlink()
        
        # Ahora debería poder eliminar el equipo
        equipment_id = self.equipment.id
        self.equipment.unlink()
        
        # Verificar que el equipo fue eliminado
        found_equipment = self.env['service.equipment'].search([('id', '=', equipment_id)])
        self.assertEqual(len(found_equipment), 0, "El equipo no fue eliminado correctamente")
