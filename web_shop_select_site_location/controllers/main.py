# -*- coding: utf-8 -*-
import datetime
import requests
import logging
import json
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
odoo_session = requests.Session()


class WenShopSelectSiteLocation(http.Controller):

    @http.route(['/select/pending/sites'], type='http', auth="public", website=True)
    def website_select_delivery_type(self, **post):
        order = request.website.sale_get_order()
        site = post['site_id']
        if site != '0':
            site_id = request.env['crm.team'].sudo().browse(int(site)).site_id.id
        else:
            site_id = order.partner_id.team_id.site_id.id
        order.sudo().write({
            'partner_team_site_id': site_id,
        })
        res = {
            'state': '200',
            'site_address': request.env['crm.team'].sudo().browse(int(site)).site_contact_address
        }

        return json.dumps(res)
