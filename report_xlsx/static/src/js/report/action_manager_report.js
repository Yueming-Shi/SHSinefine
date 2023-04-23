/** @odoo-module **/

import { download } from "@web/core/network/download";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

async function xlsx_report_download(action, options, env) {
     if (action.report_type != "xlsx") {
     	 return;
     }
    let url = `/report/xlsx/${action.report_name}`;
    const actionContext = action.context || {};
    url += `/${actionContext.active_ids.join(",")}`;

    env.services.ui.block();
    try {
        await download({
            url: "/report/download",
            data: {
                data: JSON.stringify([url, action.report_type]),
                context: JSON.stringify(env.services.user.context),
            },
        });
    } finally {
        env.services.ui.unblock();
    }
    const onClose = options.onClose;
    if (action.close_on_report_download) {
        return env.services.action.doAction({ type: "ir.actions.act_window_close" }, { onClose });
    } else if (onClose) {
        onClose();
        return true;
    }
}

registry.category("ir.actions.report handlers").add("xlsx_handler", xlsx_report_download);
