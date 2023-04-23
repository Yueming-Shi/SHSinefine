# See LICENSE file for full copyright and licensing details.

{
    'name': 'agency_bill',
    'depends': [
        'agency_stock', 'website_sale',
    ],
    'data': [
        'data/ir_actions_server.xml',
        'views/res_partner.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/website.xml',
    ],
    'installable': True,
    'auto_install': False,
}
