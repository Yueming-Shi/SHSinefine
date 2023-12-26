# See LICENSE file for full copyright and licensing details.
from datetime import datetime
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError


class ShippingLargeParcel(models.Model):
    _name = 'shipping.large.parcel'
    _description = "大包裹"
    _rec_name = 'name'

    name = fields.Char('包裹号', readonly=True, default='草稿')
    logistics_provider = fields.Char('物流商')
    logistics_tracking_code = fields.Char('物流追踪码')
    delivery_time = fields.Datetime('出库时间')
    length = fields.Float('长(CM)')
    width = fields.Float('宽(CM)')
    height = fields.Float('高(CM)')
    volume = fields.Float('体积(m³)')
    sender_contact = fields.Many2one('res.partner', '发件人')
    address_contact = fields.Many2one('res.partner', '收件人')
    shipping_bill_ids = fields.Many2many(
        'shipping.bill', 'shipping_bill_large_parcel_rel', 'large_parcel_id', 'shipping_bill_id', '客户运单',
        copy=False)

    site_id = fields.Many2one('res.partner', '站点')
    is_sent = fields.Boolean()

    weight = fields.Float('重量')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ShippingLargeParcel, self).create(vals_list)
        res.name = res.env['ir.sequence'].next_by_code('shipping.large.parcel')
        return res

    def resend_email(selfs, confirm_true=False):
        for self in selfs:
            vvip_shippings = self.shipping_bill_ids.filtered(lambda l: l.sale_partner_id.partner_vip_type == 'svip')
            if vvip_shippings and not confirm_true:
                return {
                    'name': 'VVIP客户确认扣款',
                    'view_mode': 'form',
                    'res_model': 'shipping.large.parcel.vvip.confirm.wizard',
                    'view_id': self.env.ref('shipping_bills.shipping_large_parcel_vvip_confirm_wizard_form').id,
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_shipping_large_id': self.id,
                    },
                    'target': 'new',
                }
            else:
                _term_lambda = lambda s: (s.sale_partner_id.id)
                for term in set(self.shipping_bill_ids.mapped(_term_lambda)):
                    this_shipping_bills = self.shipping_bill_ids.filtered(lambda s: _term_lambda(s) == term)
                    # vvip自动扣款
                    self.vvip_wallet_payment(this_shipping_bills)
                    # 包裹发出给客户发送邮件
                    self.send_parcel_sent_email(this_shipping_bills)

                if not self.delivery_time:
                    self.delivery_time = datetime.now()
                for shipping_bill in self.shipping_bill_ids:
                    shipping_bill.sudo().update({
                        'logistics': self.logistics_provider,
                        'tracking_no': self.logistics_tracking_code,
                        'state': 'transported',
                        'out_date': self.delivery_time
                    })

                # 给站点发送邮件
                template = self.env.ref('shipping_bills.mail_template_shipping_large_parcel')
                template.sudo().send_mail(self.id, raise_exception=True, force_send=True)
                self.is_sent = True

    # 包裹发出通知客户
    def send_parcel_sent_email(self, shippings):
        openid = shippings[0].sale_partner_id.user_ids.wx_openid
        # 获取token
        token = self.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
        item_dict = {}
        vals = ''
        for shipping in shippings:
            sale_order = shipping.sale_order_id.sudo()
            sale_product_names = sale_order.order_line.sudo().filtered(
                lambda l: l.product_sale_category_id and l.product_material_id).mapped('product_sale_category_id').mapped('name')
            vals += "%s（%s）\n" % (shipping.picking_code, ','.join(sale_product_names or ""))

        item_dict['picking_code'] = ','.join(shippings.mapped('picking_code') or " ")
        item_dict['logistics'] = ','.join(shippings.mapped('logistics') or " ")
        item_dict['tracking_no'] = ','.join(shippings.mapped('tracking_no') or " ")
        item_dict['name'] = ','.join(shippings.mapped('name') or " ")
        item_dict['vals'] = vals

        if openid:
            tmpl_id = "fKRko5U-JjPalqSmtG6nlTeuezIpTAD41hGM7JX3NQw"
            tmpl_data = {
                "first": {
                    "value": "您的包裹已发出:",
                    "color": "#173177"
                },
                "keyword1": {
                    "value": item_dict['vals'] or "",
                    "color": "#173177"
                },
                "keyword2": {
                    "value": item_dict['logistics'] or "",
                    "color": "#173177"
                },
                "keyword3": {
                    "value": item_dict['tracking_no'] or "",
                    "color": "#173177"
                },
                "remark": {
                    "value": "取件码[%s]" % item_dict['picking_code'] or "",
                    "color": "#173177"
                },
            }
            shippings[0].wx_information_send(token, openid, tmpl_data, tmpl_id)

        # 发送邮件
        self.env.ref('shipping_bills.mail_template_data_shipping_bill_issue').with_context(
            item_dict=item_dict).send_mail(shippings[0].id, force_send=True)

        # 发送短信
        if shippings[0].sale_partner_id.phone:
            msg = 'Package [%s] has been dispatched. ' \
                  'For queries, contact our customer service.    Sinefine' % item_dict['tracking_no']
            shippings[0].send_message_post(msg)

    # vvip自动扣款逻辑
    def vvip_wallet_payment(self, shippings):
        for shipping in shippings:
            if shipping.sale_partner_id.partner_vip_type == 'svip':
                shipping_sale = shipping.sudo().sale_order_id
                invoice_order = shipping.sale_invoice_ids.filtered(lambda l: l.state != 'cancel')
                for invoice in invoice_order:
                    wallet_id = self.env['website.wallet.transaction'].sudo().create({
                        'wallet_type': 'debit',
                        'partner_id': shipping.sale_partner_id.id,
                        'sale_order_id': shipping_sale.id,
                        'reference': 'sale_order',
                        'amount': invoice.amount_total,
                        'currency_id': invoice.currency_id.id,
                        'status': 'done'
                    })
                    shipping_sale.sudo().write({
                        'wallet_used': invoice.amount_total,
                        'wallet_transaction_id': wallet_id.id
                    })
                    invoice.sudo().update({
                        'wallet_added': True,
                        'invoice_line_ids': [(0, 0, {
                            'name': 'Wallet Used' + ' ' + str(invoice.amount_total),
                            'analytic_account_id': shipping_sale.analytic_account_id.id or False,
                            'price_unit': -shipping_sale.wallet_used,
                            'price_subtotal': -shipping_sale.wallet_used,
                            'quantity': 1,
                            'discount': 0,
                        })],
                    })
        return True
