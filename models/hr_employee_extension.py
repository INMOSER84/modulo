from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Campos para información de servicio
    is_technician = fields.Boolean(string='Is Technician', default=False)
    technician_code = fields.Char(string='Technician Code')
    specialization = fields.Char(string='Specialization')
    certification = fields.Char(string='Certification')
    certification_date = fields.Date(string='Certification Date')
    certification_expiry = fields.Date(string='Certification Expiry')
    service_order_count = fields.Integer(compute='_compute_service_order_count', string='Service Orders')

    def _compute_service_order_count(self):
        for employee in self:
            employee.service_order_count = self.env['service.order'].search_count([
                ('technician_id', '=', employee.id)
            ])

    def action_view_service_orders(self):
        self.ensure_one()
        action = self.env.ref('modulo.action_service_order').read()[0]
        action['domain'] = [('technician_id', '=', self.id)]
        action['context'] = {'default_technician_id': self.id}
        return action

    def check_certification_validity(self):
        """Check if certification is still valid"""
        for employee in self:
            if employee.certification_expiry and employee.certification_expiry < fields.Date.today():
                # Send notification to manager
                manager = employee.parent_id or employee.department_id.manager_id
                if manager:
                    self.env['mail.thread'].message_notify(
                        partner_ids=manager.partner_id.ids,
                        subject=_("Certification Expired for %s") % employee.name,
                        body=_("The certification for %s has expired on %s.") % (employee.name, employee.certification_expiry),
                        email_layout_xmlid='mail.mail_notification_light'
                    )
