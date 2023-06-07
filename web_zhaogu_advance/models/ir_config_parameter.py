# See LICENSE file for full copyright and licensing details.
import json

import requests

from odoo import models

odoo_session = requests.Session()

class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def obtain_token(self):
        appid = self.env['ir.config_parameter'].search([('key', '=', 'wechat.appid')]).value
        secret = self.env['ir.config_parameter'].search([('key', '=', 'wechat.appsecret')]).value
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
            appid, secret)
        res = odoo_session.get(url=url)
        res_json = json.loads(res.text)
        token = res_json['access_token']
        access_token = self.env['ir.config_parameter'].search([('key', '=', 'wechat.access_token')])
        access_token.write({
            'value': token
        })

        return True


