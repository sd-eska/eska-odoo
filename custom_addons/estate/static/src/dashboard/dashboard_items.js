/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { NumberCard } from "./number_card/number_card";
import { PieChartCard } from "./pie_chart_card/pie_chart_card";

const itemsRegistry = registry.category("awesome_dashboard");

itemsRegistry
    .add("new_orders", {
        id: "new_orders",
        description: _t("New orders this month"),
        Component: NumberCard,
        props: (data) => ({
            title: _t("New Orders"),
            value: data.new_orders_this_month,
            color: "primary",
        }),
    })
    .add("total_amount", {
        id: "total_amount",
        description: _t("Total amount of new orders"),
        Component: NumberCard,
        props: (data) => ({
            title: _t("Total Amount"),
            value: data.total_amount_new_orders + " ₺",
            color: "success",
        }),
    })
    .add("avg_tshirts", {
        id: "avg_tshirts",
        description: _t("Average t-shirts per order"),
        Component: NumberCard,
        props: (data) => ({
            title: _t("Avg. T-Shirts"),
            value: data.average_tshirts_per_order,
            color: "info",
        }),
    })
    .add("cancelled_orders", {
        id: "cancelled_orders",
        description: _t("Cancelled orders this month"),
        Component: NumberCard,
        props: (data) => ({
            title: _t("Cancelled Orders"),
            value: data.cancelled_orders_this_month,
            color: "danger",
        }),
    })
    .add("avg_time", {
        id: "avg_time",
        description: _t("Average time to process"),
        Component: NumberCard,
        size: 2,
        props: (data) => ({
            title: _t("Avg. Processing Time (New to Sent/Cancelled)"),
            value: data.average_time_to_process + " " + _t("Days"),
            color: "warning",
        }),
    })
    .add("tshirt_sizes", {
        id: "tshirt_sizes",
        description: _t("T-shirt sizes distribution"),
        Component: PieChartCard,
        size: 2,
        props: (data, action) => ({
            label: _t("T-Shirt Sizes Distribution"),
            data: data.tshirt_sizes,
            onSegmentClick: (segment) => {
                // Open filtered list view for the clicked t-shirt size
                action.doAction({
                    type: "ir.actions.act_window",
                    name: _t("Properties - Size %s", segment.label),
                    res_model: "estate.property",
                    views: [[false, "list"], [false, "form"]],
                    domain: [["name", "ilike", segment.label]],
                });
            },
        }),
    });
