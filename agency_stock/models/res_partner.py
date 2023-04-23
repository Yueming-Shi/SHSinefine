# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, SUPERUSER_ID
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_state_agency = fields.Boolean('是省代')
    is_city_agency = fields.Boolean('是城代')
    is_customer = fields.Boolean('是客户')

    state_agency_id = fields.Many2one('res.partner','省级代理')
    city_agency_ids = fields.One2many('res.partner','state_agency_id','下属城市代理')

    city_agency_id = fields.Many2one('res.partner','城市代理')
    customer_ids = fields.One2many('res.partner','city_agency_id','下属客户')

    team_stock_location_id = fields.Many2one(related='team_id.stock_location_id', store=True)