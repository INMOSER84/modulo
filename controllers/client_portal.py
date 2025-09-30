from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError
from odoo import _
import logging

_logger = logging.getLogger(__name__)

class ClientPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        ServiceOrder = request.env['service.order']
        if 'service_order_count' in counters:
            values['service_order_count'] = ServiceOrder.search_count([
                ('partner_id', '=', partner.id)
            ])

        ServiceEquipment = request.env['service.equipment']
        if 'equipment_count' in counters:
            values['equipment_count'] = ServiceEquipment.search_count([
                ('partner_id', '=', partner.id)
            ])

        return values

    @http.route(['/my/service-orders', '/my/service-orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_service_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        ServiceOrder = request.env['service.order']

        domain = [('partner_id', '=', partner.id)]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date_requested desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

        # default sort by date
        if not sortby:
            sortby = 'date'

        order = searchbar_sortings[sortby]['order']

        # count for pager
        service_order_count = ServiceOrder.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/service-orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=service_order_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        service_orders = ServiceOrder.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'service_orders': service_orders,
            'page_name': 'service_order',
            'pager': pager,
            'default_url': '/my/service-orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("modulo.portal_my_service_orders", values)

    @http.route(['/my/service-order/<int:service_order_id>'], type='http', auth="user", website=True)
    def portal_my_service_order(self, service_order_id=None, access_token=None, **kw):
        try:
            service_order_sudo = self._document_check_access('service.order', service_order_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = {
            'service_order': service_order_sudo,
            'page_name': 'service_order',
            'access_token': access_token,
        }

        return request.render("modulo.portal_service_order_page", values)

    @http.route(['/my/service-order/<int:service_order_id>/accept'], type='http', auth="user", website=True)
    def portal_accept_service_order(self, service_order_id=None, access_token=None, **kw):
        try:
            service_order_sudo = self._document_check_access('service.order', service_order_id, access_token)
        except AccessError:
            return request.redirect('/my')

        if service_order_sudo.state == 'scheduled':
            service_order_sudo.write({
                'state': 'in_progress',
                'date_started': fields.Datetime.now()
            })
            
            # Send notification
            if service_order_sudo.technician_id and service_order_sudo.technician_id.user_id:
                service_order_sudo.message_post(
                    body=_("Service order accepted by customer"),
                    partner_ids=service_order_sudo.technician_id.user_id.partner_id.ids
                )

        return request.redirect(f'/my/service-order/{service_order_id}' + (f'?access_token={access_token}' if access_token else ''))

    @http.route(['/my/service-order/<int:service_order_id>/cancel'], type='http', auth="user", website=True)
    def portal_cancel_service_order(self, service_order_id=None, access_token=None, **kw):
        try:
            service_order_sudo = self._document_check_access('service.order', service_order_id, access_token)
        except AccessError:
            return request.redirect('/my')

        if service_order_sudo.state in ('draft', 'scheduled'):
            service_order_sudo.write({'state': 'cancelled'})
            
            # Send notification
            if service_order_sudo.technician_id and service_order_sudo.technician_id.user_id:
                service_order_sudo.message_post(
                    body=_("Service order cancelled by customer"),
                    partner_ids=service_order_sudo.technician_id.user_id.partner_id.ids
                )

        return request.redirect(f'/my/service-order/{service_order_id}' + (f'?access_token={access_token}' if access_token else ''))

    @http.route(['/my/equipment', '/my/equipment/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_equipment(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        ServiceEquipment = request.env['service.equipment']

        domain = [('partner_id', '=', partner.id)]

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'serial': {'label': _('Serial Number'), 'order': 'serial_number'},
            'next_service': {'label': _('Next Service'), 'order': 'next_service_date'},
        }

        # default sort by name
        if not sortby:
            sortby = 'name'

        order = searchbar_sortings[sortby]['order']

        # count for pager
        equipment_count = ServiceEquipment.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/equipment",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=equipment_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        equipment = ServiceEquipment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'equipment': equipment,
            'page_name': 'equipment',
            'pager': pager,
            'default_url': '/my/equipment',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("modulo.portal_my_equipment", values)

    @http.route(['/my/equipment/<int:equipment_id>'], type='http', auth="user", website=True)
    def portal_my_equipment_page(self, equipment_id=None, access_token=None, **kw):
        try:
            equipment_sudo = self._document_check_access('service.equipment', equipment_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = {
            'equipment': equipment_sudo,
            'page_name': 'equipment',
            'access_token': access_token,
        }

        return request.render("modulo.portal_equipment_page", values)

    @http.route(['/my/service-order/<int:service_order_id>/pdf'], type='http', auth="user", website=True)
    def portal_service_order_report(self, service_order_id=None, access_token=None, **kw):
        try:
            service_order_sudo = self._document_check_access('service.order', service_order_id, access_token)
        except AccessError:
            return request.redirect('/my')

        # Print the report
        pdf = request.env.ref('modulo.action_report_service_order')._render_qweb_pdf([service_order_sudo.id])[0]
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="Service_Order_%s.pdf";' % service_order_sudo.name)
        ]
        
        return request.make_response(pdf, headers=pdfhttpheaders)
