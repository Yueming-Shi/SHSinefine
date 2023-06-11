# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

import logging

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.urls import url_join, url_encode

_logger = logging.getLogger(__name__)


class PointPayment(http.Controller):

    @http.route('/shpping/point/payment', type='http', auth='public', methods=['post'], website=True)
    def point_payment_methods(self, **post):
        partner = request.env.user.partner_id

        invoice_id = post['invoice_id']
        invoice_order = request.env['account.move'].sudo().browse(int(invoice_id))

        all_shipping_bill = request.env['shipping.bill'].sudo().search([('sale_partner_id', '=', partner.id)])
        shipping_order = all_shipping_bill.filtered(lambda l: invoice_order.id in l.sale_invoice_ids.ids)

        point_balance = partner.wallet_balance
        if shipping_order:
            shipping_sale = shipping_order.sudo().sale_order_id
            if point_balance > invoice_order.amount_total:
                wallet_id = request.env['website.wallet.transaction'].sudo().create({
                    'wallet_type': 'debit',
                    'partner_id': partner.id,
                    'sale_order_id': shipping_sale.id,
                    'reference': 'sale_order',
                    'amount': invoice_order.amount_total,
                    'currency_id': shipping_order.currency_id.id,
                    'status': 'done'
                })

                shipping_sale.sudo().write({
                    'wallet_used': shipping_sale.amount_total,
                    'wallet_transaction_id': wallet_id.id
                })

                invoice_order.sudo().update({
                    'wallet_added': True,
                    'invoice_line_ids': [(0, 0, {
                            'name': 'Wallet Used' + ' ' + str(invoice_order.amount_total),
                            'analytic_account_id': shipping_sale.analytic_account_id.id or False,
                            'price_unit': -shipping_sale.wallet_used,
                            'price_subtotal' : -shipping_sale.wallet_used,
                            'quantity': 1,
                            'discount': 0,
                        })],
                })

        return request.redirect(invoice_order.get_portal_url())



