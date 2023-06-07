# See LICENSE file for full copyright and licensing details.
import requests
import json

from odoo import api
from odoo import models
from odoo.exceptions import UserError

odoo_session = requests.Session()


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(selfs, vals):
        for self in selfs:
            old_amount_total = self.amount_total
            res = super().write(vals)
            if old_amount_total != self.amount_total:
                openid = self.partner_id.user_ids.wx_openid
                # 获取token
                token = self.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
                if openid:
                    sale_id = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
                    if sale_id and sale_id[0].shipping_bill_id:
                        shipping_order = sale_id[0].shipping_bill_id
                        data = {
                            "touser": openid,
                            "template_id": "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
                            "url": "https://trans.sinefine.store/order/trans/unpaid",
                            "miniprogram": {},
                            "client_msg_id": "",
                            "data": {
                                "first": {
                                    "value": "您好，您的包裹已完成改泡，请点击信息付款。",
                                    "color": "#173177"
                                },
                                "orderno": {
                                    "value": shipping_order.name,
                                    "color": "#173177"
                                },
                                "amount": {
                                    "value": '{0:,.2f}'.format(shipping_order.sale_invoice_ids[0].amount_total),
                                    "color": "#173177"
                                },
                                "remark": {
                                    "value": "请在72小时内完成支付，否则订单将被取消。",
                                    "color": "#173177"
                                },
                            },
                        }
                        self.env['shipping.bill'].sudo().wx_information_send(token, data)
            return res
