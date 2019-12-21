from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OtherCostStatistics(models.Model):
    _name = 'other.cost.statistics'
    _description = 'Other Cost Statistics'

    name = fields.Char(string='New', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    sale_order_id = fields.Many2one('sale.order', ondelete='set null', string='Sale Order', required=True)
    cost_details_ids = fields.One2many('cost.details', 'other_cost_statistics_id', string='Cost Details')
    currency_id = fields.Many2one("res.currency", related='sale_order_id.currency_id', string="Currency", readonly=True,
                                  required=True)
    cost_subtotal = fields.Monetary(string='Cost Subtotal', readonly=True, store=True, compute='_cost_subtotal')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('other.cost.statistics') or _('New')
        result = super().create(vals)
        return result

    @api.depends('cost_details_ids.cost')
    def _cost_subtotal(self):
        for cost_details in self.cost_details_ids:
            self.cost_subtotal += cost_details.cost


class OtherCostCategories(models.Model):
    _name = 'other.cost.categories'
    _description = 'Other Cost Categories'

    name = fields.Char(string='Categories Name', required=True)


class CostDetails(models.Model):
    _name = 'cost.details'
    _description = 'Cost Details'

    other_cost_categories_id = fields.Many2one('other.cost.categories', string='Other Cost Categories',
                                               required=True, ondelete='set null')
    other_cost_statistics_id = fields.Many2one('other.cost.statistics', string='Other Cost Statistics',
                                               required=True, ondelete='set null')
    currency_id = fields.Many2one("res.currency", related='other_cost_statistics_id.currency_id', string="Currency",
                                  readonly=True, required=True)
    note = fields.Text(string='Note')
    cost = fields.Monetary(string='Cost', default=0.0)

    @api.onchange('other_cost_categories_id')
    def _onchange_other_cost_categories(self):
        current_cost_statistics_id = self.env['other.cost.statistics'].search([
            ('name', '=', self.other_cost_statistics_id.name)]).id
        current_cost_details = self.search([('other_cost_statistics_id', '=', current_cost_statistics_id)])
        for current_cost_detail in current_cost_details:
            if current_cost_detail.other_cost_categories_id.id == self.other_cost_categories_id.id:
                raise UserError('当前成本类别已有明细!')



