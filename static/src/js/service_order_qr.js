odoo.define('inmoser_service_order.service_order_qr', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;

    var _t = core._t;

    var ServiceOrderQR = {
        /**
         * Inicializa el módulo de códigos QR
         */
        init: function () {
            this.setupQRCodes();
        },

        /**
         * Configura los eventos para los botones de código QR
         */
        setupQRCodes: function () {
            var self = this;
            $(document).on('click', '.o_service_order_qr_button', function (e) {
                e.preventDefault();
                var orderId = $(this).data('order-id');
                self.showQRCode(orderId);
            });
        },

        /**
         * Muestra el diálogo con el código QR de la orden de servicio
         * @param {integer} orderId - ID de la orden de servicio
         */
        showQRCode: function (orderId) {
            var self = this;
            
            // Mostrar indicador de carga
            framework.blockUI();
            
            self._rpc({
                model: 'service.order',
                method: 'read',
                args: [[orderId], ['name', 'partner_id', 'qr_code', 'state']],
            }).then(function (result) {
                if (result.length > 0) {
                    var order = result[0];
                    
                    // Verificar si el código QR existe
                    if (!order.qr_code) {
                        // Si no existe, generarlo
                        return self.generateQRCode(orderId).then(function(qrCode) {
                            order.qr_code = qrCode;
                            return order;
                        });
                    }
                    return order;
                } else {
                    return $.Deferred().reject(_t("Service Order not found"));
                }
            }).then(function(order) {
                // Renderizar el contenido del diálogo
                var $content = $(QWeb.render('service_order_qr_modal', {
                    service_order_name: order.name,
                    customer_name: order.partner_id ? order.partner_id[1] : '',
                    qr_code_image: 'data:image/png;base64,' + order.qr_code,
                    state: order.state,
                }));

                // Crear y mostrar el diálogo
                var dialog = new Dialog(self, {
                    title: _t("Service Order QR Code"),
                    size: 'medium',
                    $content: $content,
                    buttons: [
                        {
                            text: _t("Download"),
                            classes: 'btn-primary',
                            click: function () {
                                self.downloadQRCode(order.qr_code, order.name);
                            },
                        },
                        {
                            text: _t("Print"),
                            classes: 'btn-secondary',
                            click: function () {
                                self.printQRCode(order.qr_code, order.name, order.partner_id ? order.partner_id[1] : '');
                            },
                        },
                        {
                            text: _t("Close"),
                            close: true,
                        },
                    ],
                }).open();
                
                return order;
            }).fail(function(error) {
                // Mostrar mensaje de error
                Dialog.alert(self, {
                    title: _t("Error"),
                    message: error || _t("An error occurred while loading the QR code."),
                });
            }).always(function() {
                // Ocultar indicador de carga
                framework.unblockUI();
            });
        },

        /**
         * Genera un código QR para la orden de servicio
         * @param {integer} orderId - ID de la orden de servicio
         * @returns {Deferred} - Promesa que resuelve con el código QR en base64
         */
        generateQRCode: function(orderId) {
            var self = this;
            return self._rpc({
                model: 'service.order',
                method: 'generate_qr_code',
                args: [orderId],
            });
        },

        /**
         * Descarga el código QR como una imagen PNG
         * @param {string} qrCode - Código QR en base64
         * @param {string} orderName - Nombre de la orden de servicio
         */
        downloadQRCode: function (qrCode, orderName) {
            var link = document.createElement('a');
            link.href = 'data:image/png;base64,' + qrCode;
            link.download = 'QR_Code_' + orderName.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        /**
         * Imprime el código QR con información de la orden
         * @param {string} qrCode - Código QR en base64
         * @param {string} orderName - Nombre de la orden de servicio
         * @param {string} customerName - Nombre del cliente
         */
        printQRCode: function (qrCode, orderName, customerName) {
            var printWindow = window.open('', '_blank');
            var printContent = QWeb.render('service_order_qr_print', {
                service_order_name: orderName,
                customer_name: customerName,
                qr_code_image: 'data:image/png;base64,' + qrCode,
                current_date: new Date().toLocaleDateString(),
            });
            
            printWindow.document.write(printContent);
            printWindow.document.close();
            
            // Esperar a que se cargue el contenido antes de imprimir
            printWindow.onload = function() {
                printWindow.print();
                printWindow.close();
            };
        },
    };

    // Inicializar cuando el cliente web esté listo
    core.bus.on('web_client_ready', null, function () {
        ServiceOrderQR.init();
    });

    return ServiceOrderQR;
});
