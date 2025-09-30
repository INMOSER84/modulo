/** @odoo-module **/

import { CalendarView } from "@web/views/calendar/calendar_view";
import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
import { CalendarModel } from "@web/views/calendar/calendar_model";
import { viewRegistry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";

export class ServiceOrderCalendarModel extends CalendarModel {
    async load(params) {
        params.domain = params.domain || [];
        
        // Filtrar por estados relevantes
        params.domain.push(['state', 'in', ['pending', 'in_progress', 'scheduled']]);
        
        const result = await super.load(params);
        return result;
    }

    getCalendarEventRecord(record) {
        const event = super.getCalendarEventRecord(record);
        
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
    }
}

export class ServiceOrderCalendarRenderer extends CalendarRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");
    }

    getEventClass(event) {
        let classes = super.getEventClass(event);
        
        // Agregar clase según el estado para diferentes colores
        if (event.state === 'pending') {
            classes += ' o_event_pending';
        } else if (event.state === 'in_progress') {
            classes += ' o_event_in_progress';
        } else if (event.state === 'scheduled') {
            classes += ' o_event_scheduled';
        }
        
        return classes;
    }

    getEventContent(event) {
        let content = super.getEventContent(event);
        
        // Agregar información adicional al evento
        let title = event.title;
        if (event.partner_name) {
            title += ' - ' + event.partner_name;
        }
        if (event.technician_name) {
            title += ' (' + event.technician_name + ')';
        }
        
        content.title = title;
        return content;
    }

    getEventTooltip(event) {
        let tooltip = '<div class="o_calendar_tooltip">';
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
    }

    async onEventClicked(event) {
        const { id } = event;
        const action = {
            type: "ir.actions.act_window",
            res_model: "service.order",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        };
        this.actionService.doAction(action);
    }
}

export class ServiceOrderCalendarView extends CalendarView {
    setup() {
        super.setup();
        this.renderer = ServiceOrderCalendarRenderer;
        this.model = ServiceOrderCalendarModel;
    }

    get viewParams() {
        const params = super.viewParams;
        
        // Configurar campos del calendario
        return {
            ...params,
            dateStart: 'scheduled_date',
            dateStop: 'scheduled_date_end',
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
            quickCreate: false,
        };
    }
}

ServiceOrderCalendarView.display_name = _t('Service Order Calendar');
ServiceOrderCalendarView.icon = 'fa-calendar';
ServiceOrderCalendarView.multiRecord = true;
ServiceOrderCalendarView.searchMenuTypes = ['filter', 'groupBy'];

viewRegistry.add('service_order_calendar', ServiceOrderCalendarView);

