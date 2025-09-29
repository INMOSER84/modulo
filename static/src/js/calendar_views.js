odoo.define('inmoser_service_order.calendar_views', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');
    var CalendarRenderer = require('web.CalendarRenderer');
    var CalendarModel = require('web.CalendarModel');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var _t = core._t;

    var ServiceOrderCalendarModel = CalendarModel.extend({
        /**
         * Sobrescribir el método load para filtrar órdenes de servicio
         * por estado y técnico asignado
         */
        load: function (params) {
            var self = this;
            params.domain = params.domain || [];
            
            // Filtrar por estados relevantes
            params.domain.push(['state', 'in', ['pending', 'in_progress', 'scheduled']]);
            
            return this._super(params);
        },

        /**
         * Obtener información adicional para mostrar en el calendario
         */
        getCalendarEventRecord: function (record) {
            var event = this._super(record);
            
            // Agregar información del cliente
            if (record.partner_id) {
                event.partner_name = record.partner_id[1];
            }
            
            // Agregar información del técnico
            if (record.technician_id) {
                event.technician_name = record.technician_id[1];
            }
            
            // Agregar tipo de servicio
            if (record.service_type_id) {
                event.service_type = record.service_type_id[1];
            }
            
            return event;
        },
    });

    var ServiceOrderCalendarRenderer = CalendarRenderer.extend({
        /**
         * Personalizar la visualización de eventos en el calendario
         */
        render_event: function (event) {
            var $event = this._super(event);
            
            // Agregar información adicional al evento
            var title = event.title;
            if (event.partner_name) {
                title += ' - ' + event.partner_name;
            }
            if (event.technician_name) {
                title += ' (' + event.technician_name + ')';
            }
            
            $event.find('.fc-title').text(title);
            
            // Agregar clase según el estado para diferentes colores
            if (event.state === 'pending') {
                $event.addClass('o_event_pending');
            } else if (event.state === 'in_progress') {
                $event.addClass('o_event_in_progress');
            } else if (event.state === 'scheduled') {
                $event.addClass('o_event_scheduled');
            }
            
            return $event;
        },

        /**
         * Personalizar el tooltip del evento
         */
        getEventTooltip: function (event) {
            var tooltip = '<div class="o_calendar_tooltip">';
            tooltip += '<strong>' + event.title + '</strong><br/>';
            
            if (event.partner_name) {
                tooltip += _t('Customer: ') + event.partner_name + '<br/>';
            }
            
            if (event.technician_name) {
                tooltip += _t('Technician: ') + event.technician_name + '<br/>';
            }
            
            if (event.service_type) {
                tooltip += _t('Service Type: ') + event.service_type + '<br/>';
            }
            
            tooltip += _t('Status: ') + event.state + '<br/>';
            tooltip += '</div>';
            
            return tooltip;
        },
    });

    var ServiceOrderCalendarView = CalendarView.extend({
        config: _.extend({}, CalendarView.prototype.config, {
            Model: ServiceOrderCalendarModel,
            Renderer: ServiceOrderCalendarRenderer,
        }),
        display_name: _t('Service Order Calendar'),
        icon: 'fa-calendar',
        calendarView: 'week',
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            
            // Configurar campos del calendario
            this.arch.attrs = _.extend({}, this.arch.attrs, {
                date_start: 'scheduled_date',
                date_stop: 'scheduled_date_end',
                color: 'technician_id',
                filters: [
                    {
                        field: 'technician_id',
                        name: _t('Technician'),
                    },
                    {
                        field: 'state',
                        name: _t('State'),
                    },
                ],
                mode: 'week',
                quick_create: false,
            });
        },
    });

    viewRegistry.add('service_order_calendar', ServiceOrderCalendarView);

    return {
        ServiceOrderCalendarModel: ServiceOrderCalendarModel,
        ServiceOrderCalendarRenderer: ServiceOrderCalendarRenderer,
        ServiceOrderCalendarView: ServiceOrderCalendarView,
    };
});
