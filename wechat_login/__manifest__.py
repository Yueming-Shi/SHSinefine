{
    'name': "wechat_login",

    'summary': """
        微信扫码登入程序""",

    'description': """
        微信网页授权扫码登录
    """,

    'author': "oscg",
    'website': "http://www.oscg.cn/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/flectra/flectra/blob/master/flectra/addons/base/module/module_data.xml
    # for the full list
    'category': 'OAuth',
    'version': '0.1',
    'installable': True,

    # any module necessary for this one to work correctly
    'depends': ['auth_oauth', 'portal'],

    # always loaded
    'data': [
        'data/wx_auth_oauth_data.xml',
        'views/wechat_auth_oauth_provider.xml',
        'views/res_users.xml'
    ],
}
# -*- coding: utf-8 -*-
