# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def model_get_portal_order(cls, force_id=None, force_line_id=None, force_user=None):
        force_id, force_line_id = int(force_id or 0), int(force_line_id or 0)
        if force_line_id:
            self = cls.env['sale.order.line'].browse(force_line_id).order_id
        else:
            self = cls.browse(force_id).exists()
        if not self:
            user = force_user or cls.env.user
            self = cls.search([('partner_id','=',user.partner_id.id),('shipping_no','=',False)],limit=1,order='id desc')
        if not self:
            self = cls.create({'partner_id':user.partner_id.id,})
        return self

    def portal_update_line(self, sale_category_id, brand_id, material_id, qty, order_line_id, product_other):
        sale_category_id, brand_id, material_id, qty = sale_category_id.strip(), brand_id.strip(),\
                                                       material_id.strip(), qty.strip()
        try:
            qty = float(qty)
        except Exception as e:
            raise UserError('无效数量')

        sale_category_id = sale_category_id and int(sale_category_id) or False
        brand_id = brand_id and int(brand_id) or False
        material_id = material_id and int(material_id) or False

        product = self.env['product.product'].model_find_from_portal(sale_category_id, material_id)

        if not order_line_id:
            self.write({'order_line':[(0,0,{
                'product_id': product.id, 'product_uom': product.uom_id.id,
                'product_uom_qty': qty, 'name': product.name,
                'product_brand_id': brand_id,
                'other_remake': product_other
            })]})
        else:
            sale_order_line = self.order_line.filtered(lambda l:str(l.id) == order_line_id)
            sale_order_line.write({
                'product_id': product.id, 'product_uom': product.uom_id.id,
                'product_uom_qty': qty, 'name': product.name,
                'product_brand_id': brand_id.id,
                'other_remake': product_other
            })


    @api.model
    def model_get_portal_orders(cls, force_ids=None, force_user=None):
        if force_ids:
            selfs = cls.browse(int(force_ids)).exists()
        else:
            user = force_user or cls.env.user
            selfs = cls.search([('partner_id','=',user.partner_id.id)])
        return selfs

