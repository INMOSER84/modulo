# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ServiceOrderBusinessLogic(models.AbstractModel):
    _name = 'service.order.business.logic'
    _description = _('Business Logic for Service Orders')

    @api.model
    def _validate_service_order(self, order):
        """Validate a service order before scheduling"""
        errors = []
        
        if not order.partner_id:
            errors.append(_("Customer is required"))
        
        if not order.service_type_id:
            errors.append(_("Service type is required"))
        
        if order.service_type_id.requires_equipment and not order.equipment_id:
            errors.append(_("Equipment is required for this service type"))
        
        if order.service_type_id.requires_technician and not order.technician_id:
            errors.append(_("Technician is required for this service type"))
        
        return errors
