# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta

class Website(models.Model):
    _inherit = 'website'

    is_display_personal_home = fields.Boolean('是否替换个人中心')
