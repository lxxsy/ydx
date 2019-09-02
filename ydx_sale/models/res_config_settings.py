# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    so_order_approval = fields.Boolean('Sale Order Approval')
    so_double_validation_amount = fields.Monetary(string='The Smallest Number',
        currency_field='company_currency_id',
        help="The Smallest Number")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')
    sale_contract_approval = fields.Boolean('Sale Contract Approval')
    sale_return_approval = fields.Boolean('Sale Return Approval', default=True)
    sale_return_double_validation_amount = fields.Monetary(string='The Smallest Number',
                                                  currency_field='company_currency_id',
                                                  help="Minimum amount for which a double validation is required for sale order")


    def get_values(self):
        res = super(ResConfiguration, self).get_values()
        res.update(
            so_order_approval=self.env['ir.config_parameter'].sudo().get_param('sale_approval_workflow.so_order_approval'),
            so_double_validation_amount=float(self.env['ir.config_parameter'].sudo().get_param('sale_approval_workflow.so_double_validation_amount')),
            sale_contract_approval=self.env['ir.config_parameter'].sudo().get_param('sale.sale_contract_approval'),
            sale_return_approval=self.env['ir.config_parameter'].sudo().get_param('sale_approval_workflow.sale_return_approval'),
            sale_return_double_validation_amount=float(self.env['ir.config_parameter'].sudo().get_param('sale_approval_workflow.sale_return_double_validation_amount')),

        )
        return res

    def set_values(self):
        super(ResConfiguration, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('sale_approval_workflow.so_order_approval', self.so_order_approval)
        self.env['ir.config_parameter'].sudo().set_param('sale_approval_workflow.so_double_validation_amount', self.so_double_validation_amount)
        self.env['ir.config_parameter'].sudo().set_param('sale.sale_contract_approval', self.sale_contract_approval)
        self.env['ir.config_parameter'].sudo().set_param('sale_approval_workflow.sale_return_approval', self.sale_return_approval)
        self.env['ir.config_parameter'].sudo().set_param('sale_approval_workflow.sale_return_double_validation_amount', self.sale_return_double_validation_amount)

