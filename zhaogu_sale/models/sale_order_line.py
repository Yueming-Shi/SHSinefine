# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_sale_category_id = fields.Many2one(related='product_id.sale_category_id',store=True)
    product_material_id = fields.Many2one(related='product_id.material_id',store=True)
    product_brand_id = fields.Many2one('product.brand','品牌')
    other_remake = fields.Char('其他备注')

    brand_is_in_blacklist = fields.Boolean('黑名单',related='product_brand_id.is_in_blacklist',store=True)

    def name_get(self):
        result = []
        for record in self:
            name = '%s - %s' % (record.order_id.name, record.product_id.name)
            result.append((record.id, name))
        return result

