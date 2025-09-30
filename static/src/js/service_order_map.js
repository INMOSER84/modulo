/** @odoo-module **/

import { MapController } from "@web/views/map/map_controller";
import { MapRenderer } from "@web/views/map/map_renderer";
import { MapModel } from "@web/views/map/map_model";
import { viewRegistry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class ServiceOrderMapRenderer extends MapRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    getMarkers() {
        const markers = super.getMarkers();
        // Personalizar marcadores según el estado
        return markers.map(marker => {
            let color = "#3498db"; // Color por defecto
            if (marker.state === 'done') {
                color = "#2ecc71"; // Verde para completadas
            } else if (marker.state === 'in_progress') {
                color = "#f39c12"; // Naranja para en progreso
            } else if (marker.state === 'cancel') {
                color = "#e74c3c"; // Rojo para canceladas
            }
            return {...marker, color};
        });
    }
}

export class ServiceOrderMapModel extends MapModel {
    async load(params) {
        const result = await super.load(params);
        // Personalizar la carga de datos para el mapa
        return result;
    }
}

export class ServiceOrderMapController extends MapController {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    async onMarkerClicked(marker) {
        const { id } = marker;
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

viewRegistry.add("service_order_map", {
    ...MapController,
    Model: ServiceOrderMapModel,
    Renderer: ServiceOrderMapRenderer,
    Controller: ServiceOrderMapController,
    display_name: _t('Service Order Map'),
    icon: 'fa-map-marker-alt',
});
