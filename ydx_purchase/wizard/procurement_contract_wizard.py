# -*- coding: utf-8 -*-
from odoo import models, fields


class ProcurementContractWizard(models.TransientModel):
    _name = 'procurement.contract.wizard'

    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase orders')

    def add_procurement_contract(self):
        action = self.env.ref('ydx_purchase.procurement_contract_management_view')
        result = action.read()[0]
        no_create = self.env.context.get('no_create', False)
        res = self.env.ref('ydx_purchase.procurement_contract_management_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        context = {}
        context.update(active_model=self.env['purchase.procurement.contract'],
                       default_purchase_order_ids=self.purchase_order_ids
                       )
        result['context'] = context
        if not no_create:
                result['res_id'] = self.purchase_contract_ids.id or False
        return result

