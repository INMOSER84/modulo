# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestServiceWorkflows(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Constantes para pruebas
        self.TEST_DATE = datetime(2023, 1, 1, 10, 0, 0)
        self.TEST_DATE_END = datetime(2023, 1, 1, 12, 0, 0)
        self.NEW_DATE = datetime(2023, 1, 2, 10, 0, 0)
        
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

    def test_complete_workflow(self):
        """Probar flujo de trabajo completo de orden de servicio"""
        # Estado inicial
        self.assertEqual(self.service_order.state, 'draft', "Estado inicial incorrecto")
        
        # Programar
        self.service_order.action_schedule()
        self.assertEqual(self.service_order.state, 'scheduled', "Estado después de programar incorrecto")
        self.assertTrue(self.service_order.date_scheduled, "Fecha de programación no establecida")
        
        # Iniciar
        self.service_order.action_start()
        self.assertEqual(self.service_order.state, 'in_progress', "Estado después de iniciar incorrecto")
        self.assertTrue(self.service_order.date_started, "Fecha de inicio no establecida")
        
        # Agregar línea de refacción
        self.env['service.order.refaction.line'].create({
            'order_id': self.service_order.id,
            'product_id': self.product.id,
            'quantity': 2.0,
            'unit_price': 100.0,
        })
        
        # Completar
        wizard = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
            'notes': 'Test completion notes',
        })
        wizard.action_complete()
        
        self.assertEqual(self.service_order.state, 'completed', "Estado después de completar incorrecto")
        self.assertTrue(self.service_order.date_completed, "Fecha de completado no establecida")
        self.assertEqual(self.service_order.completion_notes, 'Test completion notes', "Notas de completado incorrectas")
        self.assertEqual(self.service_order.total_amount, 200.0, "Monto total incorrecto")

    def test_reprogram_workflow(self):
        """Probar flujo de trabajo de reprogramación de orden de servicio"""
        # Programar la orden de servicio
        self.service_order.action_schedule()
        self.assertEqual(self.service_order.state, 'scheduled', "Estado después de programar incorrecto")
        original_date = self.service_order.scheduled_date
        
        # Reprogramar
        wizard = self.env['service.reprogram.wizard'].with_context(active_id=self.service_order.id).create({
            'new_date': self.NEW_DATE,
            'reason': 'Test reprogramming reason',
        })
        wizard.action_reprogram()
        
        self.assertEqual(self.service_order.state, 'scheduled', "Estado después de reprogramar incorrecto")
        self.assertNotEqual(self.service_order.scheduled_date, original_date, "Fecha no modificada")
        self.assertEqual(self.service_order.scheduled_date, self.NEW_DATE, "Nueva fecha incorrecta")
        self.assertEqual(self.service_order.reprogramming_reason, 'Test reprogramming reason', "Razón de reprogramación incorrecta")
        
        # Verificar que se creó un registro de reprogramación
        reprogram_record = self.env['service.order.reprogram'].search([
            ('order_id', '=', self.service_order.id),
        ])
        self.assertEqual(len(reprogram_record), 1, "No se creó registro de reprogramación")
        self.assertEqual(reprogram_record.old_date, original_date, "Fecha anterior incorrecta en registro")
        self.assertEqual(reprogram_record.new_date, self.NEW_DATE, "Fecha nueva incorrecta en registro")

    def test_cancel_workflow(self):
        """Probar flujo de trabajo de cancelación de orden de servicio"""
        # Programar la orden de servicio
        self.service_order.action_schedule()
        self.assertEqual(self.service_order.state, 'scheduled', "Estado después de programar incorrecto")
        
        # Cancelar
        self.service_order.action_cancel()
        self.assertEqual(self.service_order.state, 'cancelled', "Estado después de cancelar incorrecto")
        self.assertTrue(self.service_order.date_cancelled, "Fecha de cancelación no establecida")
        
        # No se puede cancelar nuevamente
        with self.assertRaises(UserError):
            self.service_order.action_cancel()
        
        # No se puede programar una orden cancelada
        with self.assertRaises(UserError):
            self.service_order.action_schedule()
        
        # No se puede iniciar una orden cancelada
        with self.assertRaises(UserError):
            self.service_order.action_start()
        
        # No se puede completar una orden cancelada
        wizard = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
        })
        with self.assertRaises(UserError):
            wizard.action_complete()

    def test_draft_workflow(self):
        """Probar flujo de trabajo desde estado borrador"""
        # Verificar estado inicial
        self.assertEqual(self.service_order.state, 'draft', "Estado inicial incorrecto")
        
        # No se puede iniciar una orden en borrador
        with self.assertRaises(UserError):
            self.service_order.action_start()
        
        # No se puede completar una orden en borrador
        wizard = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
        })
        with self.assertRaises(UserError):
            wizard.action_complete()
        
        # Se puede cancelar una orden en borrador
        self.service_order.action_cancel()
        self.assertEqual(self.service_order.state, 'cancelled', "Estado después de cancelar incorrecto")

    def test_in_progress_workflow(self):
        """Probar flujo de trabajo desde estado en progreso"""
        # Programar e iniciar la orden
        self.service_order.action_schedule()
        self.service_order.action_start()
        self.assertEqual(self.service_order.state, 'in_progress', "Estado incorrecto")
        
        # No se puede programar una orden en progreso
        with self.assertRaises(UserError):
            self.service_order.action_schedule()
        
        # No se puede iniciar una orden ya en progreso
        with self.assertRaises(UserError):
            self.service_order.action_start()
        
        # Se puede reprogramar una orden en progreso
        wizard = self.env['service.reprogram.wizard'].with_context(active_id=self.service_order.id).create({
            'new_date': self.NEW_DATE,
            'reason': 'Test reprogramming reason',
        })
        wizard.action_reprogram()
        self.assertEqual(self.service_order.state, 'scheduled', "Estado después de reprogramar incorrecto")
        
        # Volver a iniciar para probar completado
        self.service_order.action_start()
        self.assertEqual(self.service_order.state, 'in_progress', "Estado incorrecto después de reiniciar")
        
        # Se puede cancelar una orden en progreso
        self.service_order.action_cancel()
        self.assertEqual(self.service_order.state, 'cancelled', "Estado después de cancelar incorrecto")

    def test_completed_workflow(self):
        """Probar flujo de trabajo desde estado completado"""
        # Llevar la orden a estado completado
        self.service_order.action_schedule()
        self.service_order.action_start()
        wizard = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
            'notes': 'Test completion notes',
        })
        wizard.action_complete()
        self.assertEqual(self.service_order.state, 'completed', "Estado incorrecto")
        
        # No se puede programar una orden completada
        with self.assertRaises(UserError):
            self.service_order.action_schedule()
        
        # No se puede iniciar una orden completada
        with self.assertRaises(UserError):
            self.service_order.action_start()
        
        # No se puede completar una orden ya completada
        wizard2 = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
        })
        with self.assertRaises(UserError):
            wizard2.action_complete()
        
        # No se puede reprogramar una orden completada
        wizard3 = self.env['service.reprogram.wizard'].with_context(active_id=self.service_order.id).create({
            'new_date': self.NEW_DATE,
            'reason': 'Test reprogramming reason',
        })
        with self.assertRaises(UserError):
            wizard3.action_reprogram()
        
        # No se puede cancelar una orden completada
        with self.assertRaises(UserError):
            self.service_order.action_cancel()

    def test_workflow_transitions(self):
        """Probar todas las transiciones posibles del flujo de trabajo"""
        # Crear una nueva orden para cada prueba
        transitions = [
            # (estado_inicial, accion, estado_esperado, debe_exito)
            ('draft', 'action_schedule', 'scheduled', True),
            ('draft', 'action_start', 'in_progress', False),
            ('draft', 'action_cancel', 'cancelled', True),
            ('scheduled', 'action_schedule', 'scheduled', False),
            ('scheduled', 'action_start', 'in_progress', True),
            ('scheduled', 'action_cancel', 'cancelled', True),
            ('in_progress', 'action_schedule', 'scheduled', False),
            ('in_progress', 'action_start', 'in_progress', False),
            ('in_progress', 'action_cancel', 'cancelled', True),
            ('cancelled', 'action_schedule', 'scheduled', False),
            ('cancelled', 'action_start', 'in_progress', False),
            ('cancelled', 'action_cancel', 'cancelled', False),
        ]
        
        for initial_state, action, expected_state, should_succeed in transitions:
            with self.subTest(initial_state=initial_state, action=action, expected_state=expected_state):
                # Crear orden
                order = self.env['service.order'].create({
                    'partner_id': self.partner.id,
                    'service_type_id': self.service_type.id,
                    'technician_id': self.technician.id,
                    'description': f'Test Order for {initial_state} -> {action}',
                })
                
                # Llevar al estado inicial
                if initial_state == 'scheduled':
                    order.action_schedule()
                elif initial_state == 'in_progress':
                    order.action_schedule()
                    order.action_start()
                elif initial_state == 'cancelled':
                    order.action_cancel()
                
                # Ejecutar acción
                if should_succeed:
                    # Debería tener éxito
                    getattr(order, action)()
                    self.assertEqual(order.state, expected_state, 
                                   f"Transición {initial_state} -> {action} debería llevar a {expected_state}")
                else:
                    # Debería fallar
                    with self.assertRaises(UserError):
                        getattr(order, action)()
                    self.assertEqual(order.state, initial_state, 
                                   f"Estado no debería cambiar en transición {initial_state} -> {action}")

    def test_workflow_with_equipment(self):
        """Probar flujo de trabajo con equipo asociado"""
        # Crear un equipo
        equipment = self.env['service.equipment'].create({
            'name': 'Test Equipment',
            'serial_number': 'TEST001',
            'partner_id': self.partner.id,
        })
        
        # Crear orden con equipo
        order_with_equipment = self.env['service.order'].create({
            'partner_id': self.partner.id,
            'service_type_id': self.service_type.id,
            'technician_id': self.technician.id,
            'equipment_id': equipment.id,
            'description': 'Test Service Order with Equipment',
        })
        
        # Ejecutar flujo completo
        order_with_equipment.action_schedule()
        self.assertEqual(order_with_equipment.state, 'scheduled', "Estado incorrecto")
        
        order_with_equipment.action_start()
        self.assertEqual(order_with_equipment.state, 'in_progress', "Estado incorrecto")
        
        wizard = self.env['service.complete.wizard'].with_context(active_id=order_with_equipment.id).create({
            'completion_date': '2023-01-01 12:00:00',
            'notes': 'Test completion notes',
        })
        wizard.action_complete()
        
        self.assertEqual(order_with_equipment.state, 'completed', "Estado incorrecto")
        
        # Verificar que se actualizó la última fecha de servicio del equipo
        self.assertEqual(equipment.last_service_date, datetime(2023, 1, 1).date(), 
                        "Última fecha de servicio del equipo no actualizada")

    def test_workflow_notifications(self):
        """Probar notificaciones en el flujo de trabajo"""
        # Ejecutar flujo completo y verificar notificaciones
        self.service_order.action_schedule()
        
        # Verificar mensaje de programación
        messages = self.env['mail.message'].search([
            ('model', '=', 'service.order'),
            ('res_id', '=', self.service_order.id),
        ])
        scheduled_msg = messages.filtered(lambda m: 'scheduled' in m.body.lower())
        self.assertTrue(scheduled_msg, "No se encontró mensaje de programación")
        
        self.service_order.action_start()
        
        # Verificar mensaje de inicio
        messages = self.env['mail.message'].search([
            ('model', '=', 'service.order'),
            ('res_id', '=', self.service_order.id),
        ])
        started_msg = messages.filtered(lambda m: 'started' in m.body.lower())
        self.assertTrue(started_msg, "No se encontró mensaje de inicio")
        
        wizard = self.env['service.complete.wizard'].with_context(active_id=self.service_order.id).create({
            'completion_date': '2023-01-01 12:00:00',
            'notes': 'Test completion notes',
        })
        wizard.action_complete()
        
        # Verificar mensaje de completado
        messages = self.env['mail.message'].search([
            ('model', '=', 'service.order'),
            ('res_id', '=', self.service_order.id),
        ])
        completed_msg = messages.filtered(lambda m: 'completed' in m.body.lower())
        self.assertTrue(completed_msg, "No se encontró mensaje de completado")
