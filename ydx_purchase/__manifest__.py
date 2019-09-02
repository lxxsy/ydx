# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    "name" : "ydx_purchase",
    "version" : "12.0.0.0",
    "summary": " Purchase Order template",
    "category": "Purchase",
    
    "description": """
    Product_template
    """ ,

    "depends" : ["base", "purchase", "ydx_base",'ps_account_payable','account','stock','ps_account_receivable'],
    "data": [
        'data/purchase_data.xml',
        'views/purchase_custom_view.xml',
        'views/procurement_contract_wizard.xml',
        'views/res_config_setting_view.xml',
        'report/procurement_contract_templates.xml',
        'report/procurement_contract_reports.xml',
        'security/ir.model.access.csv',
		'views/purchase_return_views.xml',
        'views/returned_money_list.xml',
        'views/procurement_contract_views.xml',
        'views/purchase_views_inherit.xml',
        'data/purchase_return_id_ai.xml',
    ],

    "author": "xugang",
    "installable": True,
    "application": True,
    "auto_install": False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
