# -*- coding: utf-8 -*-
import logging
import pprint
import requests
import qrcode
from io import BytesIO
import base64
import json

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

_logger = logging.getLogger(__name__)


class IoTPayController(http.Controller):
    _return_url = '/payment/iotpay/return'
    _notify_url = '/payment/iotpay/notify'

    @http.route(_return_url, type='http', auth="public", methods=['GET'])
    def iotpay_return_from_redirect(self, **data):
        """ IoTPay return """
        _logger.info("received IoTPay return data:\n%s", pprint.pformat(data))
        #request.env['payment.transaction'].sudo()._handle_feedback_data('iotpay', data)
        return request.redirect('/payment/status')

    @http.route(_notify_url, type='http', auth='public', methods=['POST'], csrf=False)
    def iotpay_notify(self, **post):
        """ IoTPay Notify """
        _logger.info("received IoTPay notification data:\n%s", pprint.pformat(post))
        tx = request.env['payment.transaction'].sudo()._handle_feedback_data('iotpay', post)

        # 判断是否为充值钱包
        if tx.state == 'done':
            self.payment_validate_point(tx.id, sale_order_id=None)
        return 'success'  # Return 'success' to stop receiving notifications for this tx

    @http.route('/payment/iotpay/qrcode', type='http', auth="public", website=True, methods=['GET'])
    def iotpay_qrcode_pay(self, order, qrurl, amount):
        """ User scan qrcode to pay """
        def make_qrcode(url):
            img = qrcode.make(url)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            heximage = base64.b64encode(buffer.getvalue())
            return "data:image/png;base64,{}".format(heximage.decode('utf-8'))

        values = {}
        values['qrcode'] = make_qrcode(qrurl)
        values['order'] = order
        values['amount'] = amount
        return request.render("payment_iotpay.iotpay_qrcode", values)

    @http.route('/payment/iotpay/result', type='http', auth="public", website=True)
    def iotpay_query(self, order):
        """query payment result from page"""
        tx = request.env['payment.transaction'].sudo().search([('reference', '=', order), ('provider', '=', 'iotpay')])
        if tx and tx.state == 'done':
            # 支付成功
            return json.dumps({"result": 0, "order": order})
        return json.dumps({"result": 1, "order": order})


    def payment_validate_point(self, transaction_id=None, sale_order_id=None):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)

        product = request.website.wallet_product_id

        # if payment.acquirer is credit payment provider
        for line in order.order_line:
            if product and line.product_id.id == product.id:
                wallet_transaction_obj = request.env['website.wallet.transaction']
                if tx.acquirer_id.need_approval:
                    wallet_create = wallet_transaction_obj.sudo().create({
                        'wallet_type': 'credit',
                        'partner_id': order.partner_id.id,
                        'sale_order_id': order.id,
                        'reference': 'sale_order',
                        'amount': order.order_line.price_unit * order.order_line.product_uom_qty,
                        'currency_id': order.pricelist_id.currency_id.id,
                        'status': 'draft'
                    })
                else:
                    wallet_create = wallet_transaction_obj.sudo().create({
                        'wallet_type': 'credit',
                        'partner_id': order.partner_id.id,
                        'sale_order_id': order.id,
                        'reference': 'sale_order',
                        'amount': order.order_line.price_unit * order.order_line.product_uom_qty,
                        'currency_id': order.pricelist_id.currency_id.id,
                        'status': 'done'
                    })
                    wallet_create.wallet_transaction_email_send()  # Mail Send to Customer
                    order.partner_id.update({
                        'wallet_balance': order.partner_id.wallet_balance + order.order_line.price_unit * order.order_line.product_uom_qty})
                order.with_context(send_email=True).action_confirm()
                request.website.sale_reset()
                # 任意充值即为vip
                if order.partner_id.partner_vip_type not in ['svip', 'vip']:
                    order.partner_id.partner_vip_type = 'vip'

        return True
