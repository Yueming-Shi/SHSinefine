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
            openid = self.sale_partner_id.user_ids.wx_openid
            # 获取token
            token = self.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
            if vals.get('state') == 'transported':
                if openid:
                    tmpl_id = "fKRko5U-JjPalqSmtG6nlTeuezIpTAD41hGM7JX3NQw"
                    tmpl_data = {
                        "first": {
                            "value": "您的包裹已发出:",
                            "color": "#173177"
                        },
                        "keyword1": {
                            "value": self.name or "",
                            "color": "#173177"
                        },
                        "keyword2": {
                            "value": self.logistics or "",
                            "color": "#173177"
                        },
                        "keyword3": {
                            "value": self.tracking_no or "",
                            "color": "#173177"
                        },
                        "remark": {
                            "value": "取件码[%s]" % self.picking_code or "",
                            "color": "#173177"
                        },
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                # 发送邮件
                self.env.ref('shipping_bills.mail_template_data_shipping_bill_issue').send_mail(self.id)

                # 发送短信
                if self.sale_partner_id.phone:
                    msg = 'Package [%s] has been dispatched. ' \
                          'For queries, contact our customer service.    Sinefine' % self.tracking_no
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
            if not self.has_changed:
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
                            "value": self.name or "",
                            "color": "#173177"
                        },
                        "amount": {
                            "value": str('{0:,.2f}'.format(fee)),
                            "color": "#173177"
                        },
                        "remark": {
                            "value": "取件码[%s]" % self.picking_code or "",
                            "color": "#173177"
                        },
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                # 发送邮件
                self.env.ref('shipping_bills.mail_template_data_shipping_bill_to_warehouse').send_mail(self.id)

                # 发送短信
                if self.sale_partner_id.phone:
                    msg = 'Package [%s] has arrived at warehouse. Shipment Cost is [%s].' \
                          'Please make payment via your registered account.' \
                          'For queries, contact our customer service.     Sinefine' % (self.tracking_no, fee)
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
            if self.has_changed:
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
                                "value": self.name or "",
                                "color": "#173177"
                            },
                            "amount": {
                                "value": str('{0:,.2f}'.format(fee)),
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "取件码[%s]" % self.picking_code or "",
                                "color": "#173177"
                            },
                    }
                    self.wx_information_send(token, openid, tmpl_data, tmpl_id)

                # 发送邮件
                self.env.ref('shipping_bills.mail_template_data_shipping_bill_modified_foam').send_mail(self.id)

                # 发送短信
                if self.sale_partner_id.phone:
                    msg = 'Package [%s] has been repackaged. New shipment cost is [%s].' \
                          'Please adjust your payment. For any concerns, ' \
                          'contact our customer service.     Sinefine' % (self.tracking_no, fee)
                    self.send_message_post(msg)
        return result

