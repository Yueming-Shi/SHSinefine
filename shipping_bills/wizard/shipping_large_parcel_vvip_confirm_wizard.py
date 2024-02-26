# -*- coding: utf-8 -*-

import logging
import math

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime


class ShippingLargeParcelVvipConfirmWizard(models.TransientModel):
    _name = 'shipping.large.parcel.vvip.confirm.wizard'

    shipping_large_id = fields.Many2one('shipping.large.parcel', string="大包裹")

    @api.depends('shipping_large_id')
    def _compute_data(selfs):
        for self in selfs:
            data = ''
            vvip_shipping = self.shipping_large_id.shipping_bill_ids.filtered(lambda l: l.sale_partner_id.partner_vip_type == 'svip')
            _term_lambda = lambda s: (s.sale_partner_id.id)
            for term in set(vvip_shipping.mapped(_term_lambda)):
                this_shipping_bills = vvip_shipping.filtered(lambda s: _term_lambda(s) == term)
                raise UserError(this_shipping_bills)
                fee_total = self._compute_vvip_factor(this_shipping_bills)
                partner_name = this_shipping_bills[0].sale_partner_id.name
                partner_wallt_price = this_shipping_bills[0].sale_partner_id.wallet_balance
                balance_price = partner_wallt_price - fee_total
                data += '客户: %s, 余额: %s, 扣款: %s, 扣款后余额: %s \n' % (partner_name, '%.2f' % partner_wallt_price, '%.2f' % fee_total, '%.2f' % balance_price)
            self.data = data or "无VVIP用户"
    data = fields.Text('VVIP用户',compute="_compute_data", readonly=True)

    def apply(self):
        self.shipping_large_id.resend_email(confirm_true=True)
        return True

    # vvip计算各个包裹价格
    def _compute_vvip_factor(self, merge_shippings):
        _term_lambda = lambda s: (s.shipping_factor_id.id)
        fee_total = 0
        for term in set(merge_shippings.mapped(_term_lambda)):
            this_shipping_bills = merge_shippings.filtered(lambda s: _term_lambda(s) == term)
            shipping_factor = this_shipping_bills[0].shipping_factor_id

            volume = 0
            for shipping1 in this_shipping_bills:
                volume += shipping1.length * shipping1.width * shipping1.height

            if (sum(this_shipping_bills.mapped('volume_weight')) / sum(
                    this_shipping_bills.mapped('actual_weight'))) < shipping_factor.double_difference:
                size_weight = sum(this_shipping_bills.mapped('actual_weight'))
                first_weight = shipping_factor.vip_first_weight
                first_total_price = shipping_factor.vip_first_total_price
                next_price_unit = shipping_factor.vip_next_price_unit
                next_weight_to_ceil = shipping_factor.vip_next_weight_to_ceil
            else:
                size_weight = max([sum(this_shipping_bills.mapped('actual_weight')), volume / shipping_factor.factor])
                first_weight = shipping_factor.first_weight
                first_total_price = shipping_factor.first_total_price
                next_price_unit = shipping_factor.next_price_unit
                next_weight_to_ceil = shipping_factor.next_weight_to_ceil

            weight = math.ceil(
                size_weight * 1000 / next_weight_to_ceil) * next_weight_to_ceil

            if weight < first_weight:
                fee = first_total_price
            else:
                fee = first_total_price + (
                        weight - first_weight) / next_weight_to_ceil * next_price_unit
            fee_total += fee
        return fee_total

