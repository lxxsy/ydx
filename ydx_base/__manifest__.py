# -*- coding: utf-8 -*-
{
    'name': "ydx_base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'uom', 'purchase', 'sale', 'sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_inherit_view.xml',
        'views/product_views.xml',
        'data/data.xml',
        'data/ydx_decimal_precision_inherit_data.xml',
        'views/product_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}