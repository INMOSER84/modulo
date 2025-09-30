# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class StockIntegration(models.AbstractModel):
    _name = 'stock.integration'
    _description = _('Stock Integration for Service Orders')

    @api.model
    def _check_product_availability(self, product_id, quantity):
        """Check if a product is available in stock"""
        product = self.env['product.product'].browse(product_id)
        if product.qty_available >= quantity:
            return True
        return False

    @api.model
    def _reserve_product_for_service(self, product_id, quantity, location_id):
        """Reserve a product for a service order"""
        # Implementation for product reservation
        return True

    @api.model
    def _consume_product_for_service(self, product_id, quantity, location_id):
        """Consume a product for a service order"""
        scrap_location = self.env.ref('stock.stock_location_scrapped')
        if not scrap_location:
            _logger.warning(_("Consumption location not found. Using scrap location instead."))
        
        consumption_location = self.env.ref('stock.location_consumption', False)
        if not consumption_location:
            if scrap_location:
                consumption_location = scrap_location
            else:
                _logger.error(_("Neither consumption nor scrap location found."))
                return False
        
        # Implementation for product consumption
        return True

    @api.model
    def _return_product_from_service(self, product_id, quantity, location_id):
        """Return a product from a service order"""
        scrap_location = self.env.ref('stock.stock_location_scrapped')
        if not scrap_location:
            _logger.error(_("Neither consumption nor scrap location found."))
            return False
        
        # Implementation for product return
        return True

    @api.model
    def _create_picking_for_service(self, partner_id, product_ids, quantities):
        """Create a picking for a service order"""
        customer_location = self.env.ref('stock.stock_location_customers', False)
        if not customer_location:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.property_stock_customer:
                customer_location = partner.property_stock_customer
            else:
                _logger.warning(_("Customer location not found. Using partner location instead."))
                customer_location = self.env.ref('stock.stock_location_suppliers')
        
        if not customer_location:
            _logger.error(_("No customer location found."))
            return False
        
        # Implementation for picking creation
        return True
