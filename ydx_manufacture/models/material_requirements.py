# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class MrpMaterialRequirements(models.Model):
    _name = "mrp.material.requirements"
    _description = "Mrp Material Requirements"
    _order = 'id desc'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        domain="[('type', 'in', ['product', 'consu'])]", required=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        domain="['&', ('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', 'consu'])]",
        help="If a product variant is defined the BOM is available only for this product.")
    mrp_material_requirements_line_ids = fields.One2many('mrp.material.requirements.line', 'mrp_material_requirements_id',
                                                         'Mrp Material Requirements Lines', copy=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Unit of Measure'), required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id, oldname='product_uom', required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of bills of material.")
    is_purchase = fields.Boolean(
        'IsPurchase', default=False,
        help="If the is_purchase field is set to False, it will allow you to hide data without removing it.")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('mrp.material.requirements'),
        required=True)

class MrpMaterialRequirementsLine(models.Model):
    _name = "mrp.material.requirements.line"
    _description = "Mrp Material Requirements Line"
    _order = 'id desc'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    product_id = fields.Many2one(
        'product.product', 'Component', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id', readonly=False)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id,
        oldname='product_uom', required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")
    mrp_material_requirements_id = fields.Many2one(
        'mrp.material.requirements', 'Mrp Material Requirements',
        index=True, required=True)
    parent_product_tmpl_id = fields.Many2one('product.template', 'Parent Product Template', related='mrp_material_requirements_id.product_tmpl_id')
    valid_product_attribute_value_ids = fields.Many2many('product.attribute.value', related='mrp_material_requirements_id.product_tmpl_id.valid_product_attribute_value_ids')
    attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Apply on Variants',
        help="BOM Product Variants needed form apply this line.")
    is_purchase = fields.Boolean(
        'IsPurchase', default=False,
        help="If the is_purchase field is set to False, it will allow you to hide data without removing it.")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('mrp.material.requirements.line'),
        required=True)


class YdxMrpStockMove(models.Model):
    _inherit = 'stock.move'

    purchase_ok = fields.Boolean(related='product_id.purchase_ok', readonly=True)
    virtual_available = fields.Float(
        '预测数量', related='product_id.virtual_available',
        digits=dp.get_precision('Product Unit of Measure'))
    qty_available = fields.Float(
        '在手数量', related='product_id.qty_available',
        digits=dp.get_precision('Product Unit of Measure'))
    reordering_min_qty = fields.Float('安全库存', related='product_id.reordering_min_qty')
