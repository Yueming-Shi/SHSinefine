# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ShippingBill(models.Model):
    _inherit = 'shipping.bill'

    # 未付款订单
    def shipping_bill_unpaid_sms(self, number):
        contact = 'test' \
                  'test' \
                  'test' \
                  'test'
        send_sms = self.env['sms.sms'].sudo().create({
            'number': number,
            'partner_id': False,
            'body': contact,
        })
        send_sms.send()

    # 大包裹运单
    def shipping_large_parcel_sms(self, number):
        contact = 'test' \
                  'test' \
                  'test' \
                  'test'
        send_sms = self.env['sms.sms'].sudo().create({
            'number': number,
            'partner_id': False,
            'body': contact,
        })
        send_sms.send()

