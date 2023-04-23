# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

import logging

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.urls import url_join, url_encode

_logger = logging.getLogger(__name__)


class Controller(http.Controller):

    @http.route('/my/personal/home', type='http', auth='public', methods=['GET'], website=True)
    def sale_fill_order_create_view(self):
        partner = request.env.user.partner_id
        order = request.website.sale_get_order()
        wishlist = request.env['product.wishlist'].with_context(display_default_code=False).current()
        values = {
            'partner': partner,
            'website_sale_order': order,
            'wishlist': wishlist
        }
        return request.render('zhaogu_website_my_home.haitao_website_my_home', values)



