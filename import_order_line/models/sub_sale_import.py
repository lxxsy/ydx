# -*- encoding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError
import base64
import xlrd
from ydxaddons.import_order_line.models.sub_sale_base import OUTSOURCE_SHEET_NAME,OUTSOURCE_HEADER_ROW,OUTSOURCE_DATA_BEGIN_ROW,\
     OUTSOURCE_MAP,FMETAL_SHEET_NAME,FMETAL_HEADER_ROW,FMETAL_DATA_BEGIN_ROW,FMETAL_MAP,PRODUCTION_SHEET_NAME,PRODUCTION_HEADER_ROW,\
    PRODUCTION_DATA_BEGIN_ROW,PRODUCTION_MAP,CMETAL_SHEET_NAME,CMETAL_HEADER_ROW,CMETAL_DATA_BEGIN_ROW,CMETAL_MAP


class ImportSubSaleWizard(models.TransientModel):
    _name = 'import.sub.sale.wizard'
    _description = u"导入子销售订单明细"

    master_id = fields.Many2one('sub.sale.order', u'子订单编号', ondelete="cascade", readonly=True)
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
        res = super(ImportSubSaleWizard, self).default_get(fields)
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
                order_id = self.master_id.order_id.id,
                sub_order_id = self.master_id.id,
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

            items.append(item)

        return items

    def _get_cmetal_datas(self, sheet, header_row, data_row, data_map, errors):
        tmp_map = []
        name_col = -1
        total_row = -1
        sm_row = -1
        for col in range(0, sheet.ncols):
            value = sheet.cell_value(header_row, col)
            for m in data_map:
                if value == m.get('header'):
                    if value == "名称":
                        name_col = col
                    m['col'] = col
                    tmp_map.append(m)
        items = []
        if name_col < 0:
            raise UserError("连接五金没有找到列【名称】，名称是必须有的列。")

        for row in range(data_row, sheet.nrows):
            tmp_value1 = sheet.cell_value(row, name_col)
            tmp_value2 = sheet.cell_value(row, 0)
            if "总量" in tmp_value1:
                total_row = row
            if "说明" in tmp_value2:
                sm_row = row

        if (total_row < 0) or (sm_row < 0) or (total_row >= sm_row) or (sm_row > sheet.nrows):
            raise UserError("连接五金没有找到【总量】或 【说明】，总量和说明是输入内容的定位符,并且说明所在的行必须在总量的下面。")

        for row in range(total_row+1, sm_row):
            product_domain = []
            product_uom_domain = []
            item = dict(
                order_id = self.master_id.order_id.id,
                sub_order_id = self.master_id.id,
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

        if self.excel_file:
            excel = xlrd.open_workbook(file_contents=base64.decodebytes(self.excel_file))
            outsource_datas = []
            fmetal_datas = []
            production_datas = []
            cmetal_datas = []
            errors = []

            for sheet_name in excel.sheet_names():
                if sheet_name == OUTSOURCE_SHEET_NAME:
                    outsource_sheet = excel.sheet_by_name(OUTSOURCE_SHEET_NAME)
                    outsource_datas = self._get_datas(outsource_sheet, OUTSOURCE_HEADER_ROW, OUTSOURCE_DATA_BEGIN_ROW, OUTSOURCE_MAP, errors)
                elif sheet_name == FMETAL_SHEET_NAME:
                    fmetal_sheet = excel.sheet_by_name(FMETAL_SHEET_NAME)
                    fmetal_datas = self._get_datas(fmetal_sheet, FMETAL_HEADER_ROW, FMETAL_DATA_BEGIN_ROW, FMETAL_MAP, errors)
                elif sheet_name == PRODUCTION_SHEET_NAME:
                    production_sheet = excel.sheet_by_name(PRODUCTION_SHEET_NAME)
                    production_datas = self._get_datas(production_sheet, PRODUCTION_HEADER_ROW, PRODUCTION_DATA_BEGIN_ROW, PRODUCTION_MAP, errors)
                elif sheet_name == CMETAL_SHEET_NAME:
                    cmetal_sheet = excel.sheet_by_name(CMETAL_SHEET_NAME)
                    cmetal_datas = self._get_cmetal_datas(cmetal_sheet, CMETAL_HEADER_ROW, CMETAL_DATA_BEGIN_ROW, CMETAL_MAP, errors)

            if errors:
                raise UserError(u'表中数据有以下问题：\n {errors}'.format(errors='\n'.join(errors)))

            if outsource_datas:
                self._write_datas("res.outsource", self.master_id.outsource_line, outsource_datas)

            if fmetal_datas:
                self._write_datas("res.function.metal", self.master_id.function_metal_line, fmetal_datas)

            if production_datas:
                self._write_datas("res.production.part", self.master_id.production_part_line, production_datas)

            if cmetal_datas:
                self._write_datas("res.connection.metal", self.master_id.connection_metal_line, cmetal_datas)

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wizard_view(self):
        view = self.env.ref('import_order_line.form_import_sub_sale_order_line_wizard')
        return {'name': _(u'导入订单明细'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.sub.sale.order.line.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': self.ids[0],
                'context': self.env.context}