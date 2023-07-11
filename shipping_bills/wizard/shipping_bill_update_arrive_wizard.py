# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateArriveWizard(models.TransientModel):
    _name = 'shipping.bill.update.arrive.wizard'

    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            input = data.strip()
            shipping_bill = self.env['shipping.bill'].search([('name','=',input),('state','=','transported')],limit=1)
            if not shipping_bill:
                shipping_bill = self.env['shipping.bill'].search([('sale_fetch_no', '=', input),
                                                                  ('state', '=', 'transported')],limit=1)
            if not shipping_bill:
                raise UserError(f'未找到 {input} 的单据')
            shipping_bill.write({
                'arrived_date': _today,
                'state': 'arrived',
            })

            # 发送微信消息
            openid = shipping_bill.sale_partner_id.user_ids.wx_openid
            if openid:
                # 获取token
                token = shipping_bill.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
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
                        "value": shipping_bill.tracking_no,
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": "请及时到站领取您的包裹",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "取件码[%s]" % shipping_bill.picking_code,
                        "color": "#173177"
                    },
                }
                shipping_bill.wx_information_send(token, openid, tmpl_data, tmpl_id)
            # 发送短信
            if shipping_bill.sale_partner_id.phone:
                msg = 'Your package [%s] is ready for pick-up at [%s].' \
                      'Your Pick-up Code is [Pick-Up Code]. For assistance,' \
                      'contact our customer service. [%s]' % (
                          shipping_bill.tracking_no, shipping_bill.sale_site_id.name, shipping_bill.sale_partner_id.company_id.name)
                shipping_bill.send_message_post(msg)
