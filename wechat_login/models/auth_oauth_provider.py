#!/usr/bin/env python
# -*- coding:utf-8 -*-

from odoo import api, fields, models
from werkzeug.urls import url_encode
from werkzeug.exceptions import BadRequest
import requests


def get_result(url):
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    result = res.json()
    if 'errcode' not in result:
        return result
    else:
        raise BadRequest(res['errmsg'])


class AuthOAuthProvider(models.Model):
    """Class defining the configuration values of an OAuth2 provider"""

    _inherit = 'auth.oauth.provider'

    app_id = fields.Char(string='微信APP ID')
    app_secret = fields.Char(string='微信Secret')
    update_openid = fields.Boolean(string='是否替换微信openID')
    test =  fields.Char()
    def get_wx_token(self, code):
        params = {'appid': self.app_id, 'secret': self.app_secret, 'code': code}
        url = '{}?{}&grant_type=authorization_code'.format(self.validation_endpoint, url_encode(params))
        return get_result(url)

    def get_wx_userinfo(self, token_info):
        params = {'access_token': token_info['access_token'], 'openid': token_info['openid']}
        url = '{}?{}&lang=zh_CN'.format(self['data_endpoint'], url_encode(params))
        user_info = get_result(url)
        user_info['city'] = user_info['province'] + " " + user_info['city']
        return user_info
