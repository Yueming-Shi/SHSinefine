#!/usr/bin/env python
# -*- coding:utf-8 -*-

from werkzeug.urls import url_encode
from werkzeug.exceptions import BadRequest
from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import OAuthLogin as Home, OAuthController as Controller
import requests


def _set_wx_auth_link(provider):
    params = dict(
        appid=provider['app_id'],
        redirect_uri=request.httprequest.url_root + 'wechat/signin_new',
        response_type='code',
        scope=provider['scope'],
        state=str(provider['id'])
    )
    result = '{}?{}#wechat_redirect'.format(provider['auth_endpoint'], url_encode(params))
    return result


class OAuthLogin(Home):

    def list_providers(self):
        providers = super(OAuthLogin, self).list_providers()

        mobile_wx = request.env.ref('wechat_login.mobile_wx_provider').sudo()
        pc_wx = request.env.ref('wechat_login.pc_wx_provider').sudo()

        if not(mobile_wx.enabled and pc_wx.enabled):
            return providers

        for provider in providers:
            if provider['name'] == pc_wx.name:
                pc_wx_provider = provider
            elif provider['name'] == mobile_wx.name:
                mobile_wx_provider = provider

        if request.httprequest.user_agent.platform in ['android', 'iphone']:
            providers.remove(pc_wx_provider)
            mobile_wx_provider['auth_link'] = _set_wx_auth_link(mobile_wx_provider)
        else:
            providers.remove(mobile_wx_provider)
            pc_wx_provider['auth_link'] = _set_wx_auth_link(pc_wx_provider)

        return providers


class OAuthController(Controller):

    @http.route('/wechat/signin_new', type='http', auth='none')
    def wechat_signin(self, **kwargs):
        try:
            provider = request.env['auth.oauth.provider'].sudo().browse(int(kwargs['state']))
            token_info = provider.sudo().get_wx_token(kwargs['code'])
            user_info = provider.sudo().get_wx_userinfo(token_info)
            user = request.env['res.users'].sudo().get_by_userInfo(user_info, provider.id)
            request.session.authenticate(request.session.db, user.login, user_info['unionid'])
            return request.redirect('/')
        except Exception as e:
            return request.redirect('/web/login')

    @http.route('/wechat/update_user_mobile', type='http', auth='none')
    def wechat_update_user_mobile(self, user_id, mobile):
        user = request.env['res.users'].sudo().browse(int(user_id))
        user.sudo().update_mobile(mobile)
        return request.redirect('/')
