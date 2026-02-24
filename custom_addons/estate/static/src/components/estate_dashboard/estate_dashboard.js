/** @odoo-module **/

import { Component, useState, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Counter } from "../counter/counter";
import { Card } from "../card/card";
import { TodoList } from "../todo_list/todo_list";

export class EstateDashboard extends Component {
    static components = { Counter, Card, TodoList };

    setup() {
        this.state = useState({
            message: "Emlak Yönetim Paneli",
            safeHtml: markup("<em class='text-success'>Güvenli HTML:</em> Bu metin <strong>kalın</strong> ve düzgün işlenir."),
            unseenHtml: "<em class='text-danger'>Tehlikeli HTML:</em> Bu metin olduğu gibi (string) görünecektir.",
            sum: 0,
        });
    }

    incrementSum() {
        this.state.sum++;
    }
}

EstateDashboard.template = "estate.EstateDashboard";

registry.category("actions").add("estate_dashboard_action", EstateDashboard);
