# -*- coding: utf-8 -*-



from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    team_id = fields.Many2one(comodel_name='crm.team')
    