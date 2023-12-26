# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime


class ShippingLargeParcelVvipConfirmWizard(models.TransientModel):
    _name = 'shipping.large.parcel.vvip.confirm.wizard'

    shipping_large_id = fields.Many2one('shipping.large.parcel', string="大包裹")

    def _compute_data(selfs):
        for self in selfs:
            data = ''
            vvip_shipping = self.shipping_large_id.shipping_bill_ids.filtered(lambda l: l.sale_partner_id.partner_vip_type == 'vvip')
            _term_lambda = lambda s: (s.sale_partner_id.id)
            for term in set(vvip_shipping.mapped(_term_lambda)):
                this_shipping_bills = vvip_shipping.filtered(lambda s: _term_lambda(s) == term)
                partner_name = this_shipping_bills[0].sale_partner_id.name
                invoice_price = sum(this_shipping_bills.sale_invoice_ids.filtered(lambda l: l.state != 'cancel').mapped('amount_total'))
                partner_wallt_price = this_shipping_bills[0].sale_partner_id.wallet_balance
                balance_price = partner_wallt_price - invoice_price
                data += '客户: %s, 余额: %s, 扣款: %s, 扣款后余额: %s \n' % (partner_name, '%.2f' % partner_wallt_price, '%.2f' % invoice_price, '%.2f' % balance_price)
            self.data = data or "无vvip用户"
    data = fields.Text('vvip结构',compute="_compute_data", readonly=True)

    def apply(self):
        self.shipping_large_id.resend_email(confirm_true=True)
        return True
