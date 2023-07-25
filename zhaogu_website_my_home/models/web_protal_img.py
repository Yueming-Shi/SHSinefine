# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class WebProtalImg(models.Model):
    _name = 'web.protal.img'

    name = fields.Char('名称')
    url = fields.Char('跳转链接')
    banner_img = fields.Image("图片", max_width=1920, max_height=1920)
    banner_position = fields.Selection([('0', '上方banner'), ('0', '下方banner')], string="位置")


