/** @odoo-module **/

import { Component } from "@odoo/owl";
import { PieChart } from "../pie_chart/pie_chart";

export class PieChartCard extends Component {
    static template = "estate.PieChartCard";
    static components = { PieChart };
    static props = {
        data: { type: Object },
        label: { type: String, optional: true },
        onSegmentClick: { type: Function, optional: true },
    };
}
