# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class SiteLocation(models.Model):
    _name = 'site.location'

    name = fields.Char('位置')
    factor_id = fields.Many2one('shipping.factor', '敏感性')
    site_partner_id = fields.Many2one('res.partner', '站点')
    real_weight = fields.Float('实重')
    package_discard_day = fields.Integer('包裹弃置天数')
