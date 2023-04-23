# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, SUPERUSER_ID
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_city_agency = fields.Boolean('城市代理')