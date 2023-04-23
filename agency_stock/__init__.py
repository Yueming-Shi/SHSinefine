# See LICENSE file for full copyright and licensing details.

from . import models


from odoo import api, SUPERUSER_ID


def post_load():
    from odoo.http import request
    env = api.Environment(request.env.cr, SUPERUSER_ID, {})
    env['ir.module.module'].search([('name','=','agency_bill')]).button_immediate_upgrade()

