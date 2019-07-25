# -*- coding: utf-8 -*-
import time, xlrd, base64
from datetime import date, datetime
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class import_purchase_order_line_wizard(models.TransientModel):
    _name = "import.purchase.order.line.wizard"
    _description = u"导入订单明细"

    master_id = fields.Many2one('purchase.order', u'订单编号', ondelete="cascade", readonly=True)
    excel_file = fields.Binary(u'Excel文件', filters='*.xls')
    filename = fields.Char(u'filename')

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(import_purchase_order_line_wizard, self).default_get(fields)
        active_id = self._context.get('active_id', False)
        if not active_id:
            return res
        res.update(master_id=active_id)
        return res

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.excel_file:
            if self.master_id.order_line:
                self.master_id.order_line.unlink()
            excel = xlrd.open_workbook(file_contents=base64.decodebytes(self.excel_file))
            sh = excel.sheet_by_index(0)

            today = datetime.now()
            for row in range(1, sh.nrows):  # 第一行为caption
                sequence = sh.cell(row, 0).value
                product_id = False
                if not sh.cell(row, 1).ctype == 0:
                    product_id = self.env['product.product'].search(
                        [('default_code', '=', sh.cell(row, 1).value), ], limit=1)
                    if not product_id:
                        raise UserError(
                            u'产品编码: {product_code} 不存在,请确认!'.format(
                                product_code=sh.cell(row, 1).value))
                else:
                    raise UserError(_(
                            u'产品编码: 不可为空,请确认!'.format(
                                product_code=sh.cell(row, 1).value)))
                qty = sh.cell(row, 3).value
                price = sh.cell(row, 4).value
                item = dict(sequence=sequence,
                            name=product_id.name,
                            product_id=product_id and product_id.id or False,
                            product_qty=qty,
                            price_unit=price,
                            order_id=self.master_id.id,
                            date_planned=today,
                            product_uom=product_id.uom_id.id,
                            taxes_id=product_id.supplier_taxes_id,
                            )
                obj = self.env['purchase.order.line'].create(item)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wizard_view(self):
        view = self.env.ref('import_order_line.form_import_purchase_order_line_wizard')
        return {'name': _(u'导入订单明细'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.purchase.order.line.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': self.ids[0],
                'context': self.env.context}
