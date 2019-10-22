# -*- encoding: utf-8 -*-
from odoo import fields, models, api
import base64
import xlwt
from io import BytesIO
from ydxaddons.import_order_line.models.stock_picking_base import FMETAL_SHEET_NAME,FMETAL_HEADER_ROW,FMETAL_DATA_BEGIN_ROW,FMETAL_MAP,\
    CMETAL_SHEET_NAME,CMETAL_HEADER_ROW,CMETAL_DATA_BEGIN_ROW,CMETAL_MAP,\
    PRODUCTION_SHEET_NAME,PRODUCTION_HEADER_ROW,PRODUCTION_DATA_BEGIN_ROW,PRODUCTION_MAP
from odoo.exceptions import UserError

style = xlwt.XFStyle()
pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow'] #设置单元格背景色为黄色
style.pattern = pattern


class ExportStockPickingWizard(models.Model):
    _name = 'export.stock.picking.wizard'

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
                value = str(self._get_attribute(attr,d))
                sheet.write(row, m.get('col'), value)

    def generate_excel(self, picking_id):
        """
        根据产品数据导出excel
        :param product_ids: product.template()
        :return:
        """
        workbook = xlwt.Workbook(encoding='utf-8')

        if picking_id.picking_type_code == 'outgoing':
            # 写入功能五金工作表
            fmetal_worksheet = workbook.add_sheet(FMETAL_SHEET_NAME)
            self._write_data(fmetal_worksheet, FMETAL_HEADER_ROW, FMETAL_DATA_BEGIN_ROW,
                             FMETAL_MAP, picking_id.fmetals_move_ids_without_package)

            # 写入连接五金工作表
            cmetal_worksheet = workbook.add_sheet(CMETAL_SHEET_NAME)
            self._write_data(cmetal_worksheet, CMETAL_HEADER_ROW, CMETAL_DATA_BEGIN_ROW,
                             CMETAL_MAP, picking_id.cmetals_move_ids_without_package)
        else:
            op_worksheet = workbook.add_sheet(PRODUCTION_SHEET_NAME)
            self._write_data(op_worksheet, PRODUCTION_HEADER_ROW,PRODUCTION_DATA_BEGIN_ROW,
                             PRODUCTION_MAP, picking_id.move_ids_without_package)

        # save
        buffer = BytesIO()
        workbook.save(buffer)
        return base64.encodebytes(buffer.getvalue())

    @api.multi
    def action_export(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        picking_id = self.env['stock.picking'].search([('id', '=', active_id)])
        self.file = self.generate_excel(picking_id)

        value = dict(
            type='ir.actions.act_url',
            target='new',
            url='/web/content?model=%s&id=%s&field=file&download=true&filename=调拨单_%s.xls' % (self._name, self.id, picking_id.name),
        )
        return value