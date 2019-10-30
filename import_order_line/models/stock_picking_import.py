# -*- encoding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError
import base64
import xlrd
from ydxaddons.import_order_line.models.stock_picking_base import PRODUCTION_SHEET_NAME,PRODUCTION_HEADER_ROW,PRODUCTION_DATA_BEGIN_ROW,PRODUCTION_MAP


class ImportStockPickingWizard(models.TransientModel):
    _name = 'import.stock.picking.wizard'
    _description = u"导入子销售订单明细"

    master_id = fields.Many2one('stock.picking', u'调拨单编号', ondelete="cascade", readonly=True)
    excel_file = fields.Binary(u'Excel文件', filters='*.xls')
    filename = fields.Char(u'filename')
    method = fields.Selection([
        ('import', '导入数据'),
        ('update', '更新数据')
    ], string="操作方式", default='import', required=True)

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(ImportStockPickingWizard, self).default_get(fields)
        active_id = self._context.get('active_id', False)
        if not active_id:
            return res
        res.update(master_id=active_id)
        return res

    def _get_domain(self, item, attrstring, value, product_domain, product_uom_domain):
        attrlist = attrstring.split('.')
        is_domain = False
        if len(attrlist) == 2:
            is_domain = True
            if attrlist[0] == "product_id":
                if value == '':
                    item["product_id"] = value
                else:
                    product_domain.append((attrlist[1], '=', value))

            elif attrlist[0] == "product_uom":
                if value == '':
                    item["product_uom"] = [(6, 0,[])]
                else:
                    product_uom_domain.append((attrlist[1], '=', value))

        return is_domain

    def _seache_by_domain(self, model_name, domain):
        return self.env[model_name].search(domain, limit=1)

    def _get_datas(self, sheet, header_row, data_row, data_map, errors):
        tmp_map = []
        for col in range(0, sheet.ncols):
            value = sheet.cell_value(header_row, col)
            for m in data_map:
                if value == m.get('header'):
                    m['col'] = col
                    tmp_map.append(m)
        items = []
        for row in range(data_row, sheet.nrows):
            product_domain = []
            product_uom_domain = []
            item = dict(
                picking_id = self.master_id.id,
            )
            for m in tmp_map:
                coln = m.get("col")
                if coln < sheet.ncols:
                    m_value = sheet.cell_value(row, coln)
                    attrsting = m.get("attribute")
                    attrtype = m.get("type")
                    try:
                        if attrtype == 'int':
                            if m_value:
                                m_value = int(m_value)
                            else:
                                m_value = 0
                        elif attrtype == 'float':
                            if m_value:
                                m_value = float(m_value)
                            else:
                                m_value = 0.0
                        elif attrtype == 'string':
                            if m_value:
                                m_value = str(m_value)
                            else:
                                m_value = ''
                    except:
                        errors.append(u'{sheet}:第{rowvalue}行的[{attr}]数据类型不正确，应该为{type}!'.format(
                            sheet=sheet.name, rowvalue=row+1, attr=m.get('header'), type=attrtype))

                    is_domain= self._get_domain(item, attrsting, m_value, product_domain, product_uom_domain)
                    if not is_domain:
                        if attrsting == "product_opento":
                            if (m_value == "左开") or (m_value == "Left"):
                                m_value = "left"
                            elif (m_value == "右开") or (m_value == "Right"):
                                m_value = "right"
                            elif m_value == "对开":
                                m_value = "twoopen"
                            elif m_value == "上翻":
                                m_value = "upward"
                            elif m_value == "下翻":
                                m_value = "down"
                            elif m_value == "不开":
                                m_value = "noopen"
                            elif m_value == "对开+右开":
                                m_value = "twoopen_and_right"
                            elif m_value == "对开+左开":
                                m_value = "twoopen_and_left"
                            else:
                                errors.append(u'{sheet}:第{rowvalue}行的开向值，系统中不存在!'.format(sheet=sheet.name, rowvalue=row+1))

                        item[attrsting] = m_value

            item['product_speci_type'] = "%s-%s-%s-%s" % (item['plane_materiel'], item['thickness'], item['length'], item['width'])
            if product_domain:
                if 'product_speci_type' in item:
                    ps_type = item.get('product_speci_type')
                    if ps_type:
                        product_domain.append(('ps_speci_type', '=', ps_type))
                    else:
                        product_domain.append('|'),
                        product_domain.append(('ps_speci_type', '=', False))
                        product_domain.append(('ps_speci_type', '=', ''))

                product_id = self._seache_by_domain("product.product", product_domain)
                if not product_id:
                    errors.append(u'{sheet}:第{rowvalue}行的产品名称，系统中不存在!'.format(sheet=sheet.name, rowvalue=row+1))
                else:
                    item["product_id"] = product_id.id
                    item['product_uom'] = product_id.product_tmpl_id.uom_po_id.id

            if product_uom_domain:
                product_uom = self._seache_by_domain('uom.uom', product_uom_domain)
                if not product_uom:
                    errors.append(u'{sheet}:第{rowvalue}行的单位名称，系统中不存在!'.format(sheet=sheet.name,rowvalue=row+1))
                else:
                    item["product_uom"] = product_uom.id

            if item.get("product_id", False):
                item['name'] = item['product_id']
                item['location_id'] = self.master_id.picking_type_id.default_location_src_id.id,
                item['location_dest_id'] = self.master_id.picking_type_id.default_location_dest_id.id,
                items.append(item)

        return items

    def _write_datas(self, model_name, line, datas):
        if self.method == "update":
            for data in datas:
                for l in line:
                    if int(data.get('id', -1)) == l.id:
                        l.write(data)
        elif self.method == "import":
            line.unlink()
            self.env[model_name].create(datas)

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if '物料出库' not in self.master_id.picking_type_id.name:
            raise UserError("导入操作目前只支持物料出库单！")
        if self.excel_file:
            excel = xlrd.open_workbook(file_contents=base64.decodebytes(self.excel_file))
            production_datas = []
            errors = []

            for sheet_name in excel.sheet_names():
                if sheet_name == PRODUCTION_SHEET_NAME:
                    production_sheet = excel.sheet_by_name(PRODUCTION_SHEET_NAME)
                    production_datas = self._get_datas(production_sheet, PRODUCTION_HEADER_ROW, PRODUCTION_DATA_BEGIN_ROW, PRODUCTION_MAP, errors)

            if errors:
                raise UserError(u'表中数据有以下问题：\n {errors}'.format(errors='\n'.join(errors)))

            if production_datas:
                self._write_datas("stock.move", self.master_id.move_ids_without_package, production_datas)

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wizard_view(self):
        view = self.env.ref('import_order_line.form_import_sub_sale_order_line_wizard')
        return {'name': _(u'导入订单明细'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.stock.picking.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': self.ids[0],
                'context': self.env.context}