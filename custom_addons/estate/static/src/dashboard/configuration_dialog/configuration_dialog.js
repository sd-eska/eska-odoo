/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ConfigurationDialog extends Component {
    static template = "estate.ConfigurationDialog";
    static components = { Dialog };
    static props = {
        items: { type: Array },
        enabledItems: { type: Array },
        onApply: { type: Function },
        close: { type: Function },
    };

    setup() {
        this.state = useState({
            enabledItems: [...this.props.enabledItems],
        });
    }

    toggleItem(itemId) {
        if (this.state.enabledItems.includes(itemId)) {
            this.state.enabledItems = this.state.enabledItems.filter(id => id !== itemId);
        } else {
            this.state.enabledItems.push(itemId);
        }
    }

    onApply() {
        this.props.onApply(this.state.enabledItems);
        this.props.close();
    }
}
