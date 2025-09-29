from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ServiceReprogramWizard(models.TransientModel):
    _name = 'service.reprogram.wizard'
    _description = 'Service Reprogram Wizard'

    order_id = fields.Many2one('service.order', string='Service Order', required=True)
    new_date = fields.Datetime(string='New Date', required=True)
    reason = fields.Text(string='Reason', required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.order':
            order = self.env['service.order'].browse(self.env.context['active_id'])
            res['order_id'] = order.id
            if order.date_scheduled:
                res['new_date'] = order.date_scheduled
        return res

    def action_reprogram(self):
        self.ensure_one()

        try:
            # Validate new date
            if not self.new_date:
                raise UserError(_("New date is required"))
            
            if self.new_date < fields.Datetime.now():
                raise UserError(_("Cannot schedule in the past"))
            
            if not self.reason or not self.reason.strip():
                raise UserError(_("Reason is required for reprogramming"))

            # Check for conflicts
            business_logic = self.env['service.order.business.logic']
            temp_order = self.order_id.copy({'date_scheduled': self.new_date})
            conflicts = business_logic.check_service_order_conflicts(temp_order)
            temp_order.unlink()

            if conflicts:
                conflict_messages = [c['reason'] for c in conflicts]
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Scheduling Conflict'),
                        'message': '\n'.join(conflict_messages),
                        'type': 'danger',
                    }
                }

            # Reprogram the service order
            self.order_id.write({
                'date_scheduled': self.new_date,
                'notes': f"{self.order_id.notes or ''}\n\n{_('Reprogrammed')}: {self.reason}",
            })

            # Send notification to customer
            if self.order_id.partner_id.email:
                template = self.env.ref('modulo.email_template_service_reprogrammed', raise_if_not_found=False)
                if template:
                    template.send_mail(self.order_id.id)
                else:
                    _logger.warning("Email template 'modulo.email_template_service_reprogrammed' not found")

            # Send notification to technician
            if self.order_id.technician_id and self.order_id.technician_id.user_id:
                self.env['mail.activity'].create({
                    'res_id': self.order_id.id,
                    'res_model_id': self.env['ir.model']._get('service.order').id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': _('Service Order Reprogrammed'),
                    'note': _('Service order %s has been reprogrammed to %s. Reason: %s') % (
                        self.order_id.name, 
                        self.new_date, 
                        self.reason
                    ),
                    'user_id': self.order_id.technician_id.user_id.id,
                })

            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error("Error reprogramming service order: %s", str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': str(e),
                    'type': 'danger',
                }
            }
