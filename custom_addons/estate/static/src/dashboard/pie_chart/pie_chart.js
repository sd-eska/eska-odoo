/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
    static template = "estate.PieChart";
    static props = {
        data: { type: Object },
        label: { type: String, optional: true },
        onSegmentClick: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
        });

        onMounted(() => {
            this.renderChart();
        });
    }

    renderChart() {
        const labels = Object.keys(this.props.data);
        const values = Object.values(this.props.data);

        this.chart = new Chart(this.canvasRef.el, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#ff6384',
                        '#36a2eb',
                        '#cc65fe',
                        '#ffce56'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0 && this.props.onSegmentClick) {
                        const index = activeElements[0].index;
                        const label = labels[index];
                        const value = values[index];
                        this.props.onSegmentClick({ label, value, index });
                    }
                }
            }
        });
    }
}
