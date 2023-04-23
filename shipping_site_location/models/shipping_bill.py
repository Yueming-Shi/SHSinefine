# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ShippingBill(models.Model):
    _inherit = 'shipping.bill'

    # 仓库位置
    site_location_id = fields.Many2one('site.location', string="仓库位置", compute="_compute_site_location")
    remark = fields.Char('备注')

    def _inverse_frontend_trigger(selfs):
        for self in selfs.filtered(lambda s: s.frontend_trigger):
            frontend_trigger_arr = self.frontend_trigger.split(',')
            getattr(self, frontend_trigger_arr[0])()
            self.state = 'paired'
            if self.state == 'paired':
                getattr(self, frontend_trigger_arr[1])()
            self.write({'frontend_trigger': False})

    frontend_trigger = fields.Char(inverse='_inverse_frontend_trigger')

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            sale_order = self.env['sale.order'].search(
                [('shipping_no', 'ilike', self.name), ('shipping_bill_id', '=', False)], limit=1)
            if sale_order:
                self.update({
                    'sale_order_id': sale_order.id,
                    'no_change': sale_order.no_change,
                    'frontend_trigger': 'multi_action_match,multi_action_compute',
                })
            else:
                self.update({
                    'sale_order_id': False,
                    'no_change': False,
                    'frontend_trigger': 'multi_action_match,multi_action_compute',
                })

    def _compute_site_location(selfs):
        for self in selfs:
            if self.sale_order_id:
                if self.shipping_factor_id and self.sale_site_id:
                    site_location_id = self.env['site.location'].search([
                        ('factor_id', '=', self.shipping_factor_id.id),
                        ('site_partner_id', '=', self.sale_site_id.id)
                    ])
                    self.site_location_id = site_location_id.id
            else:
                self.site_location_id = 1

    # 获取需要创建大包裹的运单，根据重量比对创建大包裹
    def get_shipping_bill_unpacked(self):
        shipping_bills = self.env['shipping.bill'].search([('state', '=', 'valued'),
                                                           ('sale_invoice_payment_state', '=', '支付已完成'),
                                                           ('large_parcel_ids', '=', False)])
        _term_lambda = lambda s: (s.sale_site_id.id, s.shipping_factor_id.id)

        for term in set(shipping_bills.mapped(_term_lambda)):
            this_shipping_bills = shipping_bills.filtered(lambda s: _term_lambda(s) == term)
            current_real_weight = sum(this_shipping_bills.mapped('actual_weight'))
            real_weight_id = self.env['site.location'].search(
                [('site_partner_id', '=', term[0]), ('factor_id', '=', term[1])])

            if not this_shipping_bills:
                continue

            if real_weight_id and current_real_weight > real_weight_id.real_weight:
                large_parcel = self.env['shipping.large.parcel'].create({
                    'name': self.env['ir.sequence'].next_by_code('shipping.large.parcel'),
                    'site_id': term[0],
                    'shipping_bill_ids': [(6, 0, this_shipping_bills.ids)]
                })

    # 判断是否存在超过包裹存放天数的包裹，并标记可丢弃
    def model_judgment_package_day(selfs):
        for self in selfs.search([('state', '=', 'draft'), ('sale_order_id', '=', False)]):
            if self.site_location_id and self.site_location_id.name == '无头位置':
                if self.in_days > self.site_location_id.package_discard_day:
                    self.disposable = True
