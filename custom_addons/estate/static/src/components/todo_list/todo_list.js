/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { TodoItem } from "../todo_item/todo_item";

export class TodoList extends Component {
    static template = "estate.TodoList";
    static components = { TodoItem };

    setup() {
        this.todos = useState([]);
        this.nextId = 1;
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value.trim() !== "") {
            this.todos.push({
                id: this.nextId++,
                description: ev.target.value.trim(),
                isCompleted: false,
            });
            ev.target.value = "";
        }
    }
}
