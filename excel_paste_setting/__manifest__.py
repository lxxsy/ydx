# -*- coding: utf-8 -*-
{
    'name': "excel_paste_setting",
    'version': '0.1',
    'author': "xugang",
    'website': "www.youdingxin.com",
    'category': 'Uncategorized',
    'summary': """Excel粘贴配置""",
    'description': """Excel粘贴配置""",

    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/data.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],

    'application': True,
    'auto_install': False,
}