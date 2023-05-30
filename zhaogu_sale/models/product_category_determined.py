# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductCategoryDetermined(models.Model):
    _name = 'product.category.determined'

    name = fields.Char('名称')
    category_id = fields.Many2one('product.sale.category', string="分类名称")
    material_quality_id = fields.Many2one('product.material', string="材质")
    product_brand_id = fields.Many2one('product.brand', string="品牌")
    order_id = fields.Many2one('sale.order', string="订单号")
    order_line_id = fields.Many2one('sale.order.line', string="订单行")
    product_id = fields.Many2one('product.product', string="对应产品", related="order_line_id.product_id")


