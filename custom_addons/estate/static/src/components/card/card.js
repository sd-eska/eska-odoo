/** @odoo-module **/

import { Component } from "@odoo/owl";

export class Card extends Component {
    static template = "estate.Card";
    static props = {
        title: { type: String },
        content: { type: String },
    };
}
