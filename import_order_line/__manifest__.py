# -*- coding: utf-8 -*-
{
    'name': "订单明细导入",

    #简短说明
    'summary': """
        订单明细导入
        """,
    #详细描述
    'description': """
        订单明细导入
    """,

    'author': "xugang",
    'website': "http://www.youdingxin.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'other',
    'version': '0.2',
    #依赖模组
    # any module necessary for this one to work correctly
    'depends': ['sale','purchase','stock', 'ydx_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'wizard/import_sale_order_line_wizard_view.xml',
        'views/purchase_view.xml',
        'views/export_sub_sale_view.xml',
        'views/import_sub_sale_view.xml',
        'wizard/import_purchase_order_line_wizard_view.xml',
        'views/stock_adjust_view.xml',
        'wizard/import_stock_adjust_order_line_wizard_view.xml',
        'views/export_purchase_line_view.xml',
        'views/import_purchase_line_view.xml',
        'views/export_stock_picking_view.xml',
        'views/import_stock_picking_view.xml',
    ],

    # only loaded in demonstration mode

    'installable': True,
    'auto_install': True,
    'application': True,
}