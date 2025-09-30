from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError
from odoo import _
import logging
import json

_logger = logging.getLogger(__name__)

class MainController(http.Controller):

    @http.route(['/service-order/scan/<string:qr_data>'], type='http', auth="public", website=True, sitemap=False)
    def scan_service_order_qr(self, qr_data=None, **kw):
        if not qr_data:
            _logger.warning("QR scan attempt without QR data")
            return request.render('website.404')

        try:
            # Parse QR data
            parts = qr_data.split('|')
            if len(parts) < 3:
                _logger.warning("Invalid QR data format: %s", qr_data)
                return request.render('website.404')

            order_ref = parts[0]
            customer_name = parts[1]
            date_str = parts[2]

            # Find service order
            service_order = request.env['service.order'].sudo().search([
                ('name', '=', order_ref)
            ], limit=1)

            if not service_order:
                _logger.warning("Service order not found: %s", order_ref)
                return request.render('website.404')

            # Check if the customer name matches (case insensitive)
            if service_order.partner_id.name.lower() != customer_name.lower():
                _logger.warning("Customer name mismatch for order %s: expected %s, got %s", 
                               order_ref, service_order.partner_id.name, customer_name)
                return request.render('website.403')

            values = {
                'service_order': service_order,
                'qr_data': qr_data,
            }

            return request.render('modulo.service_order_qr_page', values)

        except Exception as e:
            _logger.error("Error processing QR scan: %s", str(e))
            return request.render('website.500', {
                'error_message': _('An error occurred while processing your request')
            })

    @http.route(['/api/service-order/<int:order_id>/status'], type='json', auth="api_key", methods=['GET'], csrf=False)
    def api_service_order_status(self, order_id=None, **kw):
        try:
            if not order_id:
                return {'error': _('Missing order_id')}

            # Validate API key
            api_key = request.httprequest.headers.get('Authorization')
            if not self._validate_api_key(api_key):
                _logger.warning("Invalid API key attempt for order %s", order_id)
                return {'error': _('Invalid API key')}

            service_order = request.env['service.order'].sudo().browse(order_id)

            if not service_order.exists():
                return {'error': _('Service order not found')}

            return {
                'id': service_order.id,
                'name': service_order.name,
                'state': service_order.state,
                'date_requested': service_order.date_requested,
                'date_scheduled': service_order.date_scheduled,
                'date_started': service_order.date_started,
                'date_completed': service_order.date_completed,
                'technician': service_order.technician_id.name if service_order.technician_id else None,
                'partner': service_order.partner_id.name,
                'service_type': service_order.service_type_id.name,
                'equipment': service_order.equipment_id.name if service_order.equipment_id else None,
            }

        except Exception as e:
            _logger.error("Error getting service order status: %s", str(e))
            return {'error': str(e)}

    @http.route(['/api/service-order/<int:order_id>/update'], type='json', auth="api_key", methods=['POST'], csrf=False)
    def api_update_service_order(self, order_id=None, **kw):
        try:
            if not order_id:
                return {'error': _('Missing order_id')}

            # Validate API key
            api_key = request.httprequest.headers.get('Authorization')
            if not self._validate_api_key(api_key):
                _logger.warning("Invalid API key attempt for order update %s", order_id)
                return {'error': _('Invalid API key')}

            service_order = request.env['service.order'].sudo().browse(order_id)

            if not service_order.exists():
                return {'error': _('Service order not found')}

            # Update fields based on request data
            allowed_fields = ['state', 'date_started', 'date_completed', 'notes', 'technician_id']
            update_vals = {}

            for field in allowed_fields:
                if field in kw:
                    update_vals[field] = kw[field]

            # Validate state transition
            if 'state' in update_vals:
                allowed_transitions = {
                    'draft': ['scheduled', 'cancelled'],
                    'scheduled': ['in_progress', 'cancelled'],
                    'in_progress': ['completed', 'cancelled'],
                    'completed': [],
                    'cancelled': [],
                }
                
                current_state = service_order.state
                new_state = update_vals['state']
                
                if new_state not in allowed_transitions.get(current_state, []):
                    return {'error': _('Invalid state transition from %s to %s') % (current_state, new_state)}

            if update_vals:
                service_order.write(update_vals)
                _logger.info("Service order %s updated via API", order_id)

            return {
                'success': True,
                'id': service_order.id,
                'state': service_order.state,
                'message': _('Service order updated successfully')
            }

        except Exception as e:
            _logger.error("Error updating service order: %s", str(e))
            return {'error': str(e)}

    @http.route(['/api/service-order/create'], type='json', auth="api_key", methods=['POST'], csrf=False)
    def api_create_service_order(self, **kw):
        try:
            # Validate API key
            api_key = request.httprequest.headers.get('Authorization')
            if not self._validate_api_key(api_key):
                _logger.warning("Invalid API key attempt for service order creation")
                return {'error': _('Invalid API key')}

            # Validate required fields
            required_fields = ['partner_id', 'service_type_id']
            for field in required_fields:
                if field not in kw:
                    return {'error': _('Missing required field: %s') % field}

            # Create service order
            service_order_vals = {
                'partner_id': kw['partner_id'],
                'service_type_id': kw['service_type_id'],
                'description': kw.get('description', ''),
                'priority': kw.get('priority', 'medium'),
            }

            # Optional fields
            if 'equipment_id' in kw:
                service_order_vals['equipment_id'] = kw['equipment_id']
            if 'technician_id' in kw:
                service_order_vals['technician_id'] = kw['technician_id']

            service_order = request.env['service.order'].sudo().create(service_order_vals)
            _logger.info("Service order %s created via API", service_order.name)

            return {
                'success': True,
                'id': service_order.id,
                'name': service_order.name,
                'state': service_order.state,
                'message': _('Service order created successfully')
            }

        except Exception as e:
            _logger.error("Error creating service order: %s", str(e))
            return {'error': str(e)}

    def _validate_api_key(self, api_key):
        """Validate API key"""
        if not api_key:
            return False
        
        # Remove 'Bearer ' prefix if present
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        # Get valid API key from configuration
        valid_key = request.env['ir.config_parameter'].sudo().get_param('modulo.api_key')
        return api_key == valid_key

    @http.route(['/service/dashboard'], type='http', auth="user", website=True)
    def service_dashboard(self, **kwargs):
        """Service dashboard for technicians and managers"""
        user = request.env.user
        
        # Check if user has access
        if not user.has_group('modulo.group_service_user'):
            return request.render('website.403')
        
        values = {
            'user': user,
            'page_name': 'service_dashboard',
        }
        
        # Get user's service orders (if technician)
        if user.has_group('modulo.group_service_technician'):
            technician = request.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if technician:
                values['my_service_orders'] = request.env['service.order'].search([
                    ('technician_id', '=', technician.id),
                    ('state', 'in', ['scheduled', 'in_progress'])
                ])
        
        # Get all service orders (if manager)
        if user.has_group('modulo.group_service_manager'):
            values['all_service_orders'] = request.env['service.order'].search([
                ('state', 'in', ['draft', 'scheduled', 'in_progress'])
            ], limit=10)
        
        return request.render('modulo.service_dashboard', values)
