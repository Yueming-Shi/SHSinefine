# See LICENSE file for full copyright and licensing details.
import requests
import json

from odoo import api
from odoo import models
from odoo.exceptions import UserError

odoo_session = requests.Session()


class ShippingBill(models.Model):
    _inherit = 'shipping.bill'

    def write(selfs, vals):
        result = super().write(vals)
        for self in selfs:
            invoice_id = self.sale_invoice_ids.filtered(lambda l: l.payment_state not in ['paid', 'reversed', 'invoicing_legacy'] and l.state != 'cancel')
            point_price = -sum(invoice_id.invoice_line_ids.filtered(lambda l: 'Wallet' in l.name).mapped('price_subtotal'))
            fee = sum(invoice_id.mapped('amount_total')) + (point_price or 0)
            openid = self.sale_partner_id.user_ids.wx_openid
            # 获取token
            token = self.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
            data = {}
            if openid:
                if vals.get('state') == 'returned':
                    data = {
                        "touser": openid,
                        "template_id": "3yfETXzY9V-3xPLWlxOGc7ItkNWPLCyusqKaLQkQgDI",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "尊敬的客户" + ' ' + self.sale_partner_id.name + ',' + '您的包裹已退运。',
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": self.name,
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.shipping_factor_id.name,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": "订单已退运",
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "退运快递单号：" + self.name,
                                "color": "#173177"
                            },
                        },
                    }
                    self.wx_information_send(token, data)
                elif vals.get('state') == 'transported':
                    if self.picking_code:
                        code = self.picking_code
                    else:
                        code = ''
                    data = {
                        "touser": openid,
                        "template_id": "fKRko5U-JjPalqSmtG6nlTeuezIpTAD41hGM7JX3NQw",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "您的包裹已发出:",
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": self.name,
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.logistics,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": self.tracking_no,
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "取件码[%s]" % self.picking_code,
                                "color": "#173177"
                            },
                        },
                    }
                    self.wx_information_send(token, data)
                elif vals.get('state') == 'arrived':
                    data = {
                        "touser": openid,
                        "template_id": "9_5NzQ0d9DVm-Cn75NaSTAgLviYftpaBRCCbS70ZhfI-jC3nFNnuVXK4A4",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "您的包裹已到站:",
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": "空运包裹",
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.tracking_no,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": "请及时到站领取您的包裹",
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "取件码[%s]" % self.picking_code,
                                "color": "#173177"
                            },
                        },
                    }
                    self.wx_information_send(token, data)
                elif vals.get('state') == 'signed':
                    data = {
                        "touser": openid,
                        "template_id": "0mHcAQerXuBjqJsV5ZydUTY3QfURh9m8gXojKFklGkk-jC3nFNnuVXK4A4",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "您的包裹已成功签收:",
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": "空运包裹",
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.tracking_no,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": self.signed_date,
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "感谢您的使用。期待您下次使用。",
                                "color": "#173177"
                            },
                        },
                    }
                    self.wx_information_send(token, data)
        return result

    def multi_action_compute(selfs):
        result = super().multi_action_compute()
        for self in selfs:
            invoice_id = self.sale_invoice_ids.filtered(
                lambda l: l.payment_state not in ['paid', 'reversed', 'invoicing_legacy'] and l.state != 'cancel')
            point_price = -sum(
                invoice_id.invoice_line_ids.filtered(lambda l: 'Wallet' in l.name).mapped('price_subtotal'))
            fee = sum(invoice_id.mapped('amount_total')) + (point_price or 0)
            openid = self.sale_partner_id.user_ids.wx_openid
            if openid:
                # 获取token
                token = selfs.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
                data = {
                    "touser": openid,
                    "template_id": "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
                    "url": "https://trans.sinefine.store/order/trans/unpaid",
                    "miniprogram": {},
                    "client_msg_id": "",
                    "data": {
                        "first": {
                            "value": "您的订单已到仓:",
                            "color": "#173177"
                        },
                        "orderno": {
                            "value": self.name,
                            "color": "#173177"
                        },
                        "amount": {
                            "value": "%s%s" % (self.currency_id.symbol, '{0:,.2f}'.format(fee)),
                            "color": "#173177"
                        },
                        "remark": {
                            "value": "取件码[%s]" % self.picking_code,
                            "color": "#173177"
                        },
                    },
                }
                self.wx_information_send(token, data)
        return result

    def multi_action_change(selfs):
        result = super().multi_action_change()
        for self in selfs:
            invoice_id = self.sale_invoice_ids.filtered(
                lambda l: l.payment_state not in ['paid', 'reversed', 'invoicing_legacy'] and l.state != 'cancel')
            point_price = -sum(
                invoice_id.invoice_line_ids.filtered(lambda l: 'Wallet' in l.name).mapped('price_subtotal'))
            fee = sum(invoice_id.mapped('amount_total')) + (point_price or 0)
            openid = self.sale_partner_id.user_ids.wx_openid
            if openid:
                # 获取token
                token = selfs.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
                data = {
                    "touser": openid,
                    "template_id": "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
                    "url": "",
                    "miniprogram": {},
                    "client_msg_id": "",
                    "data": {
                        "first": {
                            "value": "您的订单已改泡:",
                            "color": "#173177"
                        },
                        "orderno": {
                            "value": self.name,
                            "color": "#173177"
                        },
                        "amount": {
                            "value": "%s%s" % (self.currency_id.symbol, '{0:,.2f}'.format(fee)),
                            "color": "#173177"
                        },
                        "remark": {
                            "value": "取件码[%s]" % self.picking_code,
                            "color": "#173177"
                        },
                    },
                }
                self.wx_information_send(token, data)
        return result

    def wx_information_send(self, token, data):
        send_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % token

        headers = {
            'Content-Type': 'application/json'
        }
        data_json = json.dumps(data)

        res = odoo_session.post(url=send_url, data=bytes(data_json, 'utf-8'), headers=headers)

        return True
