# -*- coding: utf-8 -*-
{
    'name': "销售订单明细导入",

    #简短说明
    'summary': """
        销售订单明细导入
        """,
    #详细描述
    'description': """
        销售订单明细导入
        QQ:1160794317
    """,

    'author': "迈克尔老狼",
    'website': "http://www.erun.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',
    #依赖模组
    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sale_view.xml',
        'wizard/import_sale_order_line_wizard_view.xml',
    ],

    # only loaded in demonstration mode

    'installable': True,
    'auto_install': False,
    'application': True,
}