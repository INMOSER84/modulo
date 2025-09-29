# -*- coding: utf-8 -*-
{
    'name': 'Inmoser Service Management',
    'version': '17.0.1.0.0',
    'category': 'Service Management',
    'summary': 'Complete Service Order Management System for Technical Services',
    'author': 'INMOSER84',
    'website': 'https://github.com/INMOSER84/inmoser_service_order',
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'web', 
        'mail', 
        'account', 
        'stock', 
        'hr', 
        'portal', 
        'calendar', 
        'product', 
        'contacts',
        'base_geolocalize',  # Añadido para funcionalidad de mapas
        'web_map',           # Añadido para vistas de mapa
        'sale',              # Añadido para integración con ventas
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/inmoser_security.xml',
        'data/service_type_data.xml',
        'data/ir_sequence_data.xml',
        'data/cron_jobs.xml',
        'data/email_templates.xml',
        'views/menu_items.xml',
        'views/service_order_views.xml',
        'views/service_order_actions.xml',
        'views/service_order_calendar.xml',
        'views/service_order_map.xml',  # Añadido para vista de mapa
        'views/service_equipment_views.xml',
        'views/service_type_views.xml',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
        'views/portal_templates.xml',
        'views/service_complete_wizard_views.xml',
        'views/service_reprogram_wizard_views.xml',
        'reports/service_order_report.xml',
        'reports/service_order_template.xml',
        'reports/service_certificate_template.xml',
        'reports/equipment_history_template.xml',
        'reports/technician_performance_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'modulo/static/src/css/portal.scss',
            'modulo/static/src/css/service_order.scss',
            'modulo/static/src/js/calendar_views.js',
            'modulo/static/src/js/service_order_qr.js',
            'modulo/static/src/js/service_order_map.js',  # Añadido para funcionalidad de mapa
        ],
        'web.assets_frontend': [
            'modulo/static/src/css/portal.scss',
        ],
        'web.assets_qweb': [
            'modulo/static/src/xml/service_order_qr.xml',
            'modulo/static/src/xml/calendar_templates.xml',
            'modulo/static/src/xml/map_templates.xml',  # Añadido para plantillas de mapa
        ],
    },
    'demo': ['demo/demo_data.xml'],
    'test': [
        'tests/test_service_order.py',
        'tests/test_service_equipment.py',
        'tests/test_business_rules.py',
        'tests/test_integrations.py',
        'tests/test_service_workflows.py',
        'tests/test_ui.py',
        'tests/test_performance.py',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['qrcode', 'requests'],  # Añadido requests para API de mapas
        'bin': ['libgeos-dev'],  # Añadido para funcionalidad geográfica
    },
    'development_status': 'Beta',
    'price': 0,
    'currency': 'EUR',
    'images': ['static/description/icon.png'],
    'description': '''
This module provides a complete service order management system for technical services companies.

Features:
    * Service order creation and management
    * Equipment tracking and maintenance history
    * Technician scheduling and assignment
    * Customer portal for service tracking
    * QR code generation for equipment and service orders
    * Integration with accounting, inventory and HR modules
    * Comprehensive reporting system
    * Mobile-friendly interface
    * Map views for service location tracking (NEW in v17)

This module is ideal for companies that provide technical services such as:
    * HVAC maintenance
    * Electrical services
    * Plumbing services
    * Appliance repair
    * IT support services
    * Facility management
    ''',
}
