/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "../dashboard_item/dashboard_item";
import { NumberCard } from "../number_card/number_card";
import { PieChartCard } from "../pie_chart_card/pie_chart_card";
import { ConfigurationDialog } from "../configuration_dialog/configuration_dialog";
import { useDashboardConfig } from "../dashboard_hooks";

export class EstateSummary extends Component {
    static template = "estate.EstateSummary";
    static components = { Layout, DashboardItem, NumberCard, PieChartCard, ConfigurationDialog };

    setup() {
        // 1. Servisler ve Kayıtlar
        this.items = registry.category("awesome_dashboard").getAll();
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.rpc = useService("rpc");

        // Veri yönetimini servis üzerinden yapıyoruz (Modülerlik)
        this.statistics = useService("awesome_dashboard.statistics");
        this.stats = useState(this.statistics.stats);

        // 2. Özel Hook Kullanımı (Konfigürasyon yönetimi)
        this.config = useDashboardConfig(this.items, this.rpc);

        // 3. Yaşam Döngüsü
        onWillStart(async () => {
            // İlk verinin ve ayarların yüklenmesini bekle
            await Promise.all([
                this.statistics.initialLoad,
                this.config.initialLoad
            ]);
        });

        this.display = {
            controlPanel: { "top-right": false, "bottom-right": false },
        };
    }

    get filteredItems() {
        return this.items.filter(item => this.config.enabledItems.includes(item.id));
    }

    openConfiguration() {
        this.dialog.add(ConfigurationDialog, {
            items: this.items,
            enabledItems: this.config.enabledItems,
            onApply: (newEnabledItems) => {
                this.config.update(newEnabledItems);
            },
        });
    }

    openCustomers() {
        this.action.doAction("base.action_partner_form");
    }

    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Leads",
            res_model: "crm.lead",
            views: [[false, "list"], [false, "form"]],
        });
    }
}

registry.category("lazy_components").add("EstateSummary", EstateSummary);
