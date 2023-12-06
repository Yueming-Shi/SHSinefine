# See LICENSE file for full copyright and licensing details.

{
    'name': 'zhaogu_website_my_home',
    'depends': [
        'base', 'website', 'website_sale_wishlist'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/action.xml',
        'views/menu.xml',
        'views/web_protal_img_view.xml',
        'views/website_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
