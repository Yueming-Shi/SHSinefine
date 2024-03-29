# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError


class ShippingLargeParcel(models.Model):
    _name = 'shipping.large.parcel'
    _description = "大包裹"
    _rec_name = 'name'

    name = fields.Char('包裹号')
    logistics_provider = fields.Char('物流商')
    logistics_tracking_code = fields.Char('物流追踪码')
    length = fields.Float('长')
    width = fields.Float('宽')
    height = fields.Float('高')

    shipping_bill_ids = fields.Many2many(
        'shipping.bill', 'shipping_bill_large_parcel_rel', 'large_parcel_id', 'shipping_bill_id', '客户运单',
        copy=False)

    site_id = fields.Many2one('res.partner', '站点')
    is_sent = fields.Boolean()

    def resend_email(selfs):
        for self in selfs:
            for shipping_bill in self.shipping_bill_ids:
                if shipping_bill.logistics and shipping_bill.tracking_no:
                    shipping_bill.write({
                        'logistics': self.logistics_provider,
                        'tracking_no': self.logistics_tracking_code,
                    })
            # 发送邮件
            template = self.env.ref('shipping_bills.mail_template_shipping_large_parcel')
            email = template.send_mail(self.id, raise_exception=True)
            email_email = self.env['mail.mail'].browse(email)
            email_email.send()
            self.is_sent = True
