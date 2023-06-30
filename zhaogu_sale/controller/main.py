# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

import logging

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request, content_disposition, Controller, route
from werkzeug.urls import url_join, url_encode
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


class Controller(http.Controller):

    @http.route('/order/nocustomer', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def sale_fill_order_create_view(self, waybill_no=False):
        partner_type = request.env.user.partner_id.partner_vip_type
        partner = request.env.user.partner_id
        # 不可改泡
        no_change = True

        if partner_type == 'svip':
            no_change = False

        values = {
            'user_name': request.env.user.name,
            'waybill_no': waybill_no,
            'no_change': no_change,
            'partner': partner
        }
        return request.render('zhaogu_sale.sale_portal_fill_order_create_template', values)

    @http.route('/sale/create/documents', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def sale_fill_order_create(self, **kwargs):
        user = request.env.user
        partner_type = request.env.user.partner_id.partner_vip_type
        partner = request.env.user.partner_id
        if kwargs.get('select_site') != '0':
            partner_team_site_id = int(kwargs.get('select_site'))
        else:
            partner_team_site_id = user.partner_id.team_id.site_id.id
        no_change = False
        if partner_type in ['svip', 'vip']:
            no_change = True
        sale_shipping_no = request.env['sale.order'].sudo().search(
            [('shipping_no', '=', kwargs.get('shipping_no'))])

        if sale_shipping_no and sale_shipping_no.partner_id.id != user.partner_id.id:
            values = {
                'user_name': request.env.user.name,
                'error_message': '运单号已存在。',
                'waybill_no': False,
                'no_change': no_change,
                'partner': partner
            }
            return request.render('zhaogu_sale.sale_portal_fill_order_create_template', values)
        elif sale_shipping_no and sale_shipping_no.partner_id.user_ids.id == user.id and not sale_shipping_no.shipping_bill_id:
            return request.redirect('/sale/portal/fill_order?order_id=' + str(sale_shipping_no.id))
        elif sale_shipping_no and sale_shipping_no.partner_id.user_ids.id == user.id and sale_shipping_no.shipping_bill_id:
            values = {
                'user_name': request.env.user.name,
                'error_message': '运单号已存在。',
                'waybill_no': False,
                'no_change': no_change,
                'partner': partner
            }
            return request.render('zhaogu_sale.sale_portal_fill_order_create_template', values)
        else:
            values = {
                'partner_id': user.partner_id.id,
                'shipping_no': kwargs.get('shipping_no'),
                'no_change': bool(kwargs.get('no_change')),
                'partner_team_site_id': partner_team_site_id,
                'website_id': request.website.id
            }
            sale_order = request.env['sale.order'].sudo().create(values)
            return request.redirect('/sale/portal/fill_order?order_id=' + str(sale_order.id))

    @http.route('/user/detail/edit', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def user_detail_edit(self):
        user = request.env.user
        partner = user.partner_id
        if not partner.email and not partner.street or not partner.city or not partner.state_id or not partner.zip or not partner.phone or not partner.country_id:
            return '400'
        else:
            return '200'

    @http.route('/sale/portal/fill_order', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def sale_portal_fill_order(self, order_id=None, user_name=None, state=None, shipping_no=None, error_message=None,**kwargs):
       if request.env.user == request.env.ref('base.public_user'):
           redirect_url = '/sale/portal/fill_order?%s'%url_encode({'order_id':order_id,'shipping_no':shipping_no})
           return request.redirect('/web/login?redirect=%s'%redirect_url)
       sale_order = request.env['sale.order'].sudo().model_get_portal_order(force_id=order_id)
       values = {
           'order_id': sale_order.id,
           'state': state,
           'user_name': user_name or request.env.user.name,
           'shipping_no': sale_order.shipping_no or shipping_no or '',
           'lines': [{
               'product_sale_category_name':line.product_sale_category_id.name or '',
               'product_material_name':line.product_material_id.name or '',
               'product_brand_name':line.product_brand_id.name or '',
               'product_qty': line.product_uom_qty,
               'edit_url': '/sale/portal/fill_order_line?%s'%url_encode({'order_id':sale_order.id,'order_line_id':line.id}),
               'delete_url': '/sale/portal/delete_order_line?%s'%url_encode({'order_id':sale_order.id,'order_line_id':line.id}),
           } for line in sale_order.order_line],
           'error_message': error_message,
       }
       return request.render('zhaogu_sale.sale_portal_fill_order_template', values)


    @http.route('/sale/portal/fill_order_line', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def sale_portal_fill_order_line(self, order_id=None, order_line_id=None, shipping_no=None, **kwargs):
        sale_order = request.env['sale.order'].browse(int(order_id))
        if order_line_id:
            sale_order_line = sale_order.order_line.filtered(lambda l:l.id == int(order_line_id))
            product = sale_order_line.product_id
            sale_category_id, product_brand_id, product_material_id = product.sale_category_id.id,\
                                                        sale_order_line.brand_id.id, product.material_id.id
            qty = str(sale_order_line.product_uom_qty)
        else:
            sale_category_id, product_brand_id, product_material_id = kwargs.get('sale_category_id',''),\
                                    kwargs.get('product_brand_id', ''), kwargs.get('product_material_id','')
            qty = ''

        return request.render('zhaogu_sale.sale_portal_fill_order_line_template', {
            'order_id': sale_order.id,
            'order_line_id': order_line_id,
            'sale_categories': [(category.id, category.name) for category in request.env['product.sale.category'].search([])],
            'product_brands': [(material.id, material.name) for material in request.env['product.brand'].search([])],
            'product_materials':[(brand.id, brand.name) for brand in request.env['product.material'].search([])],
            'error_message': kwargs.get('error_message',''),
            'sale_category_id': sale_category_id,
            'product_brand_id': product_brand_id,
            'product_material_id': product_material_id,
            'qty': qty,
            'shipping_no': shipping_no,
        })

    @http.route('/sale/portal/delete', type='http', auth='public', methods=['GET'], csrf=False)
    def sale_portal_delete_order(self, order_id, **kwargs):
        sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        sale_order.sudo().unlink()
        return request.redirect('/sale/portal/orders?ytype=draft')


    @http.route('/sale/portal/save', type='http', auth='public', methods=['GET'], csrf=False)
    def sale_portal_save_order(self, order_id=None, user_name=None, shipping_no=None, lines=None, **kwargs):
        try:
            sale_order = request.env['sale.order'].sudo().model_get_portal_order(force_id=order_id)
            shipping_id = request.env['shipping.bill'].sudo().search([('name', '=', shipping_no)])
            if not shipping_no:
                return request.redirect('/sale/portal/fill_order?%s' % url_encode(
                    {'order_id': order_id, 'shipping_no': shipping_no, 'error_message': '运单号不能为空'}))
            if not sale_order.order_line:
                return request.redirect('/sale/portal/fill_order?%s' % url_encode(
                    {'order_id': order_id, 'shipping_no': shipping_no, 'error_message': '明细不能为空'}))
            sale_order.write({'shipping_no':shipping_no})
            if shipping_id:
                sale_order.write({
                    'fetch_no': shipping_id.picking_code,
                    'shipping_bill_id': shipping_id.id
                })
                shipping_id.sale_order_id = sale_order.id
                shipping_id.state = 'paired'
                if shipping_id.state == 'paired':
                    shipping_id.multi_action_compute()
        except Exception as e:
            return request.redirect('/sale/portal/fill_order?%s' % url_encode(
                {'order_id': order_id, 'error_message': str(e)}))
        else:
            return request.redirect('/')

    @http.route('/sale/portal/save_line', type='http', auth='public', methods=['GET'], csrf=False)
    def sale_portal_save_order_line(self, order_id, order_line_id, sale_category_id, product_other, product_brand_id, product_material_id,
                                    qty, shipping_no=None,**kwargs):
        sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        try:
            sale_order.portal_update_line(sale_category_id, product_brand_id, product_material_id, qty, order_line_id, product_other)
        except UserError as e:
            params = {
                'order_id':order_id, 'error_message':str(e), 'order_line_id':order_line_id,
                'sale_category_id':sale_category_id, 'product_brand_id':product_brand_id,
                'product_material_id': product_material_id, 'qty':qty, 'shipping_no':shipping_no,
            }
            return request.redirect(f'/sale/portal/fill_order_line?%s'%url_encode(params))
        return request.redirect(f'/sale/portal/fill_order?%s'%url_encode({
            'order_id':order_id, 'shipping_no': sale_order.shipping_no or shipping_no}))


    @http.route('/sale/portal/orders', type='http', auth='public',website=True)
    def sale_portal_orders(self, ytype, **kwargs):
        partner = request.env.user.partner_id.id
        if request.env.user == request.env.ref('base.public_user'):
            redirect_url = '/sale/portal/orders'
            return request.redirect('/web/login?redirect=%s'%redirect_url)
        if ytype == 'draft':
            sale_orders = request.env['sale.order'].sudo().search([('partner_id', '=', partner), ('state', '=', 'draft'), ('shipping_bill_id', '=' , False)])
        elif ytype == 'valuedno':
            sale_orders = request.env['sale.order'].sudo().search([('shipping_bill_state', '=', 'valued'),
                                                                   ('partner_id', '=', partner)]).filtered(lambda l:l.shipping_bill_id.sale_invoice_payment_state == '支付未完成')
        elif ytype == 'valued':
            sale_orders = request.env['sale.order'].sudo().search(
                [('shipping_bill_state', '=', 'valued'), ('partner_id', '=', partner)]).filtered(
                lambda l: l.shipping_bill_id.sale_invoice_payment_state == '支付已完成')
        elif ytype == 'arrived':
            sale_orders = request.env['sale.order'].sudo().search(
                [('shipping_bill_state', 'in', ['arrived', 'transported']), ('partner_id', '=', partner)])
        else:
            return request.redirect(request.httprequest.referrer)


        values = {'sale_orders':sale_orders}
        return request.render('zhaogu_sale.sale_portal_orders_template', values)

class CustomerPortal2(CustomerPortal):

    @http.route()
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        user = request.env.user
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                user.sudo().write({
                    'email': post['email'],
                    'login': post['email']
                })
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response



