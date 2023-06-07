# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # 遗弃购物车
    def shopping_cart_sms(self, number):
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
