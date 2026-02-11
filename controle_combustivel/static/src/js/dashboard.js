/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class FuelDashboard extends Component {
    static template = "controle_combustivel.FuelDashboard";

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            data: {}
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        const data = await this.rpc("/combustivel/dashboard/data");
        Object.assign(this.state.data, data);
    }

    async createAbastecimento() {
        this.action.doAction("controle_combustivel.action_abastecimento_tree", {
            additionalContext: {
                default_state: 'rascunho'
            }
        });
    }
}

registry.category("actions").add("controle_combustivel.dashboard", FuelDashboard);
