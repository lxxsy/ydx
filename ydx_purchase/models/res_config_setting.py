from odoo import fields, models

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_contract_approval = fields.Boolean('Purchase Contract Approval')
    so_return_approval = fields.Boolean('Purchase Return Money Approval', default=True)
    so_double_validation_amount = fields.Monetary(string='The Samllest Number',
                                                  currency_field='company_currency_id',
                                                  help="Minimum amount for which a double validation is required for sale order")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
                                          help='Utility field to express amount currency')

    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        res.update(
            purchase_contract_approval=self.env['ir.config_parameter'].sudo().get_param('purchase.purchase_contract_approval'),
            so_return_approval=self.env['ir.config_parameter'].sudo().get_param('purchase_approval_workflow.so_return_approval'),
            so_double_validation_amount=float(self.env['ir.config_parameter'].sudo().get_param('purchase_approval_workflow.so_double_validation_amount'))
        )
        return res

    def set_values(self):
        super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('purchase.purchase_contract_approval', self.purchase_contract_approval)
        self.env['ir.config_parameter'].sudo().set_param('purchase_approval_workflow.so_return_approval', self.so_return_approval)
        self.env['ir.config_parameter'].sudo().set_param('purchase_approval_workflow.so_double_validation_amount', self.so_double_validation_amount)