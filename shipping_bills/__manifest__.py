{
    'name': 'Shipping Bills',
    'description': 'Shipping Bills',
    'category': 'Operations/Inventory',
    'summary': 'shipping bill',
    'sequence': 300,
    'version': '15.1.0',
    'website': 'http://www.oscg.cn/',
    'author': 'OSCG',
    'license': 'AGPL-3',
    'depends': ['sale','delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_team.xml',
        'views/sale_order.xml',
        'views/shipping_bill.xml',
        'views/shipping_factor.xml',
        'views/product_product_view.xml',
        'views/shipping_large_parcel.xml',
        'views/shipping_state.xml',
        'views/modification_fee_view.xml',
        'views/res_partner_view.xml',
        'views/action.xml',
        'views/menu.xml',
        'data/ir_actions_server.xml',
        'data/ir_config_parameter.xml',
        'data/ir_sequence.xml',
        'data/product_product.xml',
        'data/modification_fee.xml',
        'data/ir_cron.xml',
        'data/mail_template_date.xml',
        'data/shipping_state.xml',
        'wizard/action.xml',
        'wizard/menu.xml',
        'wizard/shipping_bill_update_transport_wizard.xml',
        'wizard/shipping_bill_update_arrive_wizard.xml',
        'wizard/shipping_bill_update_sign_wizard.xml',
        'wizard/shipping_bill_update_return_wizard.xml',
        'wizard/shipping_bill_update_discard_wizard.xml',
        'wizard/shipping_large_parcel_vvip_confirm_wizard.xml',
    ],

}
