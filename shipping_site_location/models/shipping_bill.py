# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ShippingBill(models.Model):
    _inherit = 'shipping.bill'

    # 仓库位置
    site_location_id = fields.Many2one('site.location', string="仓库位置", compute="_compute_site_location")
    remark = fields.Char('备注')
    is_no_header = fields.Boolean('无头件')
    return_cost = fields.Float('退运成本')
    return_note = fields.Char('退运备注')
    partner_vip_number = fields.Char('VVIP号码', related='sale_partner_id.partner_vip_number')
    partner_vip_type = fields.Selection(related='sale_partner_id.partner_vip_type')

    def _inverse_frontend_trigger(selfs):
        for self in selfs.filtered(lambda s: s.frontend_trigger):
            getattr(self, self.frontend_trigger)()
            # frontend_trigger_arr = self.frontend_trigger.split(',')
            # getattr(self, frontend_trigger_arr[0])()
            # self.state = 'paired'
            # if self.state == 'paired':
            #     getattr(self, frontend_trigger_arr[1])()
            self.write({'frontend_trigger': False})

    frontend_trigger = fields.Char(inverse='_inverse_frontend_trigger')

    @api.model_create_multi
    def create(self,val_list):
        res = super(ShippingBill, self).create(val_list)
        if res.site_location_id.name == '无头位置':
            res.is_no_header = True
        return res

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            sale_order = self.env['sale.order'].search(
                [('shipping_no', 'ilike', self.name), ('shipping_bill_id', '=', False)], limit=1)
            if sale_order:
                self.update({
                    'sale_order_id': sale_order.id,
                    'no_change': sale_order.no_change,
                    'frontend_trigger': 'multi_action_match',
                })
            else:
                self.update({
                    'sale_order_id': False,
                    'no_change': False,
                    'frontend_trigger': 'multi_action_match',
                })

    def _compute_site_location(selfs):
        for self in selfs:
            if self.sale_order_id and self.sale_order_id.partner_team_site_id:
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

    def multi_action_match(selfs):
        res = super(ShippingBill, selfs).multi_action_match()
        for self in selfs:
            if self.partner_vip_type == 'svip':
                invoice_id = self.sale_invoice_ids.filtered(
                    lambda l: l.payment_state not in ['paid', 'reversed', 'invoicing_legacy'] and l.state != 'cancel')
                point_price = -sum(
                    invoice_id.invoice_line_ids.filtered(lambda l: 'Wallet' in l.name).mapped('price_subtotal'))
                fee = sum(invoice_id.mapped('amount_total')) + (point_price or 0)
                openid = self.sale_partner_id.user_ids.wx_openid
                if openid:
                    # 获取token
                    token = selfs.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
                    tmpl_id = "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA"
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
                self.env.ref('shipping_bills.mail_template_data_shipping_bill_to_warehouse').send_mail(self.id,
                                                                                                       force_send=True)

                # 发送短信
                if self.sale_partner_id.phone:
                    msg = 'Package [%s] has arrived at warehouse. Shipment Cost is [%s %s].' \
                          'Please make payment via your registered account.' \
                          'For queries, contact our customer service.     Sinefine' % (
                          self.tracking_no, self.currency_id.name, fee)
                    self.send_message_post(msg)
        return res
