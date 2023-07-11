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
                    tmpl_id = "3yfETXzY9V-3xPLWlxOGc7ItkNWPLCyusqKaLQkQgDI"
                    tmpl_data = {
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
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)
                elif vals.get('state') == 'transported':
                    tmpl_id = "fKRko5U-JjPalqSmtG6nlTeuezIpTAD41hGM7JX3NQw"
                    tmpl_data = {
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
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                    # 发送短信
                    msg = 'Package [%s] has been dispatched. ' \
                          'For queries, contact our customer service.' % self.tracking_no
                    self.send_message_post(msg)
                elif vals.get('state') == 'arrived':
                    tmpl_id = "9_5NzQ0d9DVm-Cn75NaSTAgLviYftpaBRCCbS70ZhfI-jC3nFNnuVXK4A4"
                    tmpl_data = {
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
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                    # 发送短信
                    msg = 'Your package [%s] is ready for pick-up at [%s].' \
                          'Your Pick-up Code is [Pick-Up Code]. For assistance,' \
                          'contact our customer service. [%s]' % (
                          self.tracking_no, self.sale_site_id.name, self.sale_partner_id.company_id.name)
                    self.send_message_post(msg)
                elif vals.get('state') == 'signed':
                    tmpl_id = "0mHcAQerXuBjqJsV5ZydUTY3QfURh9m8gXojKFklGkk-jC3nFNnuVXK4A4"
                    tmpl_data = {
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
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                    # 发送短信
                    msg = 'Successful delivery for package [%s]. It has been signed for. ' \
                          'For any feedback or assistance, reach out to our customer service. [%s]'  % (
                          self.tracking_no, self.sale_partner_id.company_id.name)
                    self.send_message_post(msg)
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
                tmpl_id = "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
                tmpl_data = {
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
                }
                self.wx_information_send(token, openid, tmpl_data, tmpl_id)
                # 发送短信
                msg = 'Package [%s] has arrived at warehouse. Shipment Cost is [%s].' \
                      'Please make payment via your registered account.' \
                      'For queries, contact our customer service. [%s]' % (self.tracking_no, fee, self.sale_partner_id.company_id.name)
                self.send_message_post(msg)

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
                tmpl_id = "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
                tmpl_data = {
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
                }
                self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                # 发送短信
                msg = 'Package [%s] has been repackaged. New shipment cost is [%s].' \
                      'Please adjust your payment. For any concerns, ' \
                      'contact our customer service. [%s]' % (self.tracking_no, fee, self.sale_partner_id.company_id.name)
                self.send_message_post(msg)
        return result

    def wx_information_send(self, token, openid, tmpl_data, tmpl_id):
        data = {
            "touser": openid,
            "template_id": tmpl_id,
            "url": "",
            "miniprogram": {},
            "client_msg_id": "",
            "data": tmpl_data
        }

        send_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % token

        headers = {
            'Content-Type': 'application/json'
        }
        data_json = json.dumps(data)

        res = odoo_session.post(url=send_url, data=bytes(data_json, 'utf-8'), headers=headers)

        return True

    def send_message_post(self, msg):
        send_sms = self.env['sms.sms'].sudo().create({
            'number': self.sale_partner_id.phone,
            'partner_id': self.sale_partner_id.id,
            'body': msg,
        })
        send_sms.send()

