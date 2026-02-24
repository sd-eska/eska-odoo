/** @odoo-module **/

import { Component } from "@odoo/owl";

export class DashboardItem extends Component {
    static template = "estate.DashboardItem";
    static props = {
        slots: { type: Object, optional: true },
        size: { type: Number, optional: true },
    };
    static defaultProps = {
        size: 1,
    };
}
