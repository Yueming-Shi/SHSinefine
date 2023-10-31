# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api

class Website(models.Model):
    _inherit = 'website'

    should_city_agency_care = fields.Boolean('城市代理')
