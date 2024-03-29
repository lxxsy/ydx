# -*- encoding: utf-8 -*-
from odoo import fields, models, api
import base64
import xlwt
import datetime
from io import BytesIO
from ydxaddons.import_order_line.models.purchase_line_base import PURCHASE_SHEET_NAME,PURCHASE_HEADER_ROW,PURCHASE_DATA_BEGIN_ROW,\
     PURCHASE_MAP

style = xlwt.XFStyle()
pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow'] #设置单元格背景色为黄色
style.pattern = pattern

datestyle = xlwt.XFStyle()
datestyle.num_format_str = 'yyyy/mm/dd'

class ExportPurchaseLineWizard(models.Model):
    _name = 'export.purchase.line.wizard'

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
        # if isinstance(value, datetime.datetime):
        #     value = value.strftime("%Y/%m/%d")
        if attr == "product_opento":
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

    def _write_data(self, sheet, header_row, data_row, map, data):
        for m in map:
            if m.get("required"):
                sheet.write(header_row, m.get('col'), m.get('header'), style=style)
            else:
                sheet.write(header_row, m.get('col'), m.get('header'))

        for row in range(data_row, len(data)+data_row):
            d = data[row-data_row]
            for m in map:
                attr = m.get("attribute")
                if not attr:
                    continue
                value = self._get_attribute(attr,d)
                if attr == "taxes_id.name" and not value:
                    value = ''
                if attr == "date_planned":
                    sheet.write(row, m.get('col'), value, style=datestyle)
                else:
                    sheet.write(row, m.get('col'), value)

    def generate_excel(self, purchase_order_id):
        """
        根据产品数据导出excel
        :param product_ids: product.template()
        :return:
        """
        workbook = xlwt.Workbook(encoding='utf-8')

        # 写入外购工作表
        worksheet = workbook.add_sheet(PURCHASE_SHEET_NAME)
        self._write_data(worksheet, PURCHASE_HEADER_ROW, PURCHASE_DATA_BEGIN_ROW,
                         PURCHASE_MAP, purchase_order_id.order_line)

        # save
        buffer = BytesIO()
        workbook.save(buffer)
        return base64.encodebytes(buffer.getvalue())

    @api.multi
    def action_export(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        purchase_order_id = self.env['purchase.order'].search([('id', '=', active_id)])
        self.file = self.generate_excel(purchase_order_id)

        value = dict(
            type='ir.actions.act_url',
            target='new',
            url='/web/content?model=%s&id=%s&field=file&download=true&filename=采购明细_%s.xls' % (self._name, self.id, purchase_order_id.name),
        )
        return value