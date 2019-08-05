# -*- coding: utf-8 -*-
import time, xlrd, base64
from datetime import date, datetime
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class import_stock_adjust_order_line_wizard(models.TransientModel):
    _name = "import.stock.adjust.order.line.wizard"
    _description = u"导入订单明细"

    master_id = fields.Many2one('stock.inventory', u'订单编号', ondelete="cascade", readonly=True)
    excel_file = fields.Binary(u'Excel文件', filters='*.xls')
    filename = fields.Char(u'filename')

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(import_stock_adjust_order_line_wizard, self).default_get(fields)
        active_id = self._context.get('active_id', False)
        if not active_id:
            return res
        res.update(master_id=active_id)
        return res

    def _check_file(self):
        data_list = []
        err_list = []
        data_index = []
        self.ensure_one()
        if self.excel_file:
            if self.master_id.line_ids:
                self.master_id.line_ids.unlink()
            excel = xlrd.open_workbook(file_contents=base64.decodebytes(self.excel_file))
            sh = excel.sheet_by_index(0)

            for row in range(1, sh.nrows):  # 第一行为caption
                flag = 0
                data={}
                product_id = False
                product_cell = sh.cell(row, 0).value

                if not sh.cell(row, 0).ctype == 0:
                    product_id = self.env['product.product'].search(
                        [('default_code', '=', product_cell), ], limit=1)
                    if not product_id:
                        flag = 1
                        err_list.append(
                            u'{product_code}：产品编码不存在,请确认!\n'.format(
                                product_code=product_cell))
                else:
                    flag = 1
                    err_list.append(u'产品编码: 不可为空,请确认!\n'.format(
                            product_code=product_cell))

                location_cell = sh.cell(row, 1).value
                location_id = False
                if location_cell:
                    location_id = self.env['stock.location'].sudo().search(
                        [('complete_name', '=', location_cell), ], limit=1)
                    if not location_id:
                        flag = 1
                        err_list.append(
                            u'{product_code}: 仓库位置 {location_cell} 不存在,请确认!\n'.format(
                                product_code=product_cell,location_cell=location_cell))
                else:
                    flag = 1
                    err_list.append(
                        u'{product_code}: 仓库位置 {product_cell}的位置不可为空,请确认!\n'.format(
                            product_code=product_cell,product_cell=product_cell))

                key = str(product_cell)+str(location_cell)
                if key in data_index:
                    err_list.append(
                            u'{product_code} {location_cell}：产品和位置重复,请确认!\n'.format(
                                product_code=product_cell,location_cell=location_cell))
                data_index.append(key)
                product_qty = sh.cell(row, 2).value
                if product_qty == '':
                    flag = 1
                    err_list.append(
                        u'{product_code}: 数量不可为空,请确认!\n'.format(
                            product_code=product_cell))
                if flag == 0:
                    data['product_id'] = product_id
                    data['location_id'] = location_id
                    data['product_qty'] = product_qty
                    data_list.append(data)

            if len(err_list) > 0:
                raise UserError(u'数据表错误: \n {err}'.format(err='\n'.join(err_list)))

            return data_list

    @api.multi
    def action_confirm(self):
        data_list = self._check_file()
        for data in data_list:
            item = dict(product_id=data['product_id'].id,
                        product_uom_id=data['product_id'].uom_id.id,
                        product_qty=data['product_qty'],
                        inventory_id=self.master_id.id,
                        location_id=data['location_id'].id
                        )
            obj = self.env['stock.inventory.line'].create(item)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wizard_view(self):
        view = self.env.ref('import_order_line.form_import_stock_adjust_order_line_wizard')
        return {'name': _(u'导入订单明细'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.stock.adjust.order.line.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': self.ids[0],
                'context': self.env.context}
