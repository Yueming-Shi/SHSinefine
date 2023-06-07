# -*- coding: utf-8 -*-
{
    'name':"OSCG-昆明兆古网站",
    'description':"""
        昆明兆古网站
    """,
    'category': 'Hidden',
    'version':'1.0',
    'depends':['base', 'web', 'website', 'shipping_bills'],
    'data':[
        "views/web_zhaogu_be_claimed_view.xml",
        "views/web_zhaogu_shipping_detail_view.xml",
        "views/web_my_portal_detail_view.xml",
        "views/web_my_portal_invoice_list_view.xml",
        "data/ir_config_parameter_token.xml",
    ],
    'qweb':[

    ],
    'assets': {
            'web.assets_backend': [
                'web_zhaogu_advance/static/src/css/portal_orders_new.css',
            ],
        },
    'auto_install': False,
    'license': 'OEEL-1',
}
