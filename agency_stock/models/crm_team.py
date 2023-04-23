# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, SUPERUSER_ID

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    stock_location_id = fields.Many2one('stock.location','库存位置')
