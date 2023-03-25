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

    shipping_bill_ids = fields.Many2many(
        'shipping.bill', 'shipping_bill_large_parcel_rel', 'large_parcel_id', 'shipping_bill_id', '客户运单',
        copy=False)

    site_id = fields.Many2one('res.partner', '站点')
    is_sent = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ShippingLargeParcel, self).create(vals_list)
        res.name = res.env['ir.sequence'].next_by_code('shipping.large.parcel')
        return res

    def resend_email(selfs):
        for self in selfs:
            if not self.delivery_time:
                self.delivery_time = datetime.now()
            for shipping_bill in self.shipping_bill_ids:
                shipping_bill.sudo().update({
                    'logistics': self.logistics_provider,
                    'tracking_no': self.logistics_tracking_code,
                    'state': 'transported',
                    'out_date': self.delivery_time
                })
            # 发送邮件
            template = self.env.ref('shipping_bills.mail_template_shipping_large_parcel')
            email = template.sudo().send_mail(self.id, raise_exception=True)
            email_email = self.env['mail.mail'].sudo().browse(email)
            email_email.sudo().send()
            self.is_sent = True
