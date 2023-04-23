# -*- coding: utf-8 -*-
import re
import logging
import qrcode
import base64
from io import BytesIO
from wechatpy.oauth import WeChatOAuth

from odoo import  http, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import SIGN_UP_REQUEST_PARAMS
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.web.controllers import main

 
def is_valid_email(email):
    return  re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


SIGN_UP_REQUEST_PARAMS.update({'site_id'})
_logger = logging.getLogger(__name__)



def make_qrcode(self, qrurl):
    """generate qrcode from url"""
    img = qrcode.make(qrurl)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    heximage = base64.b64encode(buffer.getvalue())
    return "data:image/png;base64,{}".format(heximage.decode('utf-8'))
http.HttpRequest.make_qrcode = make_qrcode


class WeChatPay(http.Controller):

    @http.route('/MP_verify_Jmsp8MJMPOgz9JCy.txt', type='http', auth="public", website=True)
    def wZTUQ2JgWfaLaoLF(self):    
        return 'Jmsp8MJMPOgz9JCy'

        
class PortalAccount(CustomerPortal):

    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'teams_count' in counters:
            teams_count = request.env['crm.team'].sudo().search_count([])
            values['teams_count'] = teams_count
        return values

    @http.route(['/my/teams', '/my/teams/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_teams1(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        TeamsEnv = request.env['crm.team'].sudo()
        domain = []
        teams_count = TeamsEnv.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/teams",
            total=teams_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        teams = TeamsEnv.search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'teams': teams,
            'page_name': 'Teams',
            'pager': pager,
            'default_url': '/my/teams',
        })
        return request.render("wechat_sign.portal_my_teams", values)


class AuthSignupHome(AuthSignupHome):

    def list_teams(self):
        return request.env['crm.team'].sudo().search([])
        
    def get_auth_signup_qcontext(self):
        result = super(AuthSignupHome, self).get_auth_signup_qcontext()
        result["teams"] = self.list_teams()
        base_url = request.httprequest.base_url
       
        result['baes_url'] = base_url
        return result

    def _wechat_instance(self, site_id=0):
        appid = request.env['ir.config_parameter'].sudo().get_param('wechat.appid')
        secret = request.env['ir.config_parameter'].sudo().get_param('wechat.appsecret')        
        base_url = request.httprequest.url_root
        url = '%swechat/signin/%s' % (base_url, site_id)
       
        wechat_auth = WeChatOAuth(appid, secret, url, 'snsapi_userinfo')  
        return wechat_auth

    @http.route(['/wechat/login', '/wechat/login/<int:site>'], type='http', auth='public', website=True, sitemap=False)
    def wechat_login(self, site=0, *args, **kw):
        wechat_auth = self._wechat_instance(site)  
        authorize_url = wechat_auth.authorize_url
       
        return  request.redirect(authorize_url, 301, False) 

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        
        if kw.get('wx_openid', False) and kw.get('access_token', False):
            #如果没有用户 则再获取用户信息 创建用户
            site = kw.get('site_id', 0)
            wechat_auth = self._wechat_instance(site)  
            res = wechat_auth.get_user_info(kw['wx_openid'], kw['access_token'])
            res = request.env['res.users'].create_wechat_user(res, site)
            if res:
                wechat_auth = self._wechat_instance(site)  
                authorize_url = wechat_auth.authorize_url
                
                return  request.redirect(authorize_url, 301, False) 
            else:
                return request.redirect('/404')

        user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
        if user_agent.find('MicroMessenger') > -1:
            wechat_auth = self._wechat_instance(kw.get('site_id', 0))  
            authorize_url = wechat_auth.authorize_url
            return  request.redirect(authorize_url, 301, False) 
        return super().web_auth_signup(*args, **kw)

    def _prepare_signup_values(self, qcontext):
        value = super()._prepare_signup_values(qcontext)
        if qcontext.get('site_id'):
            value.update({
                'team_id': qcontext.get('site_id')
            })
        #base_url = request.httprequest.base_url
        #_logger.info(base_url)
        #value['baes_url'] = base_url
        return value

    @http.route('/web/site/list', type='http', auth='public', website=True, sitemap=False)
    def site_list(self):
        sites = request.env['crm.team'].sudo().search([])
        return request.render("wechat_sign.sitelist", {'sites': sites})
 
class Home(main.Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        #import pdb;pdb.set_trace()
        print(request.session.uid)
        if request.session.uid and request.session.uid != 2 and not is_valid_email(request.env['res.users'].browse(request.session.uid).login):
            return  request.redirect('/bind/email', 301, False) 
        return super().web_client(s_action, **kw)

    @http.route('/bind/email', type='http',auth='public', website=True)
    def bind_email(self, **kw):
        if request.httprequest.method == 'POST':
            if request.params.get('login'):
                login = request.params.get('login')
                if is_valid_email(login):                    
                    request.env['res.users'].browse(request.session.uid).write({'login': login})
                    try:
                        request.env['res.users'].browse(request.session.uid).action_reset_password()
                    except Exception as e:
                        _logger.info(str(e))
                    return request.redirect('/web/signup')
                else:
                    return request.render('wechat_sign.bind_email', {'error': 'Invaild email'})
                    
        return request.render('wechat_sign.bind_email')