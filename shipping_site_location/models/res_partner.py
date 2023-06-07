# import logging

from odoo import models, fields, api, _


# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # 仓库位置
    site_location_ids = fields.One2many('site.location', 'site_partner_id', string="仓库位置")

    partner_vip_type = fields.Selection([('svip', 'SVIP'), ('vip', 'VIP'), ('common', '普通')], string="客户类型", default='common')

    team_id = fields.Many2one('crm.team', tracking=True)

    def normal_partner_vip_type(selfs):
        for self in selfs:
            self.partner_vip_type = 'common'
