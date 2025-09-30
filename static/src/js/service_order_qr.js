/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { loadBundle } from "@web/core/assets";
import { Component } from "@odoo/owl";
import { useBus } from "@web/core/utils/hooks";

export class ServiceOrderQR extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.actionService = useService("action");
        this.router = useService("router");
        
        useBus(this.env.bus, "service_order:show_qr", (ev) => {
            this.showQRCode(ev.detail.orderId);
        });
    }

    async showQRCode(orderId) {
        // Mostrar indicador de carga
        this.dialog.add(Dialog, {
            title: _t("Loading..."),
            size: "medium",
            body: _t("Please wait while we load the QR code."),
        });

        try {
            // Obtener datos de la orden de servicio
            const result = await this.orm.call('service.order', 'read', [[orderId], ['name', 'partner_id', 'qr_code', 'state']]);
            
            if (result.length === 0) {
                throw new Error(_t("Service Order not found"));
            }
            
            let order = result[0];
            
            // Verificar si el código QR existe
            if (!order.qr_code) {
                // Si no existe, generarlo
                order.qr_code = await this.orm.call('service.order', 'generate_qr_code', [orderId]);
            }
            
            // Cerrar diálogo de carga
            this.dialog.close();
            
            // Mostrar diálogo con el código QR
            this.dialog.add(Dialog, {
                title: _t("Service Order QR Code"),
                size: "medium",
                body: this.renderDialogContent(order),
                buttons: [
                    {
                        text: _t("Download"),
                        classes: 'btn-primary',
                        click: () => this.downloadQRCode(order.qr_code, order.name),
                    },
                    {
                        text: _t("Print"),
                        classes: 'btn-secondary',
                        click: () => this.printQRCode(order.qr_code, order.name, order.partner_id ? order.partner_id[1] : ''),
                    },
                    {
                        text: _t("Close"),
                        close: true,
                    },
                ],
            });
            
        } catch (error) {
            // Cerrar diálogo de carga
            this.dialog.close();
            
            // Mostrar mensaje de error
            this.notification.add(error.message || _t("An error occurred while loading the QR code."), {
                type: "danger",
            });
        }
    }

    renderDialogContent(order) {
        return `
            <div class="text-center">
                <h4>${order.name}</h4>
                <p>${_t("Customer")}: ${order.partner_id ? order.partner_id[1] : ''}</p>
                <p>${_t("Status")}: ${order.state}</p>
                <img src="data:image/png;base64,${order.qr_code}" class="img-fluid" alt="QR Code" style="max-width: 200px;"/>
            </div>
        `;
    }

    downloadQRCode(qrCode, orderName) {
        const link = document.createElement('a');
        link.href = 'data:image/png;base64,' + qrCode;
        link.download = 'QR_Code_' + orderName.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    printQRCode(qrCode, orderName, customerName) {
        const printWindow = browser.open('', '_blank');
        const printContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>${_t("Service Order QR Code")}</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; }
                    .header { margin-bottom: 20px; }
                    .qr-container { margin: 20px 0; }
                    .footer { margin-top: 20px; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>${orderName}</h2>
                    <p><strong>${_t("Customer")}:</strong> ${customerName}</p>
                </div>
                <div class="qr-container">
                    <img src="data:image/png;base64,${qrCode}" alt="QR Code" style="max-width: 200px;"/>
                </div>
                <div class="footer">
                    <p>${_t("Generated on")} ${new Date().toLocaleDateString()}</p>
                </div>
            </body>
            </html>
        `;

        printWindow.document.write(printContent);
        printWindow.document.close();

        // Esperar a que se cargue el contenido antes de imprimir
        printWindow.onload = function() {
            printWindow.print();
            printWindow.close();
        };
    }
}

// Registrar el componente para que esté disponible
export const serviceOrderQRService = {
    start() {
        // Inicializar eventos para los botones de QR
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('o_service_order_qr_button')) {
                event.preventDefault();
                const orderId = event.target.dataset.orderId;
                this.env.bus.trigger("service_order:show_qr", { orderId });
            }
        });
    },
};

import { registry } from "@web/core/registry";
registry.category("services").add("service_order_qr", serviceOrderQRService);
