# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # 新品上市
    def new_product_launch_sms(self, number):
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
