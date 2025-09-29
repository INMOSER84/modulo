# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestServiceOrder(TransactionCase):

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
        
        # Crear un tipo de servicio
        self.service_type = self.env['service.type'].create({
            'name': 'Test Service Type',
            'duration': 2.0,
            'equipment_required': False,
            'technician_required': True,
            'description': 'Test service type description',
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
            'technician_id': self.technician.id,
            'description': 'Test Service Order',
            'scheduled_date': self.TEST_DATE,
            'scheduled_date_end': self.TEST_DATE_END,
        })

    def test_service_order_creation(self):
        """Probar creación de orden de servicio"""
        self.assertEqual(self.service_order.state, 'draft', "Estado inicial incorrecto")
        self.assertTrue(self.service_order.name.startswith('SO/'), "Formato de nombre incorrecto")
        self.assertEqual(self.service_order.partner_id, self.partner, "Cliente incorrecto")
        self.assertEqual(self.service_order.service_type_id, self.service_type, "Tipo de servicio incorrecto")
        self.assertEqual(self.service_order.technician_id, self.technician, "Técnico incorrecto")
        
        # Verificar secuencia automática
        order2 = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        self.assertNotEqual(self.service_order.name, order2.name, "Las órdenes deben tener nombres diferentes")

    def test_service_order_schedule(self):
        """Probar programación de orden de servicio"""
        self.service_order.action_schedule()
        self.assertEqual(self.service_order.state, 'scheduled', "Estado después de programar incorrecto")
        self.assertTrue(self.service_order.date_scheduled, "Fecha de programación no establecida")
        
        # Probar programar una orden ya programada
        with self.assertRaises(UserError):
            self.service_order.action_schedule()

    def test_service_order_start(self):
        """Probar inicio de orden de servicio"""
        self.service_order.action_schedule()
        self.service_order.action_start()
        self.assertEqual(self.service_order.state, 'in_progress', "Estado después de iniciar incorrecto")
        self.assertTrue(self.service_order.date_started, "Fecha de inicio no establecida")
        
        # Probar iniciar una orden ya iniciada
        with self.assertRaises(UserError):
            self.service_order.action_start()
        
        # Probar iniciar una orden no programada
        new_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        with self.assertRaises(UserError):
            new_order.action_start()

    def test_service_order_complete(self):
        """Probar completado de orden de servicio"""
        self.service_order.action_schedule()
        self.service_order.action_start()

        # Completar la orden de servicio
        wizard = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
            'notes': 'Test completion notes',
        })
        wizard.action_complete()

        self.assertEqual(self.service_order.state, 'completed', "Estado después de completar incorrecto")
        self.assertTrue(self.service_order.date_completed, "Fecha de completado no establecida")
        self.assertEqual(self.service_order.completion_notes, 'Test completion notes', "Notas de completado incorrectas")
        
        # Probar completar una orden ya completada
        with self.assertRaises(UserError):
            wizard.action_complete()
        
        # Probar completar una orden no iniciada
        new_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        new_order.action_schedule()
        with self.assertRaises(UserError):
            wizard.with_context(active_id=new_order.id).action_complete()

    def test_service_order_cancel(self):
        """Probar cancelación de orden de servicio"""
        self.service_order.action_cancel()
        self.assertEqual(self.service_order.state, 'cancelled', "Estado después de cancelar incorrecto")
        
        # Probar cancelar una orden ya cancelada
        with self.assertRaises(UserError):
            self.service_order.action_cancel()
        
        # Probar cancelar una orden completada
        completed_order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        completed_order.action_schedule()
        completed_order.action_start()
        wizard = self.env['service.complete.wizard'].with_context(active_id=completed_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
        })
        wizard.action_complete()
        
        with self.assertRaises(UserError):
            completed_order.action_cancel()

    def test_service_order_refaction_line(self):
        """Probar línea de refacción de orden de servicio"""
        refaction_line = self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.product.id,
            'quantity': 2.0,
            'unit_price': 100.0,
        })

        self.assertEqual(refaction_line.subtotal, 200.0, "Subtotal calculado incorrecto")
        self.assertEqual(len(self.service_order.refaction_line_ids), 1, "Número de líneas de refacción incorrecto")
        
        # Verificar actualización de total
        self.assertEqual(self.service_order.total_amount, 200.0, "Monto total incorrecto")
        
        # Agregar otra línea de refacción
        refaction_line2 = self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'unit_price': 50.0,
        })
        
        self.assertEqual(len(self.service_order.refaction_line_ids), 2, "Número de líneas de refacción incorrecto")
        self.assertEqual(self.service_order.total_amount, 250.0, "Monto total incorrecto")

    def test_service_order_constraints(self):
        """Probar restricciones de orden de servicio"""
        # Sin cliente
        with self.assertRaises(ValidationError):
            self.env['service.order'].create({
                'service_type_id': self.service_type.id,
                'technician_id': self.technician.id,
            })
            
        # Sin tipo de servicio
        with self.assertRaises(ValidationError):
            self.env['service.order'].create({
                'partner_id': self.partner.id,
                'technician_id': self.technician.id,
            })
            
        # Sin técnico (requerido para este tipo de servicio)
        with self.assertRaises(ValidationError):
            self.env['service.order'].create({
                'partner_id': self.partner.id,
                'service_type_id': self.service_type.id,
            })
            
        # Fechas inconsistentes
        with self.assertRaises(ValidationError):
            self.env['service.order'].create({
                'partner_id': self.partner.id,
                'service_type_id': self.service_type.id,
                'technician_id': self.technician.id,
                'scheduled_date': '2023-01-01 12:00:00',
                'scheduled_date_end': '2023-01-01 10:00:00',
            })

    def test_service_order_onchange_methods(self):
        """Probar métodos onchange de orden de servicio"""
        # Probar onchange de tipo de servicio
        new_service_type = self.env['service.type'].create({
            'name': 'New Service Type',
            'duration': 3.0,
            'equipment_required': True,
            'technician_required': True,
        })
        
        order = self.env['service.order'].new({
            'partner_id': self.partner.id,
            'service_type_id': new_service_type.id,
            'scheduled_date': self.TEST_DATE,
        })
        
        order._onchange_service_type_id()
        self.assertEqual(order.duration, 3.0, "Duración no actualizada correctamente")
        
        # Probar onchange de fechas
        order.scheduled_date = self.TEST_DATE
        order.scheduled_date_end = self.TEST_DATE_END
        order._onchange_dates()
        self.assertEqual(order.duration, 2.0, "Duración calculada incorrectamente")

    def test_service_order_compute_methods(self):
        """Probar métodos compute de orden de servicio"""
        # Agregar líneas de refacción
        self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.product.id,
            'quantity': 2.0,
            'unit_price': 100.0,
        })
        
        # Verificar campo calculado de total
        self.assertEqual(self.service_order.total_amount, 200.0, "Total calculado incorrectamente")
        
        # Verificar campo calculado de duración
        self.assertEqual(self.service_order.duration, 2.0, "Duración calculada incorrectamente")
        
        # Verificar campo calculado de estado
        self.assertEqual(self.service_order.state, 'draft', "Estado calculado incorrectamente")

    def test_service_order_action_methods(self):
        """Probar métodos de acción de orden de servicio"""
        # Probar acción para ver líneas de refacción
        action = self.service_order.action_view_refaction_lines()
        self.assertEqual(action['type'], 'ir.actions.act_window', "Acción incorrecta")
        self.assertEqual(action['res_model'], 'service.order.refaction.line', "Modelo incorrecto")
        self.assertIn(('order_id', '=', self.service_order.id), action['domain'], "Dominio incorrecto")
        
        # Probar acción para duplicar orden
        new_order = self.service_order.copy()
        self.assertNotEqual(new_order.id, self.service_order.id, "Orden no duplicada correctamente")
        self.assertEqual(new_order.partner_id, self.service_order.partner_id, "Cliente no copiado correctamente")
        self.assertEqual(new_order.state, 'draft', "Estado no reseteado correctamente")

    def test_service_order_search(self):
        """Probar búsqueda de órdenes de servicio"""
        # Crear varias órdenes con diferentes estados
        order1 = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        
        order2 = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        
        order2.action_schedule()
        order2.action_start()
        
        # Buscar por estado
        draft_orders = self.env['service.order'].search([('state', '=', 'draft')])
        self.assertIn(order1, draft_orders, "Orden en borrador no encontrada")
        self.assertNotIn(order2, draft_orders, "Orden en progreso encontrada en búsqueda de borradores")
        
        # Buscar por cliente
        partner_orders = self.env['service.order'].search([('partner_id', '=', self.partner.id)])
        self.assertIn(order1, partner_orders, "Orden del cliente no encontrada")
        self.assertIn(order2, partner_orders, "Orden del cliente no encontrada")
        
        # Buscar por técnico
        technician_orders = self.env['service.order'].search([('technician_id', '=', self.technician.id)])
        self.assertIn(order1, technician_orders, "Orden del técnico no encontrada")
        self.assertIn(order2, technician_orders, "Orden del técnico no encontrada")

    def test_service_order_unlink(self):
        """Probar eliminación de órdenes de servicio"""
        # Crear una orden con líneas de refacción
        self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'unit_price': 100.0,
        })
        
        order_id = self.service_order.id
        
        # Eliminar orden
        self.service_order.unlink()
        
        # Verificar que la orden fue eliminada
        found_order = self.env['service.order'].search([('id', '=', order_id)])
        self.assertEqual(len(found_order), 0, "Orden no eliminada correctamente")
        
        # Verificar que las líneas de refacción también fueron eliminadas
        refaction_lines = self.env['service.order.refaction.line'].search([('order_id', '=', order_id)])
        self.assertEqual(len(refaction_lines), 0, "Líneas de refacción no eliminadas correctamente")

    def test_service_order_workflow(self):
        """Probar flujo de trabajo completo de orden de servicio"""
        # Crear orden
        order = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
        })
        
        # Flujo completo
        order.action_schedule()
        self.assertEqual(order.state, 'scheduled', "Estado incorrecto después de programar")
        
        order.action_start()
        self.assertEqual(order.state, 'in_progress', "Estado incorrecto después de iniciar")
        
        # Agregar línea de refacción
        self.env['service.order.refaction.line'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'unit_price': 100.0,
        })
        
        # Completar orden
        wizard = self.env['service.complete.wizard'].with_context(active_id=order.id).create({
            'completion_date': '2023-01-01 12:00:00',
            'notes': 'Test completion notes',
        })
        wizard.action_complete()
        
        self.assertEqual(order.state, 'completed', "Estado incorrecto después de completar")
        self.assertEqual(order.total_amount, 100.0, "Total incorrecto después de completar")
        
        # No se puede cancelar una orden completada
        with self.assertRaises(UserError):
            order.action_cancel()
