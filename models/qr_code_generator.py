from odoo import models, fields, api
import logging
import io
import base64

_logger = logging.getLogger(__name__)

class QRCodeGenerator(models.AbstractModel):
    _name = 'qr.code.generator'
    _description = 'QR Code Generator'

    qr_code = fields.Binary(string='QR Code', compute='_generate_qr_code', store=True)

    @api.depends('name')
    def _generate_qr_code(self):
        for record in self:
            try:
                import qrcode
                from qrcode import constants

                qr_data = self._get_qr_data(record)
                if qr_data:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)

                    img = qr.make_image(fill_color="black", back_color="white")

                    # Convert to base64
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    img_str = base64.b64encode(buffer.getvalue())

                    record.qr_code = img_str
                else:
                    record.qr_code = False
            except ImportError:
                _logger.warning("qrcode library not found. Please install it: pip install qrcode[pil]")
                record.qr_code = False
            except Exception as e:
                _logger.error("Error generating QR code: %s", str(e))
                record.qr_code = False

    def _get_qr_data(self, record):
        """Override this method to provide QR data for specific models"""
        return None
