from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ServiceCompleteWizard(models.TransientModel):
    _name = 'service.complete.wizard'
    _description = 'Service Complete Wizard'

    order_id = fields.Many2one('service.order', string='Service Order', required=True)
    completion_date = fields.Datetime(string='Completion Date', default=fields.Datetime.now, required=True)
    notes = fields.Text(string='Completion Notes')
    line_ids = fields.One2many('service.complete.wizard.line', 'wizard_id', string='Refaction Lines')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.order':
            order = self.env['service.order'].browse(self.env.context['active_id'])
            res['order_id'] = order.id

            # Create default lines from existing refaction lines
            lines = []
            for line in order.refaction_line_ids:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'unit_price': line.unit_price,
                    'notes': line.notes,
                }))
            res['line_ids'] = lines
        return res

    def action_complete(self):
        self.ensure_one()

        try:
            # Validate completion date
            if not self.completion_date:
                raise UserError(_("Completion date is required"))
            
            if self.order_id.date_started and self.completion_date < self.order_id.date_started:
                raise UserError(_("Completion date cannot be before start date"))

            # Update refaction lines
            for line in self.line_ids:
                if not line.exists():
                    # Create new refaction line
                    self.env['service.order.refaction.line'].create({
                        'order_id': self.order_id.id,
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'unit_price': line.unit_price,
                        'notes': line.notes,
                    })
                else:
                    # Update existing refaction line
                    line.write({
                        'quantity': line.quantity,
                        'unit_price': line.unit_price,
                        'notes': line.notes,
                    })

            # Complete the service order
            self.order_id.write({
                'date_completed': self.completion_date,
                'notes': self.notes,
                'state': 'completed'
            })

            # Send notification
            template = self.env.ref('modulo.email_template_service_completed', raise_if_not_found=False)
            if template:
                template.send_mail(self.order_id.id)
            else:
                _logger.warning("Email template 'modulo.email_template_service_completed' not found")

            # Create activity for technician if assigned
            if self.order_id.technician_id and self.order_id.technician_id.user_id:
                self.env['mail.activity'].create({
                    'res_id': self.order_id.id,
                    'res_model_id': self.env['ir.model']._get('service.order').id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': _('Service Order Completed'),
                    'note': _('Service order %s has been completed.') % self.order_id.name,
                    'user_id': self.order_id.technician_id.user_id.id,
                })

            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error("Error completing service order: %s", str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': str(e),
                    'type': 'danger',
                }
            }
