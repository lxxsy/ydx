# -*- coding: utf-8 -*-
{
    'name': "ydx_sale",

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
    'depends': ['base', 'sale', 'sales_team', 'product', 'purchase', 'sale_management', 'sale_stock','ydx_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'data/sale_data.xml',
        'report/sale_contract_reports.xml',
        'report/sale_contract_templates.xml',
        'wizards/sale_order_line_price_history.xml',
        'wizards/sale_make_invoice_advance_views.xml',
        'views/menu.xml',
        'views/details_views.xml',
        'views/sales_order_history_view.xml',
        'views/line_pice_history_views.xml',
        'views/res_config_setting_view.xml',
        'views/sale_order_view.xml',
        'views/sale_contract_view.xml',
		'views/returned_money_lists.xml',
		'views/sale_return_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
