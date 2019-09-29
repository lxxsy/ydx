from odoo import api, fields, models,_


class YdxPurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    cabinet_no = fields.Char(string='Cabinet Number')
    material = fields.Char(string="Material")
    product_colour = fields.Char(string="Colour")
    length = fields.Float(string='Finished Length')
    width = fields.Float(string='Finished Width')
    thickness = fields.Float(string='Finished Thickness')
    band_number = fields.Char(string="Sealing side information")
    remarks = fields.Text(string="Remarks")
    product_opento = fields.Selection([
        ('left','左开'),
        ('right', '右开'),
        ('twoopen', _('对开')),
        ('upward', _('上翻')),
        ('down', _('下翻')),
        ('noopen', _('不开')),
    ], string='开向')
    product_speci_type = fields.Char(string=_('规格型号'))

    @api.multi
    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(YdxPurchaseRequisitionLine, self)._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        res['cabinet_no'] = self.cabinet_no
        res['material'] = self.material
        res['product_colour'] = self.product_colour
        res['product_length'] = self.length
        res['width'] = self.width
        res['thickness'] = self. thickness
        res['band_number'] = self.band_number
        res['remarks'] = self.remarks
        res['product_opento'] = self.product_opento
        res['product_speci_type'] = self.product_speci_type
        return res
