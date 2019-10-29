# -*- encoding: utf-8 -*-
from odoo import fields, models, api
import base64
import xlwt
from io import BytesIO
from ydxaddons.import_order_line.models.sale_order_base import OUTSOURCE_SHEET_NAME,OUTSOURCE_HEADER_ROW,OUTSOURCE_DATA_BEGIN_ROW,\
     OUTSOURCE_MAP,FMETAL_SHEET_NAME,FMETAL_HEADER_ROW,FMETAL_DATA_BEGIN_ROW,FMETAL_MAP

style = xlwt.XFStyle()
pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow'] #设置单元格背景色为黄色
style.pattern = pattern


class ExportSaleOrderWizard(models.Model):
    _name = 'export.sale.order.wizard'

    file = fields.Binary('导出文件')

    def _get_attribute(self, attrstring, object):
        attrlist = attrstring.split('.')
        value = ''
        tmp_object = object
        for attr in attrlist:
            value = getattr(tmp_object, attr)
            tmp_object = value

        if not value:
            return ""

        if attrstring == "product_opento":
            if value == 'left':
                value = "左开"
            elif value == 'right':
                value = "右开"
            elif value == 'twoopen':
                value = "对开"
            elif value == 'upward':
                value = "上翻"
            elif value == 'down':
                value = "下翻"
            elif value == 'noopen':
                value = "不开"
            elif value == 'twoopen_and_right':
                value = "对开+右开"
            elif value == 'twoopen_and_left':
                value = "对开+左开"
        return value

    def _write_data(self, sheet, map, data, line):
        for m in map:
            if m.get("required"):
                sheet.write(line, m.get('col'), m.get('header'), style=style)
            else:
                sheet.write(line, m.get('col'), m.get('header'))
        line += 1
        for row in range(line, len(data)+line):
            d = data[row-line]
            for m in map:
                attr = m.get("attribute")
                if attr == "null":
                    sheet.write(row, m.get('col'), "")
                    continue
                if not attr:
                    continue
                value = self._get_attribute(attr,d)
                sheet.write(row, m.get('col'), value)

    def _write_before_header(self, outsource_worksheet, line1, line2, col1, col2, msg):
        outsource_worksheet.write_merge(line1, line2, col1, col2, msg)

    def generate_excel(self, sale_id):
        """
        根据产品数据导出excel
        :param product_ids: product.template()
        :return:
        """
        workbook = xlwt.Workbook(encoding='utf-8')

        # 写入外购工作表
        outsource_line = 0
        outsource_col = len(OUTSOURCE_MAP)
        outsource_worksheet = workbook.add_sheet(OUTSOURCE_SHEET_NAME)
        for sub_sale_id in sale_id.sub_sale_order_ids:
            msg = "单号：%s" % (sub_sale_id.name)
            self._write_before_header(outsource_worksheet,
                                      outsource_line,
                                      outsource_line,
                                      0,
                                      outsource_col-1,
                                      msg)
            outsource_line += 1
            self._write_data(outsource_worksheet, OUTSOURCE_MAP, sub_sale_id.outsource_line, outsource_line)
            outsource_line += len(sub_sale_id.outsource_line) + 1

        # 写入功能五金工作表
        fmetal_line = 1
        fmetal_col = len(FMETAL_MAP)
        fmetal_worksheet = workbook.add_sheet(FMETAL_SHEET_NAME)
        for sub_sale_id in sale_id.sub_sale_order_ids:
            msg = "单号：%s" % (sub_sale_id.name)
            self._write_before_header(fmetal_worksheet,
                                      fmetal_line,
                                      fmetal_line,
                                      0,
                                      fmetal_col-1,
                                      msg)
            fmetal_line += 1
            self._write_data(fmetal_worksheet, FMETAL_MAP, sub_sale_id.function_metal_line, fmetal_line)
            fmetal_line += len(sub_sale_id.function_metal_line) + 1

        # save
        buffer = BytesIO()
        workbook.save(buffer)
        return base64.encodebytes(buffer.getvalue())

    @api.multi
    def action_export(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        sale_id = self.env['sale.order'].search([('id', '=', active_id)])
        self.file = self.generate_excel(sale_id)

        value = dict(
            type='ir.actions.act_url',
            target='new',
            url='/web/content?model=%s&id=%s&field=file&download=true&filename=销售订单_%s.xls' % (self._name, self.id, sale_id.name),
        )
        return value