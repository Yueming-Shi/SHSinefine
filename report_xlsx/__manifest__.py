# -*- coding: utf-8 -*-
{
    'name': "Excel报表模板及报表输出",

    'summary': "Excel报表模板及报表输出",
    'author': 'OSCG,',
    'website': "http://www.oscg.cn",
    'category': 'Reporting',
    'version': '0.8',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'openpyxl',
        ],
    },
    'depends': ['base', 'web', ],
    'data': [
        'views/ir_report_view.xml'
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'report_xlsx/static/src/js/report/action_manager_report.js',
        ],
     },
    'installable': True,
}
