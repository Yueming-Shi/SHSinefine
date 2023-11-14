# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.
import datetime
import logging
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class Controller(http.Controller):

    def _login_redirect(self, uid, redirect=None):
        """ Redirect regular users (employees) to the backend) and others to
        the frontend
        """
        if not redirect and request.params.get('login_success'):
            if request.env['res.users'].browse(uid).has_group('base.group_user'):
                redirect = '/web?' + request.httprequest.query_string.decode()
            else:
                redirect = '/'
        return super()._login_redirect(uid, redirect=redirect)

    @http.route('/my/personal/home', type='http', auth='public', methods=['GET'], website=True)
    def sale_fill_order_create_view(self):
        partner = request.env.user.partner_id
        order = request.website.sale_get_order()
        wishlist = request.env['product.wishlist'].with_context(display_default_code=False).current()
        banner = request.env['web.protal.img'].sudo().search([])

        website_footprint = request.env['website.visitor'].sudo().search([('partner_id', '=', partner.id)])
        product_website_footprint = website_footprint.website_track_ids.filtered(lambda l:l.product_id and l.visit_datetime > datetime.now() - timedelta(days=5))

        banner_top = []
        banner_bottom = []
        if banner:
            banner_top = request.env['web.protal.img'].sudo().search([('banner_position', '=', '0')], limit=5)
            banner_bottom = request.env['web.protal.img'].sudo().search([('banner_position', '=', '1')], limit=5)
        banner_obj = {'banner_top': banner_top, 'banner_bottom': banner_bottom}
        values = {
            'partner': partner,
            'website_sale_order': order,
            'wishlist': wishlist,
            'banner': banner_obj,
            'product_website_footprint_len': len(product_website_footprint)
        }
        return request.render('zhaogu_website_my_home.haitao_website_my_home', values)

    @http.route('/my/footprint', type='http', auth='public', methods=['GET'], website=True)
    def show_my_footprint(self):
        partner = request.env.user.partner_id
        website_footprint = request.env['website.visitor'].sudo().search([('partner_id', '=', partner.id)])
        product_website_footprint = website_footprint.website_track_ids.filtered(lambda l:l.product_id and l.visit_datetime > datetime.now() - timedelta(days=5))
        values = {
            'partner': partner,
            'product_website_footprint': product_website_footprint
        }
        return request.render('zhaogu_website_my_home.my_footprint', values)

    @http.route('/my/order', type='http', auth='public', methods=['GET'], website=True)
    def show_my_order(self, type):
        partner = request.env.user.partner_id
        orders_list = request.env['sale.order'].sudo().search([('partner_id', '=', partner.id), ('website_id', '=', request.website.id)])
        if type == 'dfh':
            orders = orders_list.filtered(lambda l: l.picking_ids and ('cancel' not in l.picking_ids.mapped('state') or 'done' not in l.picking_ids.mapped('state'))) + orders_list.filtered(lambda l: not l.picking_ids)
            type = '待发货'
        else:
            orders = orders_list.filtered(lambda l: 'cancel' in l.picking_ids.mapped('state'))
            type = '历史订单'
        values = {
            'partner': partner,
            'orders': orders,
            'type': type
        }
        return request.render('zhaogu_website_my_home.my_shop_sale_order', values)

    @http.route('/my/evaluated', type='http', auth='public', website=True, methods=['GET'])
    def show_my_evaluated(self, **kwargs):
        partner = request.env.user.partner_id

        if request.httprequest.method == 'POST':
            product_id = request.env['product.product'].sudo().browse(int(kwargs.get('product_id')))
            rating = int(kwargs.get('rating'))
            message = kwargs.get('message')
            values = {
                'rating': rating,
                'consumed': True,
                'feedback': message,
                'is_internal': False,
                'res_id': product_id.product_tmpl_id.id,
                'res_model_id': request.env['ir.model'].sudo()._get_id('product.template'),
                'partner_id': partner.id
            }
            request.env['rating.rating'].sudo().create(values)
            return request.redirect('/my/evaluated')

        orders_list = request.env['sale.order'].sudo().search([('partner_id', '=', partner.id), ('website_id', '=', request.website.id)])
        product_ids = orders_list.order_line.filtered(lambda l: l.product_id.detailed_type != 'service' and l.state in ['sale', 'done'])
        values = {
            'partner': partner,
            'product_ids': product_ids
        }
        return request.render('zhaogu_website_my_home.my_be_evaluated_order', values)

    @http.route('/submit/product/message', type='http', auth='public', website=True, methods=['POST'])
    def submit_product_message(self, **kwargs):
        partner = request.env.user.partner_id
        product_id = request.env['product.template'].sudo().browse(int(kwargs.get('product_id')))
        rating = int(kwargs.get('rating'))
        message = kwargs.get('message')

        # 创建消息
        mail_message = request.env['mail.message'].sudo().create({
            'message_type': 'comment',
            'subtype_id': 1,
            'model': 'product.template',
            'res_id': product_id.id,
            'record_name': product_id.display_name,
            'body': message
        })

        values = {
            'rating': rating,
            'consumed': True,
            'feedback': message,
            'is_internal': False,
            'res_id': product_id.id,
            'res_model_id': request.env['ir.model'].sudo()._get_id('product.template'),
            'partner_id': partner.id,
            'message_id': mail_message.id
        }
        request.env['rating.rating'].sudo().create(values)
        return request.redirect('/my/evaluated')

