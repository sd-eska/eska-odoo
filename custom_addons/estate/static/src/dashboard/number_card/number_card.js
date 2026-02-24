/** @odoo-module **/

import { Component } from "@odoo/owl";

export class NumberCard extends Component {
    static template = "estate.NumberCard";
    static props = {
        title: { type: String },
        value: { type: [String, Number] },
        color: { type: String, optional: true },
    };
}
