from odoo import models, fields, api, _


class ShippingFactor(models.Model):
    _name = 'shipping.factor'
    _description = '线路敏感性'

    name = fields.Char('名称', readonly=True, default='草稿')
    factor = fields.Float(string='体积重系数')
    currency_id = fields.Many2one('res.currency', string='币种', required=True)

    first_weight = fields.Float('首重')
    first_total_price = fields.Float('首重总价')
    next_weight_to_ceil = fields.Float('续重取整')
    next_price_unit = fields.Float('续重单价')

    @api.model
    def create(self, vals_list):
        self.name = self.env['ir.sequence'].next_by_code('shipping.large.parcel')
        return super(ShippingFactor, self).create(vals_list)
