# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, SUPERUSER_ID
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_partner(self):
        partner = self.env['res.partner']
        if self.sale_line_id:
            partner |= self.sale_line_id.order_id.partner_id
        elif self.picking_id:
            partner |= self.picking_id.partner_id
        return partner

    @api.model
    def create(cls, values):
        self = super().create(values)

        target_location = self._get_partner().team_stock_location_id.filtered(lambda l:l.is_city_agency)
        if target_location:
            if all([
                self.sale_line_id,
                # True or target_location in cls.env['stock.location'].search([('id','child_of',self.location_id.id)])
            ]):
                self.location_id = target_location.id
            elif all([
                self.picking_type_id.code == 'internal',
                not self.location_id.is_city_agency and not self.location_dest_id.is_city_agency,
                # True or target_location in cls.env['stock.location'].search([('id','child_of',self.location_dest_id.id)])
            ]):
                self.location_dest_id = target_location.id
        return self

