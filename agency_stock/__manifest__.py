# See LICENSE file for full copyright and licensing details.

{
    'name': 'agency_stock',
    'depends': [
        'sales_team', 'stock'
    ],
    'data': [
        'views/res_partner.xml',
        'views/stock_location.xml',
        'views/crm_team.xml',
    ],
    'installable': True,
    'auto_install': False,
}
