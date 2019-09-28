# -*- encoding: utf-8 -*-
from odoo import fields, models, api
import base64
import xlwt
from io import BytesIO
from ydxaddons.import_order_line.models.sub_sale_base import OUTSOURCE_SHEET_NAME,OUTSOURCE_HEADER_ROW,OUTSOURCE_DATA_BEGIN_ROW,\
     OUTSOURCE_MAP,FMETAL_SHEET_NAME,FMETAL_HEADER_ROW,FMETAL_DATA_BEGIN_ROW,FMETAL_MAP,PRODUCTION_SHEET_NAME,PRODUCTION_HEADER_ROW,\
    PRODUCTION_DATA_BEGIN_ROW,PRODUCTION_MAP,CMETAL_SHEET_NAME,CMETAL_HEADER_ROW,CMETAL_DATA_BEGIN_ROW,CMETAL_MAP

class ExportSubSaleWizard(models.Model):
    _name = 'export.sub.sale.wizard'

    file = fields.Binary('导出文件')

    def _get_attribute(self, attrstring, object):
        attrlist = attrstring.split('.')
        value = ''
        tmp_object = object
        for attr in attrlist:
            value = getattr(tmp_object, attr)
            tmp_object = value

        if attrstring == "product_opento":
            if value == 'left':
                value = "左开门"
            elif value == 'right':
                value = "右开门"

        return value

    def _write_data(self, sheet, header_row, data_row, map, data):
        for m in map:
            sheet.write(header_row, m.get('col'), m.get('header'))

        for row in range(data_row, len(data)+data_row):
            d = data[row-data_row]
            for m in map:
                attr = m.get("attribute")
                if not attr:
                    continue
                value = self._get_attribute(attr,d)
                sheet.write(row, m.get('col'), value)

    def generate_excel(self, sub_sale_id):
        """
        根据产品数据导出excel
        :param product_ids: product.template()
        :return:
        """
        workbook = xlwt.Workbook(encoding='utf-8')

        # 写入外购工作表
        outsource_worksheet = workbook.add_sheet(OUTSOURCE_SHEET_NAME)
        self._write_data(outsource_worksheet, OUTSOURCE_HEADER_ROW, OUTSOURCE_DATA_BEGIN_ROW,
                         OUTSOURCE_MAP, sub_sale_id.outsource_line)

        # 写入功能五金工作表
        fmetal_worksheet = workbook.add_sheet(FMETAL_SHEET_NAME)
        self._write_data(fmetal_worksheet, FMETAL_HEADER_ROW, FMETAL_DATA_BEGIN_ROW,
                         FMETAL_MAP, sub_sale_id.function_metal_line)

        # 写入生产部件五金工作表
        production_worksheet = workbook.add_sheet(PRODUCTION_SHEET_NAME)
        self._write_data(production_worksheet, PRODUCTION_HEADER_ROW, PRODUCTION_DATA_BEGIN_ROW,
                         PRODUCTION_MAP, sub_sale_id.production_part_line)

        # 写入连接五金工作表
        cmetal_worksheet = workbook.add_sheet(CMETAL_SHEET_NAME)
        self._write_data(cmetal_worksheet, CMETAL_HEADER_ROW, CMETAL_DATA_BEGIN_ROW,
                         CMETAL_MAP, sub_sale_id.connection_metal_line)

        # save
        buffer = BytesIO()
        workbook.save(buffer)
        return base64.encodebytes(buffer.getvalue())

    @api.multi
    def action_export(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        sub_sale_id = self.env['sub.sale.order'].search([('id', '=', active_id)])
        self.file = self.generate_excel(sub_sale_id)

        value = dict(
            type='ir.actions.act_url',
            target='new',
            url='/web/content?model=%s&id=%s&field=file&download=true&filename=子销售订单_%s.xls' % (self._name, self.id, sub_sale_id.name),
        )
        return value