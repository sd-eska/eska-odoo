/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

export const statisticsService = {
    dependencies: ["rpc"],
    start(env, { rpc }) {
        const stats = reactive({ data: {} });

        async function _loadStatistics() {
            const data = await rpc("/awesome_dashboard/statistics");
            Object.assign(stats.data, data);
        }

        // Initial load
        const initialLoad = _loadStatistics();

        // 10s refresh for testing (10 * 60 * 1000 for 10 min)
        const interval = setInterval(_loadStatistics, 10000);

        return {
            stats,
            initialLoad, // Useful for waiting on first load in onWillStart
        };
    },
};

registry.category("services").add("awesome_dashboard.statistics", statisticsService);
