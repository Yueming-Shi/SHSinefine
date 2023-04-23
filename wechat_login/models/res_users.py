#!/usr/bin/env python
# -*- coding:utf-8 -*-

from odoo import models, fields, api, http


class ResUsers(models.Model):
    _inherit = 'res.users'

    wx_openid = fields.Char('微信openid')

    @api.model
    def get_by_userInfo(cls, user_info, provider_id):
        user = cls.env['res.users'].sudo().search([('login', '=', user_info['unionid'])])
        provider = cls.env['auth.oauth.provider'].browse(provider_id)
        if not user:
            user = cls.create_user(user_info, provider.id)
        if provider.update_openid and not user.wx_openid:
            user.write({'wx_openid': user_info['openid']})
        cls.env.cr.commit()
        return user

    @api.model
    def create_user(cls, user_info, provider_id):
        return cls.with_user(1).create({
            'login': user_info['unionid'],
            'password': user_info['unionid'],
            'name': user_info['nickname'],
            'oauth_provider_id': provider_id,
            'city': user_info['city'],
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })

    def update_mobile(self, mobile):
        return self.partner_id.write({'mobile': mobile})
