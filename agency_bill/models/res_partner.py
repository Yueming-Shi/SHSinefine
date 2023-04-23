# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, SUPERUSER_ID
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_commission_rate = fields.Float('提成比例(%)')

    property_account_transfer_id = fields.Many2one('account.account','调拨科目')
    property_account_commission_id = fields.Many2one('account.account','结算科目')

